"""DenziDownloader - local web app to download videos/audio from social media links (via yt-dlp)."""
import json
import os
import shutil
import sys
import threading
import uuid
import webbrowser
from pathlib import Path

import yt_dlp
from flask import Flask, jsonify, request, send_from_directory

APP_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
CONFIG_FILE = Path.home() / ".denzidownloader.json"
DEFAULT_DIR = Path.home() / "Downloads" / "DenziDownloader"

app = Flask(__name__, static_folder=str(APP_DIR / "static"), static_url_path="/static")
jobs = {}
jobs_lock = threading.Lock()


def load_config():
    try:
        return json.loads(CONFIG_FILE.read_text())
    except Exception:
        return {}


def get_download_dir():
    return load_config().get("download_dir") or str(DEFAULT_DIR)


def set_download_dir(path):
    p = Path(path).expanduser()
    p.mkdir(parents=True, exist_ok=True)
    if not os.access(p, os.W_OK):
        raise PermissionError("Folder is not writable")
    cfg = load_config()
    cfg["download_dir"] = str(p.resolve())
    CONFIG_FILE.write_text(json.dumps(cfg))
    return cfg["download_dir"]


def ffmpeg_location():
    if shutil.which("ffmpeg"):
        return None
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def base_opts():
    opts = {"noplaylist": True, "quiet": True, "no_warnings": True}
    loc = ffmpeg_location()
    if loc:
        opts["ffmpeg_location"] = loc
    return opts


def origin_allowed(origin):
    return (
        not origin
        or origin.startswith(("chrome-extension://", "moz-extension://"))
        or origin.startswith(("http://127.0.0.1:", "http://localhost:"))
    )


@app.before_request
def guard_origin():
    # Stop random websites from driving the local API; allow the app itself and the Chrome extension.
    if not origin_allowed(request.headers.get("Origin")):
        return jsonify(error="Forbidden origin"), 403
    if request.method == "OPTIONS":
        return "", 204


@app.after_request
def add_cors(resp):
    origin = request.headers.get("Origin")
    if origin and origin_allowed(origin):
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return resp


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


def has_folder_dialog():
    try:
        import tkinter  # noqa: F401
        return True
    except Exception:
        return False


@app.get("/api/config")
def api_config():
    return jsonify(download_dir=get_download_dir(), desktop=has_folder_dialog())


@app.post("/api/pick-folder")
def api_pick_folder():
    """Native folder dialog; runs in the app process so it works for the window and the extension."""
    try:
        import tkinter
        from tkinter import filedialog
        root = tkinter.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        res = filedialog.askdirectory(initialdir=get_download_dir(), title="Choose download folder", parent=root)
        root.destroy()
    except Exception as e:
        return jsonify(error=f"Folder dialog unavailable: {e}"), 400
    if not res:
        return jsonify(download_dir=get_download_dir())
    try:
        return jsonify(download_dir=set_download_dir(res))
    except Exception as e:
        return jsonify(error=str(e)), 400


@app.post("/api/config")
def api_set_config():
    try:
        return jsonify(download_dir=set_download_dir(request.json.get("download_dir", "")))
    except Exception as e:
        return jsonify(error=str(e)), 400


@app.get("/api/browse")
def api_browse():
    p = Path(request.args.get("path") or get_download_dir()).expanduser()
    while not p.exists() and p != p.parent:
        p = p.parent
    p = p.resolve()
    dirs = []
    try:
        dirs = sorted(
            (d.name for d in p.iterdir() if d.is_dir() and not d.name.startswith(".")),
            key=str.lower,
        )
    except PermissionError:
        pass
    return jsonify(path=str(p), parent=str(p.parent) if p.parent != p else None, dirs=dirs)


@app.post("/api/mkdir")
def api_mkdir():
    data = request.json
    name = os.path.basename(data.get("name", "").strip())
    if not name:
        return jsonify(error="Invalid name"), 400
    try:
        (Path(data["path"]) / name).mkdir(exist_ok=True)
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(error=str(e)), 400


@app.post("/api/info")
def api_info():
    url = (request.json.get("url") or "").strip()
    if not url:
        return jsonify(error="Paste a link first"), 400
    try:
        with yt_dlp.YoutubeDL({**base_opts(), "skip_download": True}) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        return jsonify(error=str(e).replace("ERROR: ", "")), 400
    if info.get("entries"):
        info = next(iter(info["entries"]), info)
    heights = {}
    for f in info.get("formats") or []:
        h = f.get("height")
        if h and f.get("vcodec") not in (None, "none"):
            size = f.get("filesize") or f.get("filesize_approx")
            heights[h] = max(heights.get(h, 0), size or 0)
    return jsonify(
        title=info.get("title"),
        uploader=info.get("uploader") or info.get("channel"),
        duration=info.get("duration"),
        thumbnail=info.get("thumbnail"),
        site=info.get("extractor_key"),
        heights=[{"height": h, "size": s} for h, s in sorted(heights.items(), reverse=True)],
    )


def run_job(job_id, url, mode, height, audio_q, out_dir):
    job = jobs[job_id]

    def hook(d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            job["percent"] = round(d["downloaded_bytes"] / total * 100, 1) if total else 0
            job["speed"] = d.get("_speed_str", "").strip()
            job["eta"] = d.get("_eta_str", "").strip()
            job["status"] = "downloading"
        elif d["status"] == "finished":
            job["status"] = "processing"
            job["percent"] = 100

    opts = {
        **base_opts(),
        "outtmpl": str(Path(out_dir) / "%(title).150B [%(id)s].%(ext)s"),
        "progress_hooks": [hook],
        "restrictfilenames": False,
        "windowsfilenames": True,
    }
    if mode == "audio":
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": str(audio_q)}
        ]
    else:
        cap = f"[height<={height}]" if height else ""
        opts["format"] = f"bestvideo*{cap}+bestaudio/best{cap}/best"
        opts["merge_output_format"] = "mp4"
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
            if mode == "audio":
                path = os.path.splitext(path)[0] + ".mp3"
            elif not os.path.exists(path):
                path = os.path.splitext(path)[0] + ".mp4"
        job.update(status="done", percent=100, file=path)
    except Exception as e:
        job.update(status="error", error=str(e).replace("ERROR: ", ""))


@app.post("/api/download")
def api_download():
    d = request.json
    url = (d.get("url") or "").strip()
    if not url:
        return jsonify(error="Missing url"), 400
    out_dir = d.get("download_dir") or get_download_dir()
    try:
        out_dir = set_download_dir(out_dir)
    except Exception as e:
        return jsonify(error=f"Download folder problem: {e}"), 400
    job_id = uuid.uuid4().hex[:8]
    with jobs_lock:
        jobs[job_id] = {"id": job_id, "title": d.get("title") or url, "status": "starting",
                        "percent": 0, "mode": d.get("mode", "video"), "dir": out_dir}
    height = int(d["height"]) if d.get("height") else None
    threading.Thread(
        target=run_job,
        args=(job_id, url, d.get("mode", "video"), height, d.get("audio_quality", 192), out_dir),
        daemon=True,
    ).start()
    return jsonify(id=job_id)


@app.get("/api/jobs")
def api_jobs():
    return jsonify(list(jobs.values())[::-1])


def port_in_use(port):
    import socket
    with socket.socket() as sk:
        sk.settimeout(0.5)
        return sk.connect_ex(("127.0.0.1", port)) == 0


def open_window(url, wait_forever=True):
    try:
        if os.environ.get("NO_DESKTOP"):
            raise ImportError
        import webview
        webview.create_window("DenziDownloader", url, width=860, height=780)
        webview.start()
    except Exception:  # no webview available: fall back to the browser
        webbrowser.open(url)
        if wait_forever:
            threading.Event().wait()


def start_tray(detached):
    """Tray icon with Open/Quit. Returns True if it started. detached=True runs it on its own thread."""
    try:
        import subprocess
        import pystray
        from PIL import Image

        def open_app(icon=None, item=None):
            cmd = [sys.executable] if getattr(sys, "frozen", False) else [sys.executable, str(Path(__file__))]
            subprocess.Popen(cmd)

        def quit_app(icon, item):
            icon.stop()
            os._exit(0)

        image = Image.open(APP_DIR / "static" / "icon.png")
        menu = pystray.Menu(
            pystray.MenuItem("Open DenziDownloader", open_app, default=True),
            pystray.MenuItem("Quit", quit_app),
        )
        icon = pystray.Icon("DenziDownloader", image, "DenziDownloader", menu)
        if detached:
            icon.run_detached()
        else:
            icon.run()
        return True
    except Exception:
        return False


def main():
    port = int(os.environ.get("PORT", 8765))
    url = f"http://127.0.0.1:{port}"
    background = "--background" in sys.argv
    if port_in_use(port):
        # Already running (e.g. started with Windows): just show the window for it.
        if not background:
            open_window(url)
        return
    threading.Thread(
        target=lambda: app.run(host="127.0.0.1", port=port, threaded=True), daemon=True
    ).start()
    if background:
        if not start_tray(detached=False):
            threading.Event().wait()
    else:
        # Keep running in the tray after the window is closed (so the browser extension keeps working).
        has_tray = start_tray(detached=True)
        open_window(url, wait_forever=has_tray)
        if has_tray:
            threading.Event().wait()


if __name__ == "__main__":
    main()

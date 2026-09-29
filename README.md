# DenziDownloader

Paste a link (YouTube, X/Twitter, Instagram, TikTok, Facebook, Reddit, Vimeo… anything [yt-dlp supports](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)), pick the quality, and download as video (MP4) or MP3.

## Windows app (no Python needed)
Download `DenziDownloader.exe` from the latest run of the **Build Windows app** GitHub Action (Actions tab > latest run > Artifacts), or build it yourself with `build_windows.bat`. Double-click to open; it runs in its own window with a native folder picker.

## Run from source
```
pip install -r requirements.txt
python app.py
```
Opens http://127.0.0.1:8765. ffmpeg is bundled through `imageio-ffmpeg` (or uses your system ffmpeg).

- After pasting, the app analyzes the link and lists available qualities.
- Toggle **MP3** for audio-only (128/192/320 kbps).
- **Save to → Change…** picks the folder before downloading; the choice is remembered (`~/.denzidownloader.json`) and can be changed any time.
- Private/age-restricted content may need login cookies; keep yt-dlp updated (`pip install -U yt-dlp`) since sites change often.

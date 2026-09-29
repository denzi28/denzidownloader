# DenziDownloader

Paste a link (YouTube, X/Twitter, Instagram, TikTok, Facebook, Reddit, Vimeo… anything [yt-dlp supports](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)), pick the quality, and download as video (MP4) or MP3.

## Windows installer (for sharing)
Every push builds `DenziDownloader-Setup.exe` and publishes it on the repo's **Releases** page. Send that file (or link) to friends: they double-click it, click Next, and get a Start-menu/desktop shortcut and an uninstaller. No Python or admin rights needed. You can also build locally: `build_windows.bat`, then compile `installer.iss` with Inno Setup.

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

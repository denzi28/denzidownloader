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

## Chrome extension
The `extension/` folder is a Chrome (Manifest V3) extension that talks to the desktop app, so **the app must be running**. Click the toolbar icon on any video page: the link is filled in and analyzed automatically, then pick Video/MP3, quality and folder.

Install: unzip `DenziDownloader-Chrome-Extension.zip` (on the Releases page), open `chrome://extensions`, turn on **Developer mode**, click **Load unpacked** and select the unzipped folder. (Publishing on the Chrome Web Store needs a one-time $5 developer account.)

## Start with Windows
The installer has an option (on by default) to start DenziDownloader in the background at login, with a tray icon (Open / Quit). This keeps the browser extension working without opening the app. Launching the app normally then just opens a window for the already-running background instance.

@echo off
py -m pip install -r requirements.txt pyinstaller || exit /b 1
py -m PyInstaller --noconfirm --onefile --windowed --name DenziDownloader ^
  --add-data "static;static" --collect-all yt_dlp --collect-all imageio_ffmpeg --hidden-import pystray._win32 app.py
echo.
echo Done: dist\DenziDownloader.exe

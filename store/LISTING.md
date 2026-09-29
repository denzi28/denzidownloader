# Chrome Web Store listing (copy/paste)

**Name:** DenziDownloader
**Category:** Productivity
**Language:** English

**Summary (max 132 chars):**
Send the video or MP3 of the page you're on to the DenziDownloader desktop app, with quality and folder choice.

**Description:**
DenziDownloader is a companion extension for the DenziDownloader desktop app (Windows). Click the toolbar icon on a page and the link is sent to the app running on your own computer, which analyzes it and lists the available qualities. Choose Video (MP4) or MP3, pick the quality and the folder to save to, and download. Progress is shown in the popup.

Requires the free DenziDownloader desktop app to be installed and running. Only download content you have the right to save.

**Single purpose:**
Send the current page's link to the locally running DenziDownloader app and show its download options and progress.

**Permission justifications:**
- `activeTab` / `tabs`: read the URL of the current tab to pre-fill the link in the popup.
- Host permission `http://127.0.0.1:8765/*`: communicate with the DenziDownloader desktop app on the user's own computer.

**Remote code:** No. **Data collection:** None. The extension collects, stores and transmits no user data; the page URL is sent only to the app on localhost (127.0.0.1).

**Privacy policy URL:** link to `PRIVACY.md` in this repo (needs a public repo), or paste its text on any public page.

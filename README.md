# NEXUS Launcher

A free, open-source app launcher for Windows that loads app data automatically from GitHub.

![Version](https://img.shields.io/badge/version-3.0.0-purple)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## What is NEXUS Launcher?

NEXUS Launcher is a Windows desktop application that displays a collection of apps with descriptions, images and download links. The app data is loaded automatically from a GitHub JSON file — so users always see the latest version without needing to update the launcher itself.

## Features

- 🎮 Clean modern UI with sidebar navigation
- 🔄 Automatic updates via GitHub JSON
- 🖼 Images stored directly in JSON (no external links needed)
- 🔍 Search functionality
- 📋 Detail view for each app
- 🛡 Password-protected admin panel
- ✅ Status indicator (Connected / Offline)

## Download

Download the latest release here:
👉 [Releases](https://github.com/FNAF232619/NexusLauncher/releases/latest)

## Build it yourself

If you don't trust the pre-built `.exe`, you can build it yourself:

### Requirements
- Python 3.12
- See `requirements.txt`

### Steps

1. Clone this repository:
```
git clone https://github.com/FNAF232619/NexusLauncher.git
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Run directly with Python:
```
python launcher.py
```

4. Or build the `.exe` yourself:
```
pyinstaller --onefile --windowed --icon=icon.ico --name "NexusLauncher" launcher.py
```

## How it works

- The launcher fetches app data from a GitHub-hosted `data.json` file on startup
- All app images are stored as Base64 directly in the JSON — no external image hosting needed
- Admin panel (password protected) allows adding/editing apps and exporting the updated JSON to upload to GitHub

## Data Source

App data is loaded from:
```
https://raw.githubusercontent.com/FNAF232619/Nexus-Launcher-json/refs/heads/main/data.json
```

## Built With

- [Python 3.12](https://python.org)
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- [Pillow](https://python-pillow.org)
- [PyInstaller](https://pyinstaller.org)

## License

MIT License — free to use, modify and distribute.

## Disclaimer

This launcher only provides download links to third-party apps. The launcher itself is not responsible for the content of linked applications. Use at your own risk.

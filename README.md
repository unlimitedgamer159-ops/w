# Stremini Workspace (Native PyQt6)

This repository was replaced with a native desktop architecture for all agents.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Build Windows .exe

Run this on Windows:

```bash
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --onefile --windowed --name stremini main.py
```

The executable will be generated in `dist/stremini.exe`.

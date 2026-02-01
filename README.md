# AppMinimiser
AppMinimiser
App Auto-Minimiser

A lightweight Windows utility that automatically minimises and hides selected applications after launch — perfect for keeping launchers, updaters, and background apps out of your taskbar while they load or run.

Runs quietly in the system tray and is fully configurable via a simple GUI.

✨ Features

🕒 Delay-based actions (wait X seconds after a window appears)

🪟 Match apps by window title

🙈 Minimise and hide windows (removed from taskbar, process stays alive)

🔁 Safe for apps that are still loading (no force-closing)

🧠 Automatically handles window restores / reopens

📌 Runs in the system tray

💾 Settings saved to settings.json

🧩 Portable single-EXE build supported

🧠 How it works

The app watches for newly opened application windows

When a window matches a configured rule:

waits the specified delay

minimises it

hides it from the taskbar

The application continues running normally in the background

If the app creates its own tray icon, it will appear as usual

⚠️ No applications are force-closed. This avoids crashes and broken launchers.

🖥️ Requirements

Windows 10 / 11

Python 3.9+ (if running from source)

Python dependencies:

pywin32

pystray

Pillow

🚀 Running from source
pip install pywin32 pystray pillow
python app_auto_minimiser.py

📦 Building a standalone EXE

This app is designed to be packaged with PyInstaller.

Install PyInstaller
pip install pyinstaller

Build command
pyinstaller --onefile --noconsole app_auto_minimiser.py


Optional (recommended for reliability):

pyinstaller --onefile --noconsole ^
  --hidden-import=win32gui ^
  --hidden-import=win32con ^
  --hidden-import=PIL ^
  app_auto_minimiser.py


The EXE will be created in:

dist/app_auto_minimiser.exe

⚙️ Configuration

Settings are stored in:

settings.json


Example:

{
  "enabled": true,
  "delay_seconds": 1.5,
  "tracked_apps": {
    "steam": "minimise and hide",
    "epic games launcher": "minimise and hide"
  }
}


Window title matching is not case-insensitive

Titles must match exactly (not partial substrings)

🧭 Usage

Launch the app → it starts hidden in the tray

Double-click the tray icon or choose Open Settings

Add apps by window title

Choose an action (minimise or minimise and hide)

Set a global delay

Close the window — the app stays active in the tray

🧪 Recommended use cases

Game launchers (Steam, Epic, Battle.net)

Updaters and background tools

RGB / peripheral software

Cloud sync utilities

Apps that don’t need to live in the taskbar

⚠️ Limitations

Windows does not allow one app to force another app into the system tray

Hidden windows can only be restored by:

the app’s own tray icon

reopening the app

Console / child windows are ignored by design

🛠️ Future ideas

Restore hidden apps from the GUI

Per-app delays

Partial title matching

Auto-restore after X minutes

Startup with Windows

📄 License

MIT License — feel free to use, modify, and distribute.

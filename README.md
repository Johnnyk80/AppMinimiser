# App Auto-Minimiser (Windows)

A lightweight Windows utility that automatically **minimises or hides applications**
after they appear, based on their window title.  
Runs quietly in the **system tray** and works in the background.

Perfect for launchers, pop-ups, splash screens, or apps you don’t want stealing focus.

---

## ✨ Features

- Automatically minimise or **minimise + hide from taskbar**
- Match apps by **window title text** (case-insensitive)
- Adjustable delay before action triggers
- Runs silently in the **system tray**
- Simple GUI to manage rules
- Settings saved locally (`settings.json`)
- No installer required

---

## 🖥️ Requirements

- Windows 10 or Windows 11  
*(This app is Windows-only)*

---

## ⬇️ Installation (Recommended)

### Download the EXE
1. Go to the **Releases** page
2. Download the latest `AppAutoMinimiser.exe`
3. Run the file

> ⚠️ Windows SmartScreen may warn about an unknown publisher.  
> Click **More info → Run anyway**.

No installation, no admin rights required.

---

## 🚀 How to Use

1. Launch **App Auto-Minimiser**
2. Click **Add App**
3. Enter part (or all) of the window title  
   - Matching is **case-insensitive**
4. Choose an action:
   - **Minimise**
   - **Minimise and Hide**
5. Set an optional delay (seconds)
6. Hide the app to the tray — it will keep running

The app will now watch for matching windows and apply the chosen action automatically.

---

## 🧠 How Window Matching Works

- Matching is **case-insensitive**
- The window title must **match exactly**
- Partial matches are **not** supported

### Example

| Rule | Window Title | Result |
|----|----|----|
| `rockstar games launcher` | `Rockstar Games Launcher` | ✅ Match |
| `rockstar` | `Rockstar Games Launcher` | ❌ No match |
---

## ⚙️ Tray Controls

Right-click the tray icon to:
- Open Settings
- Enable / Disable the watcher
- Exit the application

Double-click the tray icon to reopen the settings window.

---

## 🛠️ Advanced: Run from Source

Only needed if you want to modify the app.

### Requirements
- Python 3.10+
- Windows

### Run
```bash
pip install -r requirements.txt
python app_auto_minimiser.py

📦 Building the EXE Yourself

pyinstaller --onefile --windowed app_auto_minimiser.py

The EXE will be created in the dist folder.
🧾 Settings File

Settings are saved automatically to:

settings.json

Located in the same folder as the EXE.
⚠️ Known Limitations

    Windows-only

    Some system or elevated apps may not respond to minimise commands

    Tray icons for third-party apps depend on how that app implements tray support

📜 License

MIT License — free to use, modify, and distribute.
💡 Why This Exists

Some apps insist on popping up, stealing focus, or sitting in your taskbar.
This tool politely tells them to sit down and be quiet.

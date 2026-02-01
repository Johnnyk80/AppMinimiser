import time
import threading
import sys
import os
import json
import tkinter as tk
from tkinter import ttk
import win32gui
import win32con
import pystray
from PIL import Image, ImageDraw

shutdown_event = threading.Event()
timers = []

# ================= PATHS =================

APP_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")

# ================= SETTINGS =================

settings = {
    "enabled": True,
    "delay_seconds": 1.5,
    "tracked_apps": {}
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings.update(json.load(f))
        except:
            pass
    else:
        save_settings()

def save_settings():
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)

load_settings()

enabled = settings["enabled"]
delay_seconds = settings["delay_seconds"]
tracked_apps = settings["tracked_apps"]

# ---- migrate old "close" action to new label ----
for app, action in list(tracked_apps.items()):
    if action == "close":
        tracked_apps[app] = "minimise and hide"
save_settings()

# ================= STATE =================

CHECK_INTERVAL = 0.4

window_visibility = {}
window_iconic = {}
window_first_seen = {}
handled_hwnds = set()
gui_root = None

# ================= WINDOW HELPERS =================

def is_real_app_window(hwnd):
    if not win32gui.IsWindow(hwnd):
        return False
    if win32gui.GetParent(hwnd):
        return False
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    if style & win32con.WS_CHILD:
        return False
    return bool(win32gui.GetWindowText(hwnd).strip())

def enum_app_windows():
    windows = []
    def callback(hwnd, _):
        if is_real_app_window(hwnd):
            windows.append((
                hwnd,
                win32gui.GetWindowText(hwnd).lower(),
                win32gui.IsWindowVisible(hwnd),
                win32gui.IsIconic(hwnd)
            ))
    win32gui.EnumWindows(callback, None)
    return windows

def minimise_and_hide(hwnd):
    if win32gui.IsWindow(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)

# ================= WATCHER =================

def watcher():
    while True:
        if enabled:
            now = time.time()
            current_hwnds = set()

            for hwnd, title, visible, iconic in enum_app_windows():
                current_hwnds.add(hwnd)

                was_visible = window_visibility.get(hwnd, False)
                was_iconic = window_iconic.get(hwnd, False)

                window_visibility[hwnd] = visible
                window_iconic[hwnd] = iconic

                # Treat restore-from-minimise as a new appearance
                if (visible and not was_visible) or (was_iconic and not iconic):
                    window_first_seen[hwnd] = now
                    handled_hwnds.discard(hwnd)

                if not visible or hwnd in handled_hwnds:
                    continue

                first_seen = window_first_seen.get(hwnd)
                if first_seen is None or (now - first_seen) < delay_seconds:
                    continue

                for app, action in tracked_apps.items():
                    if app == title.lower():
                        handled_hwnds.add(hwnd)

                        # minimise, minimise and hide, and legacy close all do the same
                        if action in ("minimise", "minimise and hide", "close"):
                            minimise_and_hide(hwnd)

                        break

            # Cleanup destroyed windows
            for hwnd in list(window_visibility):
                if hwnd not in current_hwnds:
                    window_visibility.pop(hwnd, None)
                    window_iconic.pop(hwnd, None)
                    window_first_seen.pop(hwnd, None)
                    handled_hwnds.discard(hwnd)

        time.sleep(CHECK_INTERVAL)

# ================= GUI =================

def center_over_parent(parent, child):
    parent.update_idletasks()
    child.update_idletasks()
    x = parent.winfo_x() + parent.winfo_width() // 2 - child.winfo_width() // 2
    y = parent.winfo_y() + parent.winfo_height() // 2 - child.winfo_height() // 2
    child.geometry(f"+{x}+{y}")

def launch_gui():
    global gui_root, enabled, delay_seconds

    root = tk.Tk()
    root.title("App Auto-Minimiser")
    root.geometry("420x420")
    root.resizable(False, False)
    root.withdraw()
    gui_root = root

    root.protocol("WM_DELETE_WINDOW", root.withdraw)
    root.bind("<Unmap>", lambda e: root.withdraw() if root.state() == "iconic" else None)

    tree = ttk.Treeview(root, columns=("App", "Action"), show="headings")
    tree.heading("App", text="Window title contains")
    tree.heading("Action", text="Action")
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh():
        tree.delete(*tree.get_children())
        for app, action in tracked_apps.items():
            tree.insert("", tk.END, values=(app, action))
        save_settings()

    def show():
        root.deiconify()
        root.lift()
        root.focus_force()

    def add_app():
        dialog = tk.Toplevel(root)
        dialog.title("Add App")
        dialog.geometry("360x200")
        dialog.transient(root)
        dialog.grab_set()

        tk.Label(dialog, text="Window title contains:").pack(pady=(15, 5))
        entry = tk.Entry(dialog)
        entry.pack(fill="x", padx=20)
        entry.focus_force()

        tk.Label(dialog, text="Action:").pack(pady=(10, 5))
        action = tk.StringVar(value="minimise")
        ttk.Combobox(
            dialog,
            textvariable=action,
            values=["minimise", "minimise and hide"],
            state="readonly"
        ).pack(padx=20)

        def confirm():
            name = entry.get().strip().lower()
            if name:
                tracked_apps[name] = action.get()
                refresh()
            dialog.destroy()

        ttk.Button(dialog, text="Add", command=confirm).pack(pady=15)
        center_over_parent(root, dialog)

    def remove_app():
        sel = tree.selection()
        if sel:
            app = tree.item(sel[0])["values"][0]
            tracked_apps.pop(app, None)
            refresh()

    def set_delay():
        dialog = tk.Toplevel(root)
        dialog.title("Set Delay")
        dialog.geometry("300x160")
        dialog.transient(root)
        dialog.grab_set()

        tk.Label(dialog, text="Seconds before action:").pack(pady=15)
        entry = tk.Entry(dialog)
        entry.insert(0, str(delay_seconds))
        entry.pack(fill="x", padx=20)
        entry.focus_force()

        def confirm():
            global delay_seconds
            try:
                delay_seconds = float(entry.get())
                settings["delay_seconds"] = delay_seconds
                save_settings()
            except:
                pass
            dialog.destroy()

        ttk.Button(dialog, text="OK", command=confirm).pack(pady=15)
        center_over_parent(root, dialog)

    ttk.Button(root, text="Add App", command=add_app).pack(fill="x", padx=10)
    ttk.Button(root, text="Remove Selected", command=remove_app).pack(fill="x", padx=10, pady=5)
    ttk.Button(root, text="Set Delay", command=set_delay).pack(fill="x", padx=10)
    ttk.Button(root, text="Hide to Tray", command=root.withdraw).pack(fill="x", padx=10, pady=10)

    launch_gui.show = show
    refresh()
    root.mainloop()

# ================= TRAY =================

def tray_image():
    img = Image.new("RGB", (64, 64), (30, 30, 30))
    d = ImageDraw.Draw(img)
    d.rectangle((18, 18, 46, 46), fill=(0, 180, 255))
    return img

def tray_open(icon, item=None):
    if gui_root:
        gui_root.after(0, launch_gui.show)

def tray_toggle(icon, item):
    global enabled
    enabled = not enabled
    settings["enabled"] = enabled
    save_settings()
    icon.update_menu()

def tray_quit(icon, item):
    shutdown_event.set()
    for t in timers:
        t.cancel()
    timers.clear()
    if gui_root:
        gui_root.after(0, gui_root.destroy)
    save_settings()
    icon.stop()
    sys.exit(0)

def tray_thread():
    icon = pystray.Icon(
        "AppMinimiser",
        tray_image(),
        "App Auto-Minimiser",
        menu=pystray.Menu(
            pystray.MenuItem(
                "Open Settings",
                tray_open,
                default=True
            ),
            pystray.MenuItem(
                "Enabled",
                tray_toggle,
                checked=lambda _: enabled
            ),
            pystray.MenuItem(
                "Exit",
                tray_quit
            )
        )
    )
    icon.run()

# ================= MAIN =================

if __name__ == "__main__":
    threading.Thread(target=watcher, daemon=True).start()
    threading.Thread(target=tray_thread, daemon=True).start()
    launch_gui()

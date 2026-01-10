import os
import sys
import requests
import time
import threading
import tempfile
import random
import traceback
import tkinter as tk
import customtkinter as ctk
import ctypes
import math
from PIL import Image, ImageTk

# ==============================================================================
# SYSTEM ENGINE
# ==============================================================================
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("audio.organizer.v2.7")
except: pass

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

GITHUB_USER = "tgriebell"
REPO_NAME = "audio-organizer-server"
SCRIPT_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/organizar_musicas.py"
TEMP_DIR = os.path.join(tempfile.gettempdir(), "AudioOrganizer_Elite")
if not os.path.exists(TEMP_DIR): os.makedirs(TEMP_DIR)
LOCAL_CORE = os.path.join(TEMP_DIR, "core_v2_7.py")

COLOR_BG = "#000000"
COLOR_ACCENT = "#00ff66"

class EliteSplash(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.configure(fg_color=COLOR_BG)
        
        # Centralização Estrita
        w, h = 600, 450
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f'{w}x{h}+{int((sw-w)/2)}+{int((sh-h)/2)}')

        # Hack Taskbar
        self.after(100, self.apply_hack)

        self.main = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0, border_width=1, border_color="#111")
        self.main.pack(fill="both", expand=True)

        # --- WAVEFORM (Centro Absoluto Matemático) ---
        # Canvas de 600px, centro é 300px
        self.canvas = tk.Canvas(self.main, height=160, bg=COLOR_BG, highlightthickness=0)
        self.canvas.place(x=0, y=40, width=600)
        
        self.bars = []
        num_bars, bar_w, gap = 24, 6, 4
        total_w = (num_bars * bar_w) + ((num_bars - 1) * gap)
        start_x = (600 - total_w) / 2 # Início exato para o centro ser 300
        
        for i in range(num_bars):
            x0 = start_x + i * (bar_w + gap)
            rect = self.canvas.create_rectangle(x0, 80, x0 + bar_w, 80, fill=COLOR_ACCENT, outline="")
            self.bars.append(rect)

        # --- LOGO & STATUS (Centralizados) ---
        self.lbl_title = ctk.CTkLabel(self.main, text="AUDIO ORGANIZER", font=("Inter Black", 36), text_color="white")
        self.lbl_title.place(relx=0.5, rely=0.62, anchor="center")
        
        self.lbl_sub = ctk.CTkLabel(self.main, text="PROFESSIONAL AI CORE v2.7", font=("Consolas", 10, "bold"), text_color="#444")
        self.lbl_sub.place(relx=0.5, rely=0.70, anchor="center")

        self.lbl_status = ctk.CTkLabel(self.main, text="SYNCHRONIZING...", font=("Consolas", 9), text_color=COLOR_ACCENT)
        self.lbl_status.place(relx=0.5, rely=0.82, anchor="center")

        self.progress = ctk.CTkProgressBar(self.main, width=300, height=2, progress_color=COLOR_ACCENT, fg_color="#0a0a0a")
        self.progress.place(relx=0.5, rely=0.90, anchor="center")
        self.progress.set(0)

        self.animating = True
        self.phase = 0
        self.animate()
        self.after(500, self.start_bootstrap)

    def apply_hack(self):
        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            style = style & ~0x00000080 | 0x00040000
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)
            self.withdraw(); self.after(10, self.deiconify)
        except: pass

    def animate(self):
        if not self.animating: return
        self.phase += 0.2
        for i, rect in enumerate(self.bars):
            dist = abs(i - len(self.bars)/2) / (len(self.bars)/2)
            att = math.cos(dist * math.pi / 2)
            h = (math.sin(self.phase + i * 0.4) * 50 + 60) * att
            x0, _, x1, _ = self.canvas.coords(rect)
            self.canvas.coords(rect, x0, 80 - h/2, x1, 80 + h/2)
        self.after(50, self.animate)

    def start_bootstrap(self):
        threading.Thread(target=self.logic, daemon=True).start()

    def logic(self):
        try:
            self.progress.set(0.4)
            r = requests.get(SCRIPT_URL, timeout=10)
            if r.status_code == 200:
                with open(LOCAL_CORE, "wb") as f: f.write(r.content)
            self.progress.set(1.0)
            time.sleep(0.8)
            self.animating = False
            self.quit()
        except: self.quit()

def main():
    app = EliteSplash()
    app.mainloop()
    app.destroy()

    if os.path.exists(LOCAL_CORE):
        with open(LOCAL_CORE, "r", encoding="utf-8") as f:
            code = f.read()
        import mutagen, pygame, PIL, requests
        scope = {
            '__name__': '__main__', 'ctk': ctk, 'ctypes': ctypes, 'os': os, 'sys': sys,
            'mutagen': mutagen, 'pygame': pygame, 'PIL': PIL, 'requests': requests, 'math': math
        }
        exec(code, scope)

if __name__ == "__main__":
    main()
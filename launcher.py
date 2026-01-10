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
# ENGINE DE SISTEMA (WIN32 TASKBAR HACK)
# ==============================================================================
try:
    myappid = 'tgriebell.audioorganizer.neural.v2.9'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except: pass

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# CONFIGURAÇÕES GITHUB
GITHUB_USER = "tgriebell"
REPO_NAME = "audio-organizer-server"
BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main"
VERSION_URL = f"{BASE_URL}/version.txt"
SCRIPT_URL = f"{BASE_URL}/organizar_musicas.py"

TEMP_DIR = os.path.join(tempfile.gettempdir(), "AudioOrganizer_Neural_Cache")
if not os.path.exists(TEMP_DIR): os.makedirs(TEMP_DIR)
LOCAL_CORE = os.path.join(TEMP_DIR, "core_v2_9.py")
LOCAL_VERSION = os.path.join(TEMP_DIR, "version.txt")

COLOR_BG = "#0a0a0a"
COLOR_ACCENT = "#00ff66"

class NeuralSplash(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.configure(fg_color=COLOR_BG)
        
        # Centralização Estrita (Center Screen)
        w, h = 600, 450
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f'{w}x{h}+{int((sw-w)/2)}+{int((sh-h)/2)}')

        # Hack Barra de Tarefas
        self.after(100, self.apply_hack)

        self.main_frame = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0, border_width=1, border_color="#1a1a1a")
        self.main_frame.pack(fill="both", expand=True)

        # --- WAVEFORM (CENTRALIZAÇÃO ABSOLUTA MATEMÁTICA) ---
        self.canvas_w = 600
        self.canvas = tk.Canvas(self.main_frame, height=160, bg=COLOR_BG, highlightthickness=0)
        self.canvas.place(x=0, y=40, width=600)
        
        self.bars = []
        num_bars, bar_w, gap = 26, 6, 4
        total_w = (num_bars * bar_w) + ((num_bars - 1) * gap)
        # O start_x deve ser exatamente metade da largura total do canvas menos metade do componente
        start_x = (600 - total_w) / 2 
        
        for i in range(num_bars):
            x0 = start_x + i * (bar_w + gap)
            rect = self.canvas.create_rectangle(x0, 80, x0 + bar_w, 80, fill=COLOR_ACCENT, outline="")
            self.bars.append(rect)

        # --- LOGO & STATUS ---
        self.lbl_title = ctk.CTkLabel(self.main_frame, text="AUDIO ORGANIZER", font=("Segoe UI", 36, "bold"), text_color="white")
        self.lbl_title.place(relx=0.5, rely=0.62, anchor="center")
        
        self.lbl_sub = ctk.CTkLabel(self.main_frame, text="NEURAL ENGINE EDITION v2.9", font=("Consolas", 10, "bold"), text_color=COLOR_ACCENT)
        self.lbl_sub.place(relx=0.5, rely=0.70, anchor="center")

        self.lbl_status = ctk.CTkLabel(self.main_frame, text="LOADING NEURAL ALGORITHMS...", font=("Consolas", 9), text_color="#444")
        self.lbl_status.place(relx=0.5, rely=0.82, anchor="center")

        self.progress = ctk.CTkProgressBar(self.main_frame, width=350, height=2, progress_color=COLOR_ACCENT, fg_color="#111")
        self.progress.place(relx=0.5, rely=0.90, anchor="center")
        self.progress.set(0)

        self.animating = True
        self.phase = 0
        self.animate_waves()
        self.after(500, self.start_bootstrap)

    def apply_hack(self):
        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            style = style & ~0x00000080 | 0x00040000
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)
            self.withdraw(); self.after(10, self.deiconify)
        except: pass

    def animate_waves(self):
        if not self.animating: return
        self.phase += 0.2
        for i, rect in enumerate(self.bars):
            dist = abs(i - len(self.bars)/2) / (len(self.bars)/2)
            att = math.cos(dist * math.pi / 2)
            h = (math.sin(self.phase + i * 0.4) * 50 + 60) * att
            x0, _, x1, _ = self.canvas.coords(rect)
            self.canvas.coords(rect, x0, 80 - h/2, x1, 80 + h/2)
        self.after(50, self.animate_waves)

    def start_bootstrap(self):
        threading.Thread(target=self.run_update, daemon=True).start()

    def run_update(self):
        try:
            # 1. Checar versão
            remote = requests.get(VERSION_URL, timeout=5).text.strip()
            local = "0.0"
            if os.path.exists(LOCAL_VERSION):
                with open(LOCAL_VERSION, "r") as f: local = f.read().strip()
            
            # 2. Baixar se necessário
            if remote != local or not os.path.exists(LOCAL_CORE):
                self.lbl_status.configure(text=f"DOWNLOADING CORE v{remote}...")
                r = requests.get(SCRIPT_URL, timeout=15)
                if r.status_code == 200:
                    with open(LOCAL_CORE, "wb") as f: f.write(r.content)
                    with open(LOCAL_VERSION, "w") as f: f.write(remote)
            
            self.progress.set(1.0)
            self.lbl_status.configure(text="SYSTEM READY")
            time.sleep(0.8)
            self.animating = False
            self.quit()
        except:
            self.quit()

def main():
    app = NeuralSplash()
    app.mainloop()
    app.destroy()

    if os.path.exists(LOCAL_CORE):
        with open(LOCAL_CORE, "r", encoding="utf-8") as f: code = f.read()
        import mutagen, pygame, PIL, requests
        scope = {
            '__name__': '__main__', 'ctk': ctk, 'ctypes': ctypes, 'os': os, 'sys': sys,
            'mutagen': mutagen, 'pygame': pygame, 'PIL': PIL, 'requests': requests, 'math': math
        }
        exec(code, scope)

if __name__ == "__main__":
    main()
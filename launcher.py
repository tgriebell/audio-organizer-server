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

COLOR_BG = "#050505"
COLOR_ACCENT = "#00ff66"
COLOR_STATUS = "#aaaaaa"

class NeuralSplash(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.configure(fg_color=COLOR_BG)
        
        # Centralização Estrita
        w, h = 600, 480
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f'{w}x{h}+{int((sw-w)/2)}+{int((sh-h)/2)}')

        # Hack Barra de Tarefas
        self.after(100, self.apply_hack)

        self.main_frame = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0, border_width=1, border_color="#1a1a1a")
        self.main_frame.pack(fill="both", expand=True)

        # --- BACKGROUND GRADIENT SIMULATION ---
        self.bg_canvas = tk.Canvas(self.main_frame, width=600, height=480, bg=COLOR_BG, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0)
        self.draw_radial_gradient()

        # --- WAVEFORM (NEON GLOW) ---
        self.canvas = tk.Canvas(self.main_frame, height=140, bg=COLOR_BG, highlightthickness=0)
        self.canvas.place(x=0, y=50, width=600)
        
        self.bars = []
        self.glows = []
        num_bars, bar_w, gap = 28, 4, 6
        total_w = (num_bars * bar_w) + ((num_bars - 1) * gap)
        start_x = (600 - total_w) / 2 
        
        for i in range(num_bars):
            x0 = start_x + i * (bar_w + gap)
            # Glow effect (simulado com retângulos maiores e menor opacidade - Tkinter hack)
            glow = self.canvas.create_rectangle(x0-2, 70, x0 + bar_w+2, 70, fill="#00441a", outline="")
            rect = self.canvas.create_rectangle(x0, 70, x0 + bar_w, 70, fill=COLOR_ACCENT, outline="")
            self.bars.append(rect)
            self.glows.append(glow)

        # --- TITULO PREMIUM ---
        self.title_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.title_container.place(relx=0.5, rely=0.58, anchor="center")

        self.lbl_audio = ctk.CTkLabel(self.title_container, text="AUDIO", font=("Segoe UI Light", 42), text_color="white")
        self.lbl_audio.pack(side="left")
        
        self.lbl_organizer = ctk.CTkLabel(self.title_container, text=" ORGANIZER", font=("Segoe UI", 42, "bold"), text_color="white")
        self.lbl_organizer.pack(side="left")

        self.lbl_author = ctk.CTkLabel(self.main_frame, text="by Thiago Griebel • TODOS OS DIREITOS RESERVADOS", font=("Segoe UI", 8, "bold"), text_color="#444", letter_spacing=1)
        self.lbl_author.place(relx=0.5, rely=0.66, anchor="center")
        
        self.lbl_sub = ctk.CTkLabel(self.main_frame, text="NEURAL ENGINE EDITION v2.9", font=("Consolas", 10, "bold"), text_color=COLOR_ACCENT)
        self.lbl_sub.place(relx=0.5, rely=0.73, anchor="center")
        # Add glow to sub
        self.lbl_sub.configure(font=("Consolas", 10, "bold")) 

        self.lbl_status = ctk.CTkLabel(self.main_frame, text="LOADING NEURAL ALGORITHMS...", font=("Consolas", 9), text_color=COLOR_STATUS)
        self.lbl_status.place(relx=0.5, rely=0.84, anchor="center")

        # --- PROGRESS BAR CUSTOM (LASER TIP) ---
        self.prog_canvas = tk.Canvas(self.main_frame, width=400, height=10, bg=COLOR_BG, highlightthickness=0)
        self.prog_canvas.place(relx=0.5, rely=0.92, anchor="center")
        self.prog_bg = self.prog_canvas.create_rectangle(0, 4, 400, 7, fill="#1a1a1a", outline="")
        self.prog_fill = self.prog_canvas.create_rectangle(0, 4, 0, 7, fill=COLOR_ACCENT, outline="")
        self.prog_glow = self.prog_canvas.create_oval(-5, 0, 5, 10, fill="white", outline="")

        self.animating = True
        self.phase = 0
        self.pulse_val = 0
        self.pulse_dir = 1
        self.progress_val = 0
        
        self.animate_elements()
        self.after(500, self.start_bootstrap)

    def draw_radial_gradient(self):
        # Simula gradiente radial com círculos
        for i in range(100):
            r = 600 - (i * 4)
            if r < 0: break
            color = f"#{max(5, 12-i//8):02x}{max(5, 12-i//8):02x}{max(5, 12-i//8):02x}"
            self.bg_canvas.create_oval(300-r, 240-r, 300+r, 240+r, fill=color, outline="")

    def apply_hack(self):
        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            style = style & ~0x00000080 | 0x00040000
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)
            self.withdraw(); self.after(10, self.deiconify)
        except: pass

    def animate_elements(self):
        if not self.animating: return
        self.phase += 0.15
        
        # 1. Waveform Animation
        for i, rect in enumerate(self.bars):
            dist = abs(i - len(self.bars)/2) / (len(self.bars)/2)
            att = math.cos(dist * math.pi / 2)
            h = (math.sin(self.phase + i * 0.3) * 40 + 50) * att
            x0, _, x1, _ = self.canvas.coords(rect)
            self.canvas.coords(rect, x0, 70 - h/2, x1, 70 + h/2)
            self.canvas.coords(self.glows[i], x0-2, 70 - h/2 - 2, x1+2, 70 + h/2 + 2)

        # 2. Pulse Status
        self.pulse_val += 0.04 * self.pulse_dir
        if self.pulse_val >= 1.0: self.pulse_dir = -1
        if self.pulse_val <= 0.4: self.pulse_dir = 1
        
        alpha_hex = hex(int(self.pulse_val * 255))[2:].zfill(2)
        # ctk labels don't support hex alpha well in all modes, so we simulate with color transition
        gray_val = int(170 * self.pulse_val)
        self.lbl_status.configure(text_color=f"#{gray_val:02x}{gray_val:02x}{gray_val:02x}")

        # 3. Update Progress Smooth
        target_w = 400 * self.progress_val
        current_coords = self.prog_canvas.coords(self.prog_fill)
        new_w = current_coords[2] + (target_w - current_coords[2]) * 0.1
        self.prog_canvas.coords(self.prog_fill, 0, 4, new_w, 7)
        self.prog_canvas.coords(self.prog_glow, new_w-5, 0, new_w+5, 10)

        self.after(30, self.animate_elements)

    def set_progress(self, val):
        self.progress_val = val

    def start_bootstrap(self):
        threading.Thread(target=self.run_update, daemon=True).start()

    def run_update(self):
        try:
            self.set_progress(0.1)
            # 1. Checar versão
            remote = requests.get(VERSION_URL, timeout=5).text.strip()
            self.set_progress(0.3)
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
            
            self.set_progress(1.0)
            self.lbl_status.configure(text="SYSTEM READY")
            time.sleep(1.2)
            self.animating = False
            self.quit()
        except:
            self.quit()

def main():
    # Tenta rodar primeiro o arquivo local para desenvolvimento/testes
    local_dev_file = os.path.join(os.path.dirname(__file__), "organizar_musicas.py")
    
    if os.path.exists(local_dev_file):
        with open(local_dev_file, "r", encoding="utf-8") as f: code = f.read()
        target_code = code
    elif os.path.exists(LOCAL_CORE):
        with open(LOCAL_CORE, "r", encoding="utf-8") as f: code = f.read()
        target_code = code
    else:
        target_code = None

    app = NeuralSplash()
    app.mainloop()
    app.destroy()

    if target_code:
        import mutagen, pygame, PIL, requests
        scope = {
            '__name__': '__main__', 'ctk': ctk, 'ctypes': ctypes, 'os': os, 'sys': sys,
            'mutagen': mutagen, 'pygame': pygame, 'PIL': PIL, 'requests': requests, 'math': math
        }
        exec(target_code, scope)

if __name__ == "__main__":
    main()
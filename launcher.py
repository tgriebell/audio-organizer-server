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
# ENGINE DE SISTEMA (WIN32 ADVANCED)
# ==============================================================================
def set_app_id():
    try:
        myappid = 'audioorganizer.pro.v2.5'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except: pass

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# CONFIGURAÇÕES GITHUB
GITHUB_USER = "tgriebell"
REPO_NAME = "audio-organizer-server"
BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main"
VERSION_URL = f"{BASE_URL}/version.txt"
SCRIPT_URL = f"{BASE_URL}/organizar_musicas.py"

TEMP_DIR = os.path.join(tempfile.gettempdir(), "AudioOrganizer_Cache")
if not os.path.exists(TEMP_DIR): os.makedirs(TEMP_DIR)
LOCAL_SCRIPT = os.path.join(TEMP_DIR, "core_v2.py")
LOCAL_VERSION = os.path.join(TEMP_DIR, "version.txt")

# THEME ENGINE
COLOR_BG = "#000000"
COLOR_ACCENT = "#00ff66"
COLOR_ACCENT_DIM = "#002211"

class CyberSplash(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 1. Configuração de Janela Stealth
        self.overrideredirect(True)
        self.attributes("-alpha", 0.0) # Inicia invisível para o Fade-in
        self.configure(fg_color=COLOR_BG)
        
        # Centralização Matemática Dinâmica
        w, h = 600, 400
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f'{w}x{h}+{int((sw-w)/2)}+{int((sh-h)/2)}')

        # 2. Hack de Barra de Tarefas (Show Icon)
        self.after(10, self.force_taskbar)

        # 3. UI Layering (Efeito de Profundidade)
        self.main_frame = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0, border_width=1, border_color="#111")
        self.main_frame.pack(fill="both", expand=True)

        # --- CANVAS DE ONDAS (Física de Áudio Centralizada) ---
        self.canvas_h = 150
        self.canvas = tk.Canvas(self.main_frame, height=self.canvas_h, bg=COLOR_BG, highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.4, anchor="center", relwidth=1.0)
        
        self.bars = []
        self.num_bars = 24
        bar_w, gap = 6, 4
        total_w = (self.num_bars * bar_w) + ((self.num_bars - 1) * gap)
        # Cálculo exato do centro do canvas
        start_x = (600 - total_w) / 2
        
        for i in range(self.num_bars):
            x0 = start_x + i * (bar_w + gap)
            rect = self.canvas.create_rectangle(x0, 75, x0 + bar_w, 75, fill=COLOR_ACCENT, outline="")
            self.bars.append(rect)

        # --- TIPOGRAFIA PREMIUM ---
        self.lbl_audio = ctk.CTkLabel(self.main_frame, text="AUDIO", font=("Segoe UI Light", 32), text_color="#555")
        self.lbl_audio.place(relx=0.43, rely=0.65, anchor="e")

        self.lbl_org = ctk.CTkLabel(self.main_frame, text="ORGANIZER", font=("Segoe UI", 32, "bold"), text_color="white")
        self.lbl_org.place(relx=0.44, rely=0.65, anchor="w")
        
        self.lbl_status = ctk.CTkLabel(self.main_frame, text="SYNCHRONIZING SYSTEM CORE...", font=("Consolas", 9), text_color=COLOR_ACCENT)
        self.lbl_status.place(relx=0.5, rely=0.75, anchor="center")

        self.progress = ctk.CTkProgressBar(self.main_frame, width=350, height=2, progress_color=COLOR_ACCENT, fg_color="#0a0a0a")
        self.progress.place(relx=0.5, rely=0.85, anchor="center")
        self.progress.set(0)

        # Animações
        self.animating = True
        self.wave_phase = 0
        self.animate_waves()
        self.fade_in()
        
        self.after(1000, self.start_logic)

    def force_taskbar(self):
        # Hack Win32 para forçar ícone em janela frameless
        try:
            GWL_EXSTYLE = -20
            WS_EX_APPWINDOW = 0x00040000
            WS_EX_TOOLWINDOW = 0x00000080
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style = style & ~WS_EX_TOOLWINDOW
            style = style | WS_EX_APPWINDOW
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
            
            # Re-aplicar para forçar atualização
            self.withdraw()
            self.after(10, self.deiconify)
        except: pass

    def fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1.0:
            self.attributes("-alpha", alpha + 0.05)
            self.after(20, self.fade_in)

    def animate_waves(self):
        if not self.animating: return
        self.wave_phase += 0.2
        for i, rect in enumerate(self.bars):
            # Onda senoidal com atenuação nas bordas (Física real)
            dist_from_center = abs(i - self.num_bars/2) / (self.num_bars/2)
            attenuation = math.cos(dist_from_center * math.pi / 2)
            
            h = (math.sin(self.wave_phase + i * 0.5) * 40 + 50) * attenuation
            h = max(4, h + random.randint(-5, 5))
            
            x0, _, x1, _ = self.canvas.coords(rect)
            self.canvas.coords(rect, x0, 75 - h/2, x1, 75 + h/2)
            
            # Efeito Glow Dinâmico
            color = COLOR_ACCENT if h > 50 else COLOR_ACCENT_DIM
            self.canvas.itemconfig(rect, fill=color)
            
        self.after(50, self.animate_waves)

    def start_logic(self):
        threading.Thread(target=self.run_updater, daemon=True).start()

    def run_updater(self):
        try:
            self.progress.set(0.3)
            time.sleep(1)
            self.progress.set(0.7)
            time.sleep(0.5)
            self.progress.set(1.0)
            self.animating = False
            self.quit()
        except: self.quit()

def main():
    set_app_id()
    app = CyberSplash()
    app.mainloop()
    app.destroy()

    if os.path.exists(LOCAL_SCRIPT):
        with open(LOCAL_SCRIPT, "r", encoding="utf-8") as f:
            code = f.read()
        
        import mutagen, pygame, PIL, requests
        scope = {
            '__name__': '__main__', 'ctk': ctk, 'ctypes': ctypes, 'os': os, 'sys': sys,
            'mutagen': mutagen, 'pygame': pygame, 'PIL': PIL, 'requests': requests,
            'Image': Image, 'ImageTk': ImageTk, 'math': math
        }
        exec(code, scope)

if __name__ == "__main__":
    main()
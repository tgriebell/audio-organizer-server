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
from PIL import Image, ImageTk

# Garantir que o PyInstaller detecte estas dependências
try:
    import mutagen
    import pygame
    import requests
    import PIL
except ImportError:
    pass

# ==============================================================================
# CONFIGURAÇÕES TÉCNICAS
# ==============================================================================
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ID Único para Taskbar
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("tgriebell.audioorganizer.v2.5")
except:
    pass

GITHUB_USER = "tgriebell"
REPO_NAME = "audio-organizer-server"
BRANCH = "main"
BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}"
VERSION_URL = f"{BASE_URL}/version.txt"
SCRIPT_URL = f"{BASE_URL}/organizar_musicas.py"

TEMP_DIR = os.path.join(tempfile.gettempdir(), "AudioOrganizer_Cache")
if not os.path.exists(TEMP_DIR): os.makedirs(TEMP_DIR)
LOCAL_SCRIPT = os.path.join(TEMP_DIR, "core_v2.py")
LOCAL_VERSION = os.path.join(TEMP_DIR, "version.txt")

COLOR_BG = "#050505"
COLOR_ACCENT = "#00ff66"

class CyberSplash(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.overrideredirect(True)
        self.configure(fg_color=COLOR_BG)
        
        # Centralização Dinâmica (Center Screen)
        w, h = 550, 420
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f'{w}x{h}+{int((sw-w)/2)}+{int((sh-h)/2)}')

        # Ícone
        icon_file = resource_path("icone_perfeito.ico")
        if os.path.exists(icon_file): self.iconbitmap(icon_file)

        # Hack Taskbar Icon
        self.after(200, self.force_taskbar)

        self.main_frame = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0, border_width=1, border_color="#1a1a1a")
        self.main_frame.pack(fill="both", expand=True)

        # --- WAVEFORM (Centro Absoluto) ---
        self.canvas = tk.Canvas(self.main_frame, height=120, bg=COLOR_BG, highlightthickness=0)
        self.canvas.pack(fill="x", pady=(50, 20))
        
        self.bars = []
        num_bars, bar_w, gap = 18, 8, 6
        total_w = (num_bars * bar_w) + ((num_bars - 1) * gap)
        start_x = (550 - total_w) / 2 # Centro da janela de 550
        
        for i in range(num_bars):
            x0 = start_x + i * (bar_w + gap)
            rect = self.canvas.create_rectangle(x0, 60, x0 + bar_w, 60, fill=COLOR_ACCENT, outline="")
            self.bars.append(rect)

        # --- LOGO (Centro Absoluto) ---
        self.logo_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.logo_frame.pack(fill="x")

        # Texto AUDIO (Fino) + ORGANIZER (Bold)
        self.lbl_audio = ctk.CTkLabel(self.logo_frame, text="AUDIO ", font=("Montserrat Light", 30), text_color="#ccc")
        self.lbl_audio.pack(side="left", expand=True, anchor="e")

        self.lbl_org = ctk.CTkLabel(self.logo_frame, text="ORGANIZER", font=("Montserrat", 30, "bold"), text_color="white")
        self.lbl_org.pack(side="left", expand=True, anchor="w")
        
        self.lbl_edition = ctk.CTkLabel(self.main_frame, text="PROFESSIONAL EDITION v2.5", font=("Consolas", 9, "bold"), text_color=COLOR_ACCENT)
        self.lbl_edition.pack(pady=(5, 20))

        self.lbl_status = ctk.CTkLabel(self.main_frame, text="Iniciando...", font=("Consolas", 10), text_color="gray")
        self.lbl_status.pack()

        self.progress = ctk.CTkProgressBar(self.main_frame, width=400, height=3, progress_color=COLOR_ACCENT, fg_color="#111")
        self.progress.pack(pady=20)
        self.progress.set(0)

        self.animating = True
        self.animate_waves()
        self.after(1000, self.start_bootstrap)

    def force_taskbar(self):
        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            style = style & ~0x00000080 | 0x00040000
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)
            self.withdraw(); self.after(10, self.deiconify)
        except: pass

    def animate_waves(self):
        if not self.animating: return
        for rect in self.bars:
            h = random.randint(10, 80)
            x0, _, x1, _ = self.canvas.coords(rect)
            self.canvas.coords(rect, x0, 60 - h/2, x1, 60 + h/2)
        self.after(80, self.animate_waves)

    def start_bootstrap(self):
        threading.Thread(target=self.run_logic, daemon=True).start()

    def run_logic(self):
        try:
            time.sleep(1)
            self.lbl_status.configure(text="Sincronizando metadados...")
            self.progress.set(0.4)
            
            # Checar Versão
            remote = None
            try:
                r = requests.get(VERSION_URL, timeout=5)
                if r.status_code == 200: remote = r.text.strip()
            except: pass
            
            if remote:
                local = "0.0"
                if os.path.exists(LOCAL_VERSION):
                    with open(LOCAL_VERSION, "r") as f: local = f.read().strip()
                
                if remote != local:
                    self.lbl_status.configure(text=f"Baixando core v{remote}...")
                    r_core = requests.get(SCRIPT_URL)
                    if r_core.status_code == 200:
                        with open(LOCAL_SCRIPT, "wb") as f: f.write(r_core.content)
                        with open(LOCAL_VERSION, "w") as f: f.write(remote)

            self.progress.set(1.0)
            self.lbl_status.configure(text="Iniciando interface...")
            time.sleep(0.8)
            self.animating = False
            self.quit()
        except: self.quit()

def main():
    splash = CyberSplash()
    splash.mainloop()
    splash.destroy()

    if os.path.exists(LOCAL_SCRIPT):
        with open(LOCAL_SCRIPT, "r", encoding="utf-8") as f:
            code = f.read()
        
        # Injetar dependências no escopo global do exec
        # Importante para o Mutagen e outros funcionarem
        import mutagen, pygame, PIL, requests
        scope = {
            '__name__': '__main__',
            'ctk': ctk,
            'ctypes': ctypes,
            'os': os,
            'sys': sys,
            'mutagen': mutagen,
            'pygame': pygame,
            'PIL': PIL,
            'requests': requests
        }
        exec(code, scope)

if __name__ == "__main__":
    main()
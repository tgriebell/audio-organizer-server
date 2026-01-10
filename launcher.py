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

# ==============================================================================
# CONFIGURAÇÕES TÉCNICAS DE SISTEMA
# ==============================================================================
def resource_path(relative_path):
    """ Gerencia caminhos de recursos dentro do EXE ou em Desenvolvimento """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ID Único para o Windows agrupar o app na barra de tarefas
try:
    myappid = 'tgriebell.audioorganizer.v2.5.pro'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

# CONFIGURAÇÕES GITHUB
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

# DESIGN SYSTEM
COLOR_BG = "#050505"
COLOR_ACCENT = "#00ff66"
COLOR_ACCENT_DIM = "#004d1f"

class CyberSplash(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Janela Frameless e Centralizada
        self.overrideredirect(True)
        self.configure(fg_color=COLOR_BG)
        
        width, height = 550, 400
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - width) / 2
        y = (sh - height) / 2
        self.geometry(f'{width}x{height}+{int(x)}+{int(y)}')

        # Ícone
        icon_file = resource_path("icone_perfeito.ico")
        if os.path.exists(icon_file):
            self.iconbitmap(icon_file)

        # Container Principal
        self.frame = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0, border_width=1, border_color="#1a1a1a")
        self.frame.pack(fill="both", expand=True)

        # --- WAVEFORM ANIMADA (Centralizada Matemática) ---
        self.canvas = tk.Canvas(self.frame, height=120, bg=COLOR_BG, highlightthickness=0)
        self.canvas.pack(fill="x", pady=(50, 20))
        
        self.bars = []
        num_bars, bar_w, gap = 20, 6, 4
        total_w = (num_bars * bar_w) + ((num_bars - 1) * gap)
        start_x = (550 - total_w) / 2
        
        for i in range(num_bars):
            x0 = start_x + i * (bar_w + gap)
            rect = self.canvas.create_rectangle(x0, 60, x0 + bar_w, 60, fill=COLOR_ACCENT, outline="")
            self.bars.append(rect)

        # --- TEXTOS ---
        self.lbl_brand = ctk.CTkLabel(self.frame, text="AUDIO ORGANIZER", font=("Montserrat", 28, "bold"), text_color="white")
        self.lbl_brand.pack()
        
        self.lbl_edition = ctk.CTkLabel(self.frame, text="PROFESSIONAL EDITION v2.5", font=("Consolas", 10, "bold"), text_color=COLOR_ACCENT)
        self.lbl_edition.pack(pady=(0, 30))

        self.lbl_status = ctk.CTkLabel(self.frame, text="Iniciando motores de IA...", font=("Consolas", 11), text_color="#555")
        self.lbl_status.pack()

        self.progress = ctk.CTkProgressBar(self.frame, width=400, height=3, progress_color=COLOR_ACCENT, fg_color="#111", border_width=0)
        self.progress.pack(pady=20)
        self.progress.set(0)

        # Estados de Carregamento Dinâmicos
        self.loading_msgs = [
            "Sincronizando núcleos de processamento neural...",
            "Calibrando algoritmos de reconhecimento de frequência...",
            "Carregando base de dados de gêneros musicais...",
            "Analisando integridade da biblioteca local...",
            "Estabelecendo conexão segura com o servidor..."
        ]

        self.animating = True
        self.animate_waves()
        self.cycle_messages()
        
        # Iniciar Lógica
        self.after(500, self.start_bootstrap)

    def animate_waves(self):
        if not self.animating: return
        for rect in self.bars:
            h = random.randint(10, 90)
            x0, _, x1, _ = self.canvas.coords(rect)
            self.canvas.coords(rect, x0, 60 - h/2, x1, 60 + h/2)
            # Efeito de cor baseado na altura
            color = COLOR_ACCENT if h > 40 else COLOR_ACCENT_DIM
            self.canvas.itemconfig(rect, fill=color)
        self.after(70, self.animate_waves)

    def cycle_messages(self):
        if not self.animating: return
        self.lbl_status.configure(text=random.choice(self.loading_msgs))
        self.after(2200, self.cycle_messages)

    def start_bootstrap(self):
        threading.Thread(target=self.bootstrap_logic, daemon=True).start()

    def bootstrap_logic(self):
        try:
            self.progress.set(0.2)
            time.sleep(1) # Valor estético

            # Verificar Versão
            remote = None
            try:
                r = requests.get(VERSION_URL, timeout=5)
                if r.status_code == 200: remote = r.text.strip()
            except: pass

            self.progress.set(0.5)
            local = "0.0"
            if os.path.exists(LOCAL_VERSION):
                with open(LOCAL_VERSION, "r") as f: local = f.read().strip()

            if remote and remote != local:
                self.lbl_status.configure(text=f"Instalando Patch {remote}...")
                r_script = requests.get(SCRIPT_URL)
                if r_script.status_code == 200:
                    with open(LOCAL_SCRIPT, "wb") as f: f.write(r_script.content)
                    with open(LOCAL_VERSION, "w") as f: f.write(remote)
                self.progress.set(0.8)

            self.progress.set(1.0)
            self.lbl_status.configure(text="Sincronização Completa!")
            time.sleep(0.8)
            self.animating = False
            self.quit()
        except:
            self.quit()

def main():
    splash = CyberSplash()
    splash.mainloop()
    splash.destroy()

    if os.path.exists(LOCAL_SCRIPT):
        with open(LOCAL_SCRIPT, "r", encoding="utf-8") as f:
            code = f.read()
        
        # Executar o Core com todas as dependências necessárias injetadas
        scope = {
            '__name__': '__main__',
            'ctk': ctk,
            'ctypes': ctypes,
            'os': os,
            'sys': sys,
            'Image': Image,
            'ImageTk': ImageTk
        }
        exec(code, scope)

if __name__ == "__main__":
    main()

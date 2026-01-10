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

# Dummy imports para o PyInstaller detectar dependências do script baixado
try:
    import mutagen
    import pygame
    from PIL import Image, ImageTk
except ImportError:
    pass

# ==============================================================================
# CONFIGURAÇÃO DE DEBUG & SYSTEM
# ==============================================================================
# Correção para o ícone na barra de tarefas (Windows)
try:
    myappid = 'br.com.audioorganizer.launcher.v2.5'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

def log_fatal_error(e):
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    log_path = os.path.join(desktop, 'ERRO_LAUNCHER.txt')
    with open(log_path, "w") as f:
        f.write(f"ERRO FATAL NO LAUNCHER:\n{str(e)}\n\nDETALHES:\n{traceback.format_exc()}")

GITHUB_USER = "tgriebell"
REPO_NAME = "audio-organizer-server"
BRANCH = "main"

BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}"
VERSION_URL = f"{BASE_URL}/version.txt"
SCRIPT_URL = f"{BASE_URL}/organizar_musicas.py"

TEMP_DIR = os.path.join(tempfile.gettempdir(), "AudioOrganizer_Cache")
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

LOCAL_SCRIPT = os.path.join(TEMP_DIR, "core_v2.py")
LOCAL_VERSION = os.path.join(TEMP_DIR, "version.txt")

def resource_path(relative_path):
    """ Retorna o caminho absoluto, funcionando para dev e para o PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# PALETA CYBER-DARK
COLOR_BG = "#050505"
COLOR_ACCENT = "#00ff66" # Neon Green
COLOR_ACCENT_DIM = "#008f39"
COLOR_TEXT = "#ffffff"

class CyberSplash(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuração de Janela
        self.overrideredirect(True)
        self.configure(fg_color=COLOR_BG)
        
        # Centralizar
        w, h = 500, 350
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width/2) - (w/2)
        y = (screen_height/2) - (h/2)
        self.geometry(f'{w}x{h}+{int(x)}+{int(y)}')

        # Ícone Seguro
        icon_path = resource_path("icone_perfeito.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)


        # Forçar foco e taskbar (Hack para overrideredirect)
        self.after(10, self.force_taskbar)

        self.main_frame = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Borda Neon Fina ao redor da janela
        self.main_frame.configure(border_width=1, border_color="#1a1a1a")

        # --- CANVAS WAVEFORM ---
        self.canvas_h = 120
        self.canvas = tk.Canvas(self.main_frame, height=self.canvas_h, bg=COLOR_BG, highlightthickness=0)
        self.canvas.pack(fill="x", pady=(20, 10))
        
        self.bars = []
        self.num_bars = 16
        bar_width = 8
        gap = 6
        total_w = (self.num_bars * bar_width) + ((self.num_bars - 1) * gap)
        start_x = (480 - total_w) / 2
        
        for i in range(self.num_bars):
            x0 = start_x + i * (bar_width + gap)
            y0 = self.canvas_h / 2
            # Efeito Glow simulado com cores
            rect = self.canvas.create_rectangle(x0, y0, x0 + bar_width, y0, fill=COLOR_ACCENT, outline="")
            self.bars.append(rect)

        self.animating = True
        self.animate_waves()

        # --- LOGO ---
        self.title_frame = ctk.CTkFrame(self.main_frame, fg_color=COLOR_BG)
        self.title_frame.pack(pady=(5, 25))

        self.lbl_audio = ctk.CTkLabel(self.title_frame, text="AUDIO", 
                                      font=("Montserrat Light", 26), text_color="#cccccc")
        self.lbl_audio.pack(side="left")

        self.lbl_org = ctk.CTkLabel(self.title_frame, text="ORGANIZER", 
                                    font=("Montserrat", 26, "bold"), text_color="white")
        self.lbl_org.pack(side="left", padx=(5, 0))
        
        self.lbl_edition = ctk.CTkLabel(self.main_frame, text="PROFESSIONAL EDITION v2.5", 
                                        font=("Consolas", 9, "bold"), text_color=COLOR_ACCENT, spacing=2)
        self.lbl_edition.pack(pady=(0, 20))

        # --- PROGRESSO & STATUS ---
        self.status_msgs = [
            "Sincronizando núcleos de processamento...",
            "Calibrando algoritmos espectrais...",
            "Carregando base de metadados...",
            "Estabelecendo conexão segura..."
        ]
        self.current_msg_idx = 0
        
        self.lbl_status = ctk.CTkLabel(self.main_frame, text=self.status_msgs[0], 
                                       font=("Consolas", 10), text_color="gray")
        self.lbl_status.pack(pady=(0, 5))

        self.progress = ctk.CTkProgressBar(self.main_frame, width=400, height=2, 
                                           progress_color=COLOR_ACCENT, fg_color="#111", border_width=0)
        self.progress.pack(pady=(0, 20))
        self.progress.set(0)

        # Timer para alternar frases
        self.after(2000, self.cycle_status)
        self.after(1000, self.start_updater)

    def force_taskbar(self):
        # Pequeno hack para garantir que apareça na barra se possível
        try:
            self.wm_attributes("-topmost", 1)
            self.wm_attributes("-topmost", 0)
        except: pass

    def cycle_status(self):
        if not self.animating: return
        self.current_msg_idx = (self.current_msg_idx + 1) % len(self.status_msgs)
        self.lbl_status.configure(text=self.status_msgs[self.current_msg_idx])
        self.after(2500, self.cycle_status)

    def animate_waves(self):
        if not self.animating: return
        center_y = self.canvas_h / 2
        
        for i, rect in enumerate(self.bars):
            # Cria um padrão de onda senoidal + random
            import math
            t = time.time() * 5
            base_h = 20
            wave = math.sin(t + i*0.5) * 30 
            noise = random.randint(-15, 15)
            height = max(4, base_h + abs(wave) + noise)
            
            coords = self.canvas.coords(rect)
            x0, _, x1, _ = coords
            
            # Gradiente "Fake" mudando a cor baseado na altura
            color = COLOR_ACCENT if height > 40 else COLOR_ACCENT_DIM
            self.canvas.itemconfig(rect, fill=color)
            self.canvas.coords(rect, x0, center_y - height/2, x1, center_y + height/2)
            
        self.after(50, self.animate_waves)

    def update_ui(self, text, progress_val):
        # A atualização de texto aqui sobrescreve o ciclo automático apenas se crítico
        if progress_val >= 0.9:
            self.lbl_status.configure(text=text)
        self.progress.set(progress_val)
        self.update()

    def start_updater(self):
        thread = threading.Thread(target=self.run_logic)
        thread.start()

    def get_remote_version(self):
        try:
            r = requests.get(VERSION_URL, timeout=5)
            if r.status_code == 200: return r.text.strip()
        except: pass
        return None

    def get_local_version(self):
        if os.path.exists(LOCAL_VERSION):
            with open(LOCAL_VERSION, "r") as f: return f.read().strip()
        return "0.0"

    def run_logic(self):
        try:
            time.sleep(1) # Efeito dramático inicial

            remote = self.get_remote_version()
            local = self.get_local_version()
            
            self.update_ui("Verificando integridade neural...", 0.4)
            time.sleep(0.8)

            if remote and remote != local:
                self.lbl_status.configure(text=f"Baixando patch v{remote}...")
                self.update_ui(f"Baixando patch v{remote}...", 0.6)
                try:
                    r = requests.get(SCRIPT_URL)
                    if r.status_code == 200:
                        with open(LOCAL_SCRIPT, "wb") as f:
                            f.write(r.content)
                        with open(LOCAL_VERSION, "w") as f:
                            f.write(remote)
                    else:
                        pass # Falha silenciosa, usa cache
                except:
                    pass
            
            self.update_ui("Iniciando Core do Sistema...", 1.0)
            time.sleep(1.0)
            
            self.animating = False
            self.quit()
        except Exception as e:
            log_fatal_error(e)
            self.quit()

def main():
    try:
        app = CyberSplash()
        app.mainloop()
        app.destroy()
    except Exception as e:
        log_fatal_error(e)
        return

    if os.path.exists(LOCAL_SCRIPT):
        try:
            with open(LOCAL_SCRIPT, "r", encoding="utf-8") as f:
                code = f.read()
            scope = globals().copy()
            scope['__name__'] = '__launcher__'
            
            exec(code, scope)
            
            if "main" in scope:
                scope["main"]()
            elif "organizar" in scope:
                scope["organizar"]()
                
        except Exception as e:
            log_fatal_error(e)
            try:
                root = tk.Tk()
                root.withdraw()
                tk.messagebox.showerror("Erro Fatal", f"O App falhou ao iniciar.\nVerifique 'ERRO_LAUNCHER.txt'\nErro: {e}")
            except: pass
    else:
        # Fallback se não tiver internet na primeira vez e nem cache
        tk.messagebox.showerror("Erro de Conexão", "Não foi possível baixar o núcleo do sistema pela primeira vez.")

if __name__ == "__main__":
    main()
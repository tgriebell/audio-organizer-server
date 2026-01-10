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

# ==============================================================================
# CONFIGURAÇÃO DE DEBUG
# ==============================================================================
def log_fatal_error(e):
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    log_path = os.path.join(desktop, 'ERRO_LAUNCHER.txt')
    with open(log_path, "w") as f:
        f.write(f"ERRO FATAL NO LAUNCHER:\n{str(e)}\n\nDETALHES:\n{traceback.format_exc()}")

try:
    import mutagen
    from PIL import Image, ImageTk
except ImportError:
    pass

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

COLOR_BG = "#0a0a0a"
COLOR_NEON = "#00ff66"

class CyberSplash(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.overrideredirect(True)
        w, h = 450, 320 # Um pouco mais alto para caber o logo melhor
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width/2) - (w/2)
        y = (screen_height/2) - (h/2)
        self.geometry(f'{w}x{h}+{int(x)}+{int(y)}')
        self.configure(fg_color=COLOR_BG)

        if os.path.exists("icone_perfeito.ico"):
            self.iconbitmap("icone_perfeito.ico")

        self.main_frame = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # CANVAS DE ONDAS (Mais alto e dinâmico)
        self.canvas_h = 100
        self.canvas = tk.Canvas(self.main_frame, height=self.canvas_h, bg=COLOR_BG, highlightthickness=0)
        self.canvas.pack(fill="x", pady=(10, 5))
        
        self.bars = []
        self.num_bars = 9 # Mais barras
        bar_width = 10
        gap = 8
        total_w = (self.num_bars * bar_width) + ((self.num_bars - 1) * gap)
        start_x = (410 - total_w) / 2
        
        for i in range(self.num_bars):
            x0 = start_x + i * (bar_width + gap)
            y0 = self.canvas_h / 2
            # Usando cor neon para preencher
            rect = self.canvas.create_rectangle(x0, y0, x0 + bar_width, y0, fill=COLOR_NEON, outline="")
            self.bars.append(rect)

        self.animating = True
        self.animate_waves()

        # TIPOGRAFIA REFINADA
        # Como o CTK não suporta multiplas fontes no mesmo label fácil, vamos usar dois labels lado a lado
        self.title_frame = ctk.CTkFrame(self.main_frame, fg_color=COLOR_BG)
        self.title_frame.pack(pady=(5, 20))

        self.lbl_audio = ctk.CTkLabel(self.title_frame, text="AUDIO", 
                                      font=("Segoe UI Light", 24), text_color="white")
        self.lbl_audio.pack(side="left")

        self.lbl_org = ctk.CTkLabel(self.title_frame, text="ORGANIZER", 
                                    font=("Segoe UI", 24, "bold"), text_color="white")
        self.lbl_org.pack(side="left", padx=(5, 0))

        # STATUS
        self.status_msgs = ["Sincronizando biblioteca...", "Analisando frequências...", "Verificando versão...", "Conectando ao servidor..."]
        self.lbl_status = ctk.CTkLabel(self.main_frame, text=self.status_msgs[0], 
                                       font=("Consolas", 10), text_color="gray")
        self.lbl_status.pack(pady=(0, 5))

        # PROGRESSO COM GLOW (Simulado com cor vibrante)
        self.progress = ctk.CTkProgressBar(self.main_frame, width=350, height=4, 
                                           progress_color=COLOR_NEON, fg_color="#1f1f1f", border_width=0)
        self.progress.pack(pady=(0, 20))
        self.progress.set(0)

        self.lbl_ver = ctk.CTkLabel(self.main_frame, text="v2.1 Launcher", 
                                    font=("Arial", 8), text_color="#333")
        self.lbl_ver.place(relx=1.0, rely=1.0, anchor="se")

        self.after(1000, self.start_updater)

    def animate_waves(self):
        if not self.animating: return
        center_y = self.canvas_h / 2
        
        for rect in self.bars:
            # Variação maior
            height = random.randint(5, 80)
            coords = self.canvas.coords(rect)
            x0, _, x1, _ = coords
            self.canvas.coords(rect, x0, center_y - height/2, x1, center_y + height/2)
            
        self.after(80, self.animate_waves) # Mais rápido (80ms)

    def update_ui(self, text, progress_val):
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
            self.update_ui("Conectando ao GitHub...", 0.1)
            time.sleep(0.5)

            remote = self.get_remote_version()
            local = self.get_local_version()
            
            self.update_ui("Verificando integridade...", 0.3)
            time.sleep(0.5)

            if remote and remote != local:
                self.update_ui(f"Baixando atualização {remote}...", 0.5)
                try:
                    r = requests.get(SCRIPT_URL)
                    if r.status_code == 200:
                        with open(LOCAL_SCRIPT, "wb") as f:
                            f.write(r.content)
                        with open(LOCAL_VERSION, "w") as f:
                            f.write(remote)
                        self.update_ui("Atualização instalada!", 0.8)
                    else:
                        self.update_ui("Erro no download. Usando cache.", 0.8)
                except:
                    self.update_ui("Falha na conexão.", 0.8)
            else:
                self.update_ui("Sistema atualizado.", 0.8)
                time.sleep(0.5)

            self.update_ui("Iniciando Core...", 1.0)
            time.sleep(0.8)
            
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
        pass

if __name__ == "__main__":
    main()
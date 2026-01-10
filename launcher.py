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
        myappid = 'audioorganizer.pro.v2.6'
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
SCRIPT_URL = f"{BASE_URL}/organizar_musicas.py"

TEMP_DIR = os.path.join(tempfile.gettempdir(), "AudioOrganizer_Elite_Cache")
if not os.path.exists(TEMP_DIR): os.makedirs(TEMP_DIR)
LOCAL_CORE = os.path.join(TEMP_DIR, "core_v2_6.py")

# THEME ENGINE
COLOR_BG = "#050505"
COLOR_ACCENT = "#00ff66"
COLOR_ACCENT_DIM = "#003311"

class CyberSplash(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.overrideredirect(True)
        self.attributes("-alpha", 0.0) 
        self.configure(fg_color=COLOR_BG)
        
        # Centralização Dinâmica
        w, h = 600, 400
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f'{w}x{h}+{int((sw-w)/2)}+{int((sh-h)/2)}')

        # Hack de Barra de Tarefas
        self.after(100, self.force_taskbar)

        # UI Container com Borda Neon Fina
        self.main_frame = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0, border_width=1, border_color="#1a1a1a")
        self.main_frame.pack(fill="both", expand=True)

        # --- CANVAS DE ONDAS (Centralização Matemática Absoluta) ---
        self.canvas_h = 120
        self.canvas = tk.Canvas(self.main_frame, height=self.canvas_h, bg=COLOR_BG, highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.4, anchor="center", relwidth=1.0)
        
        self.bars = []
        self.num_bars = 30
        bar_w, gap = 4, 4
        
        # Desenha as barras partindo do centro do canvas (300px)
        # Largura total = (30 * 4) + (29 * 4) = 120 + 116 = 236
        total_w = (self.num_bars * bar_w) + ((self.num_bars - 1) * gap)
        start_x = (600 - total_w) / 2
        
        for i in range(self.num_bars):
            x0 = start_x + i * (bar_w + gap)
            rect = self.canvas.create_rectangle(x0, 60, x0 + bar_w, 60, fill=COLOR_ACCENT, outline="")
            self.bars.append(rect)

        # --- TIPOGRAFIA ---
        self.lbl_brand = ctk.CTkLabel(self.main_frame, text="AUDIO ORGANIZER", font=("Inter Black", 34), text_color="white")
        self.lbl_brand.place(relx=0.5, rely=0.65, anchor="center")
        
        self.lbl_status = ctk.CTkLabel(self.main_frame, text="Sincronizando bibliotecas neurais...", font=("Consolas", 10), text_color=COLOR_ACCENT)
        self.lbl_status.place(relx=0.5, rely=0.78, anchor="center")

        self.progress = ctk.CTkProgressBar(self.main_frame, width=350, height=2, progress_color=COLOR_ACCENT, fg_color="#0a0a0a")
        self.progress.place(relx=0.5, rely=0.88, anchor="center")
        self.progress.set(0)

        self.animating = True
        self.wave_phase = 0
        self.animate_waves()
        self.fade_in()
        
        self.after(1000, self.start_logic)

    def force_taskbar(self):
        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            style = style & ~0x00000080 | 0x00040000
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)
            self.withdraw(); self.after(10, self.deiconify)
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
            dist = abs(i - self.num_bars/2) / (self.num_bars/2)
            att = math.cos(dist * math.pi / 2)
            h = (math.sin(self.wave_phase + i * 0.4) * 40 + 50) * att
            h = max(4, h + random.randint(-3, 3))
            
            x0, _, x1, _ = self.canvas.coords(rect)
            self.canvas.coords(rect, x0, 60 - h/2, x1, 60 + h/2)
            self.canvas.itemconfig(rect, fill=COLOR_ACCENT if h > 45 else COLOR_ACCENT_DIM)
            
        self.after(50, self.animate_waves)

    def start_logic(self):
        threading.Thread(target=self.run_bootstrap, daemon=True).start()

    def run_bootstrap(self):
        try:
            self.progress.set(0.3)
            # Baixar script se não existir ou sempre atualizar
            r = requests.get(SCRIPT_URL, timeout=10)
            if r.status_code == 200:
                with open(LOCAL_CORE, "wb") as f: f.write(r.content)
            self.progress.set(1.0)
            time.sleep(0.5)
            self.animating = False
            self.quit()
        except Exception as e:
            print(f"Erro no bootstrap: {e}")
            self.quit()

def main():
    set_app_id()
    splash = CyberSplash()
    splash.mainloop()
    splash.destroy()

    if os.path.exists(LOCAL_CORE):
        with open(LOCAL_CORE, "r", encoding="utf-8") as f:
            code = f.read()
        
        import mutagen, pygame, PIL, requests
        scope = {
            '__name__': '__main__', 'ctk': ctk, 'ctypes': ctypes, 'os': os, 'sys': sys,
            'mutagen': mutagen, 'pygame': pygame, 'PIL': PIL, 'requests': requests,
            'Image': Image, 'ImageTk': ImageTk, 'math': math
        }
        try:
            exec(code, scope)
        except Exception as e:
            # Reportar erro se o app principal falhar
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Erro de Inicialização", f"O Core do sistema falhou:\n{e}\n\n{traceback.format_exc()}")
    else:
        messagebox.showerror("Erro de Rede", "Não foi possível baixar os componentes do sistema.")

if __name__ == "__main__":
    main()

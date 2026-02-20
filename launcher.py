import os
import sys
import requests
import time
import threading
import tempfile
import ctypes
import math
import tkinter as tk
import customtkinter as ctk

# ==============================================================================
# ENGINE DE SISTEMA (WIN32 TASKBAR HACK)
# ==============================================================================
try:
    myappid = 'tgriebell.audioorganizer.launcher.v3.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except: pass

# CONFIGURAÇÕES GITHUB
GITHUB_USER = "tgriebell"
REPO_NAME = "audio-organizer-server"
BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main"
VERSION_URL = f"{BASE_URL}/version.txt"
SCRIPT_URL = f"{BASE_URL}/organizar_musicas.py"

TEMP_DIR = os.path.join(tempfile.gettempdir(), "AudioOrganizer_Neural_Cache")
if not os.path.exists(TEMP_DIR): os.makedirs(TEMP_DIR)
LOCAL_CORE = os.path.join(TEMP_DIR, "core_v3_0.py")
LOCAL_VERSION = os.path.join(TEMP_DIR, "version.txt")

COLOR_BG = "#05070a"
COLOR_ACCENT = "#00ff66"
COLOR_NEON_BLUE = "#00ccff"
COLOR_STATUS = "#aaaaaa"

# ==============================================================================
# SPLASH SCREEN COM ATUALIZADOR INTEGRADO
# ==============================================================================

class NeuralSplash(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.configure(fg_color=COLOR_BG)
        
        w, h = 600, 480
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f'{w}x{h}+{int((sw-w)/2)}+{int((sh-h)/2)}')

        self.main_frame = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0, border_width=1, border_color="#1a1a1a")
        self.main_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.main_frame, height=140, bg=COLOR_BG, highlightthickness=0)
        self.canvas.place(relx=0.5, y=120, anchor="center", width=500)
        
        self.bars = []; self.glows = []
        num_bars, bar_w, gap = 28, 4, 6
        start_x = (500 - (num_bars * (bar_w + gap))) / 2 
        
        for i in range(num_bars):
            x0 = start_x + i * (bar_w + gap)
            glow = self.canvas.create_rectangle(x0-2, 70, x0+bar_w+2, 70, fill="#00441a", outline="")
            rect = self.canvas.create_rectangle(x0, 70, x0+bar_w, 70, fill=COLOR_ACCENT, outline="")
            self.bars.append(rect); self.glows.append(glow)

        self.title_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.title_container.place(relx=0.5, y=240, anchor="center")
        ctk.CTkLabel(self.title_container, text="AUDIO", font=("Segoe UI Light", 42), text_color="white").pack(side="left")
        ctk.CTkLabel(self.title_container, text=" ORGANIZER", font=("Segoe UI", 42, "bold"), text_color="white").pack(side="left")

        ctk.CTkLabel(self.main_frame, text="by Thiago Griebel • TODOS OS DIREITOS RESERVADOS", font=("Segoe UI", 9, "bold"), text_color=COLOR_NEON_BLUE).place(relx=0.5, y=290, anchor="center")
        
        self.lbl_status = ctk.CTkLabel(self.main_frame, text="CHECKING FOR NEURAL UPDATES...", font=("Consolas", 10), text_color=COLOR_STATUS)
        self.lbl_status.place(relx=0.5, y=380, anchor="center")

        self.prog_canvas = tk.Canvas(self.main_frame, width=400, height=4, bg="#0a1530", highlightthickness=0)
        self.prog_canvas.place(relx=0.5, y=420, anchor="center")
        self.prog_fill = self.prog_canvas.create_rectangle(0, 0, 0, 4, fill=COLOR_ACCENT, outline="")

        self.animating = True; self.phase = 0; self.progress_val = 0
        self.animate_elements()
        self.start_bootstrap()

    def animate_elements(self):
        if not self.animating: return
        self.phase += 0.15
        for i, rect in enumerate(self.bars):
            dist = abs(i - len(self.bars)/2) / (len(self.bars)/2)
            att = math.cos(dist * math.pi / 2)
            h = (math.sin(self.phase + i * 0.3) * 45 + 50) * att
            try:
                self.canvas.coords(rect, self.canvas.coords(rect)[0], 70 - h/2, self.canvas.coords(rect)[2], 70 + h/2)
                self.canvas.coords(self.glows[i], self.canvas.coords(rect)[0]-2, 70 - h/2 - 2, self.canvas.coords(rect)[2]+2, 70 + h/2 + 2)
            except: pass

        target_w = 400 * self.progress_val
        curr_w = self.prog_canvas.coords(self.prog_fill)[2]
        self.prog_canvas.coords(self.prog_fill, 0, 0, curr_w + (target_w - curr_w) * 0.1, 4)
        self.after(30, self.animate_elements)

    def start_bootstrap(self):
        threading.Thread(target=self.run_update, daemon=True).start()

    def run_update(self):
        try:
            # 1. Checar versão remota
            self.progress_val = 0.2
            remote_v = requests.get(VERSION_URL, timeout=5).text.strip()
            
            local_v = "0.0"
            if os.path.exists(LOCAL_VERSION):
                with open(LOCAL_VERSION, "r") as f: local_v = f.read().strip()
            
            # 2. Baixar se necessário
            if remote_v != local_v or not os.path.exists(LOCAL_CORE):
                self.lbl_status.configure(text=f"SYNCING NEURAL CORE v{remote_v}...")
                self.progress_val = 0.5
                r = requests.get(SCRIPT_URL, timeout=15)
                if r.status_code == 200:
                    with open(LOCAL_CORE, "wb") as f: f.write(r.content)
                    with open(LOCAL_VERSION, "w") as f: f.write(remote_v)
            
            self.progress_val = 1.0
            self.lbl_status.configure(text="SYSTEM READY")
            time.sleep(0.8)
            self.animating = False
            self.after(100, self.quit)
        except Exception as e:
            print(f"Update failed: {e}")
            self.after(100, self.quit)

def main():
    # Se houver um arquivo local para testes, prioriza ele
    dev_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "organizar_musicas.py")
    
    if not os.path.exists(dev_file):
        app = NeuralSplash()
        app.mainloop()
        app.destroy()
        target_path = LOCAL_CORE
    else:
        target_path = dev_file

    if os.path.exists(target_path):
        import mutagen, shutil, queue, json, runpy, re
        runpy.run_path(target_path, run_name="__main__")

if __name__ == "__main__":
    main()

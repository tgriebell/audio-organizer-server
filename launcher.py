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
# ENGINE DE SISTEMA (WIN32 TASKBAR & ICON HACK)
# ==============================================================================
def set_app_icon(window, icon_path):
    # Hack for Windows Tkinter overrideredirect taskbar icons
    try:
        if sys.platform == "win32":
            import ctypes
            hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
            icon_flags = 1 # ICON_BIG (0 is ICON_SMALL)
            hicon = ctypes.windll.user32.LoadImageW(0, icon_path, 1, 0, 0, 0x00000010 | 0x00008000)
            ctypes.windll.user32.SendMessageW(hwnd, 0x0080, icon_flags, hicon)
    except Exception as e:
        print(f"Icon loader error: {e}")
try:
    myappid = 'tgriebell.audioorganizer.neural.v4.1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except: pass

def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

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

COLOR_BG = "#03080a"
COLOR_ACCENT = "#05d590"
COLOR_NEON_BLUE = "#048a60"
COLOR_STATUS = "#446655"

# ==============================================================================
# SPLASH SCREEN COM ATUALIZADOR INTEGRADO
# ==============================================================================

class NeuralSplash(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes("-alpha", 0.0) # Start invisible for fade in
        self.configure(fg_color=COLOR_BG)
        
        # TRUE FULL SCREEN FOR PREMIUM SPLASH
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f'{sw}x{sh}+0+0')

        try:
            base_dir = get_base_path()
            icon_path = os.path.join(base_dir, "icone_novo.ico")
            set_app_icon(self, icon_path)
            self.iconbitmap(icon_path) # Fallback standard
        except: pass

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)

        # Centered container for vertical alignment
        self.center_area = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.center_area.place(relx=0.5, rely=0.5, anchor="center")

        # Expanded High-Res Animation Canvas
        self.canvas = tk.Canvas(self.center_area, height=200, width=800, bg=COLOR_BG, highlightthickness=0)
        self.canvas.pack(pady=(0, 40))
        
        self.bars = []; self.glows = []
        num_bars, bar_w, gap = 40, 6, 8
        start_x = (800 - (num_bars * (bar_w + gap))) / 2 
        
        for i in range(num_bars):
            x0 = start_x + i * (bar_w + gap)
            # Use lines with round caps for synthetic anti-aliasing
            glow2 = self.canvas.create_line(x0+bar_w/2, 100, x0+bar_w/2, 100, fill="#02160f", width=bar_w+6, capstyle="round")
            glow1 = self.canvas.create_line(x0+bar_w/2, 100, x0+bar_w/2, 100, fill="#042a1b", width=bar_w+2, capstyle="round")
            rect = self.canvas.create_line(x0+bar_w/2, 100, x0+bar_w/2, 100, fill=COLOR_ACCENT, width=bar_w-1, capstyle="round")
            self.bars.append(rect); self.glows.append((glow1, glow2))

        self.title_container = ctk.CTkFrame(self.center_area, fg_color="transparent")
        self.title_container.pack(pady=20)
        ctk.CTkLabel(self.title_container, text="AUDIO", font=("Segoe UI Light", 72), text_color="white").pack(side="left")
        ctk.CTkLabel(self.title_container, text=" ORGANIZER", font=("Segoe UI", 72, "bold"), text_color="white").pack(side="left")

        ctk.CTkLabel(self.center_area, text="NEURAL HUB ENGINE v5.0.0", font=("Consolas", 18, "bold"), text_color=COLOR_NEON_BLUE).pack(pady=10)
        ctk.CTkLabel(self.center_area, text="by Thiago Griebel • TODOS OS DIREITOS RESERVADOS", font=("Segoe UI", 12), text_color=COLOR_STATUS).pack(pady=5)
        
        self.lbl_status = ctk.CTkLabel(self.center_area, text="INITIALIZING QUANTUM CORE...", font=("Consolas", 14), text_color=COLOR_STATUS)
        self.lbl_status.pack(pady=(50, 10))

        self.prog_canvas = tk.Canvas(self.center_area, width=600, height=4, bg="#0a1530", highlightthickness=0)
        self.prog_canvas.pack(pady=10)
        self.prog_fill = self.prog_canvas.create_rectangle(0, 0, 0, 4, fill=COLOR_ACCENT, outline="")

        self.animating = True; self.phase = 0; self.progress_val = 0
        self.animate_elements()
        self.fade_in()
        self.start_bootstrap()

    def fade_in(self):
        a = self.attributes("-alpha")
        if a < 1.0: self.attributes("-alpha", a + 0.05); self.after(20, self.fade_in)

    def animate_elements(self):
        if not self.animating: return
        self.phase += 0.12 # Smoother phase progression
        for i, rect in enumerate(self.bars):
            dist = abs(i - len(self.bars)/2) / (len(self.bars)/2)
            att = math.cos(dist * math.pi / 2)
            # Increased animation height for larger resolution
            h = (math.sin(self.phase + i * 0.3) * 75 + 85) * att
            try:
                # Update lines coords (x1, y1, x2, y2)
                cx = self.canvas.coords(rect)[0]
                self.canvas.coords(rect, cx, 100 - h/2, cx, 100 + h/2)
                self.canvas.coords(self.glows[i][0], cx, 100 - h/2 - 2, cx, 100 + h/2 + 2)
                self.canvas.coords(self.glows[i][1], cx, 100 - h/2 - 5, cx, 100 + h/2 + 5)
            except: pass

        target_w = 600 * self.progress_val
        curr_w = self.prog_canvas.coords(self.prog_fill)[2]
        self.prog_canvas.coords(self.prog_fill, 0, 0, curr_w + (target_w - curr_w) * 0.1, 4)
        self.after(30, self.animate_elements)

    def start_bootstrap(self):
        threading.Thread(target=self.run_update, daemon=True).start()

    def fade_out(self):
        # We don't fade out anymore to avoid the black gap. We pass the screen state to the main app cross-fade!
        self.quit()

    def run_update(self):
        try:
            self.progress_val = 0.2
            dev_file = os.path.join(get_base_path(), "organizar_musicas.py")
            
            if os.path.exists(dev_file) or getattr(sys, 'frozen', False):
                self.progress_val = 0.3
                self.lbl_status.configure(text="ALLOCATING MEMORY...")
                import time; time.sleep(0.4)
                
                self.progress_val = 0.5
                self.lbl_status.configure(text="LOADING NEURAL MODELS...")
                # SILENT HEAVY PRE-CACHE DURING SPLASH
                import google.generativeai
                import customtkinter
                import mutagen
                
                self.progress_val = 0.7
                self.lbl_status.configure(text="CALIBRATING AUDIO TENSORS...")
                time.sleep(0.4)
                
                self.progress_val = 0.95
                self.lbl_status.configure(text="SECURING ENCRYPTION...")
                time.sleep(0.3)
            else:
                # 1. Checar versão remota
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
            time.sleep(0.5)
            self.animating = False
            self.fade_out()
        except Exception as e:
            print(f"Update failed: {e}")
            self.fade_out()

def main():
    app = NeuralSplash()
    app.mainloop()
    # Keep the window fully visible and alive to mask the desktop during massive imports
    dev_file = os.path.join(get_base_path(), "organizar_musicas.py")
    target_path = dev_file if os.path.exists(dev_file) else LOCAL_CORE

    if os.path.exists(target_path):
        import sys
        sys._splash_window = app
        import mutagen, shutil, queue, json, runpy, re
        import google.generativeai, dotenv
        runpy.run_path(target_path, run_name="__main__")

if __name__ == "__main__":
    main()

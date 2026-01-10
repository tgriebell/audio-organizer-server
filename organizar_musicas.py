import os
import shutil
import re
import time
import sys
import threading
import random
import ctypes
import math
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from mutagen import File as MutagenFile

# Tenta carregar Pygame para evitar erros se não houver áudio
HAS_PYGAME = False
try:
    import pygame
    pygame.mixer.init()
    HAS_PYGAME = True
except: pass

# ==============================================================================
# ENGINE DE SISTEMA (WIN32 TASKBAR HACK & RESOURCES)
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

# ==============================================================================
# DESIGN SYSTEM (PREMIUM NEURAL)
# ==============================================================================
COLOR_BG = "#050505"
COLOR_SIDEBAR = "#0a0a0a"
COLOR_CARD = "#0d0d0d"
COLOR_ACCENT = "#00ff66"
COLOR_BORDER = "#1a1a1a"
COLOR_STATUS = "#aaaaaa"

# ==============================================================================
# CONFIGURAÇÃO DE PASTAS E REGRAS
# ==============================================================================
PASTA_ENTRADA = "_ENTRADA_DE_MUSICAS"

REGRAS_PALAVRAS = {
    "01_Alta_Energia_Impacto_Esportes_Carros_Acao": ["powerful", "exciting", "rock", "metal", "sport", "action", "extreme", "energy", "stomp", "drums"],
    "02_Cinematic_Emocao_Filmes_Documentarios_Drama": ["cinematic", "epic", "dramatic", "score", "trailer", "orchestra", "emotional", "documentary"],
    "03_Good_Vibes_Lifestyle_Vlog_Viagem_Comercial": ["uplifting", "happy", "carefree", "pop", "indie", "good vibes", "summer", "beach", "travel", "lifestyle", "commercial"],
    "04_Lounge_Tech_Background_Fundo_Neutro_Lofi": ["peaceful", "ambient", "lounge", "lofi", "chill", "atmosphere", "background", "calm", "relax"],
    "05_Vinhetas_Logos_Sonoros_Abaixo_30s": ["logo", "ident", "sting", "bumper", "jingle", "intro", "reveal", "vinheta"],
    "06_Casamentos_Cerimonias": ["wedding", "casamento", "bride", "noiva", "ceremony", "romantic", "love"],
    "07_Hits_Brasileiros_Copyright_Cuidado": ["sertanejo", "pagode", "funk brasil", "mpb", "jorge", "mateus"],
    "09_Corporate_Business_Tecnologia": ["corporate", "business", "tech", "technology", "innovation", "success"],
    "10_Suspense_Terror_Dark": ["dark", "scary", "tension", "horror", "terror", "suspense", "mystery"],
    "11_Comedy_Fun_Quirky": ["funny", "comedy", "quirky", "humor", "cartoon", "animation", "sneaky"],
    "12_Urban_Trap_HipHop_Modern": ["hip hop", "rap", "trap", "drill", "beat", "urban", "street", "bass", "808"],
    "13_Acoustic_Folk_Rustico": ["acoustic", "folk", "country", "roots", "guitar", "rustic", "nature"],
    "14_World_Music_Cultural_Regional": ["latin", "salsa", "asian", "african", "reggae", "world", "culture"],
    "15_Holiday_Sazonal_Natal_Feriados": ["christmas", "xmas", "holiday", "santa", "halloween"],
    "16_Kids_Infantil_Games_Escola": ["kids", "children", "game", "8bit", "arcade", "cute"],
    "17_Vocals_Cancoes_Com_Letra": ["lyrical", "vocal", "singer", "lyrics", "song", "voice"],
    "18_Jazz_Blues_Classy_Sophisticated": ["jazz", "blues", "saxophone", "swing", "classy"],
    "19_Electronic_Dance_Club_House_Techno": ["edm", "house", "techno", "dubstep", "party", "dance"],
    "20_Experimental_Abstract_SoundDesign": ["experimental", "abstract", "sound design", "glitch", "texture"]
}

ARTISTAS_CONHECIDOS = {
    "alexgrohl": "01_Alta_Energia_Impacto_Esportes_Carros_Acao",
    "glories": "01_Alta_Energia_Impacto_Esportes_Carros_Acao",
    "alon ohana": "02_Cinematic_Emocao_Filmes_Documentarios_Drama",
    "kyle preston": "02_Cinematic_Emocao_Filmes_Documentarios_Drama",
    "yehezkel raz": "02_Cinematic_Emocao_Filmes_Documentarios_Drama",
    "rex banner": "03_Good_Vibes_Lifestyle_Vlog_Viagem_Comercial",
    "ben fox": "03_Good_Vibes_Lifestyle_Vlog_Viagem_Comercial",
}

# ==============================================================================
# UI COMPONENTS
# ==============================================================================

class Toast(ctk.CTkFrame):
    def __init__(self, master, message, color=COLOR_ACCENT):
        super().__init__(master, fg_color="#000", border_width=1, border_color=color, corner_radius=15)
        ctk.CTkLabel(self, text=f"  ⚡ {message}  ", font=("Segoe UI", 13, "bold"), text_color="white").pack(padx=25, pady=15)
        self.place(relx=0.5, rely=0.1, anchor="center")
        master.after(3500, self.destroy)

class NeuralCard(ctk.CTkFrame):
    def __init__(self, master, file_path, on_select):
        super().__init__(master, fg_color=COLOR_CARD, corner_radius=18, border_width=1, border_color=COLOR_BORDER)
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        self.grid_columnconfigure(1, weight=1)
        
        self.icon = ctk.CTkLabel(self, text="◈", font=("Arial", 24), text_color=COLOR_ACCENT)
        self.icon.grid(row=0, column=0, rowspan=2, padx=(25, 20), pady=25)
        
        self.name_lbl = ctk.CTkLabel(self, text=self.filename[:60], font=("Segoe UI", 15, "bold"), text_color="white")
        self.name_lbl.grid(row=0, column=1, sticky="w", pady=(20, 0))
        
        self.info_lbl = ctk.CTkLabel(self, text="NEURAL OBJECT SCANNED // READY FOR DEPLOYMENT", font=("Consolas", 10), text_color="#555")
        self.info_lbl.grid(row=1, column=1, sticky="w", pady=(0, 20))

        for w in [self, self.icon, self.name_lbl, self.info_lbl]:
            w.bind("<Enter>", lambda e: self.on_hover(True))
            w.bind("<Leave>", lambda e: self.on_hover(False))

    def on_hover(self, hover):
        if hover:
            self.configure(border_color=COLOR_ACCENT, fg_color="#111")
            self.icon.configure(text_color="white")
        else:
            self.configure(border_color=COLOR_BORDER, fg_color=COLOR_CARD)
            self.icon.configure(text_color=COLOR_ACCENT)

# ==============================================================================
# SPLASH SCREEN CLASS (INTEGRADA)
# ==============================================================================

class NeuralSplash(ctk.CTk):
    def __init__(self, on_finish):
        super().__init__()
        self.on_finish = on_finish
        self.overrideredirect(True)
        self.configure(fg_color=COLOR_BG)
        
        w, h = 600, 480
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f'{w}x{h}+{int((sw-w)/2)}+{int((sh-h)/2)}')

        self.main_frame = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0, border_width=1, border_color="#1a1a1a")
        self.main_frame.pack(fill="both", expand=True)

        self.bg_canvas = tk.Canvas(self.main_frame, width=600, height=480, bg=COLOR_BG, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0)
        self.draw_radial_gradient()

        self.canvas = tk.Canvas(self.main_frame, height=140, bg=COLOR_BG, highlightthickness=0)
        self.canvas.place(x=0, y=50, width=600)
        
        self.bars = []; self.glows = []
        num_bars, bar_w, gap = 28, 4, 6
        total_w = (num_bars * bar_w) + ((num_bars - 1) * gap)
        start_x = (600 - total_w) / 2 
        
        for i in range(num_bars):
            x0 = start_x + i * (bar_w + gap)
            glow = self.canvas.create_rectangle(x0-2, 70, x0+bar_w+2, 70, fill="#00441a", outline="")
            rect = self.canvas.create_rectangle(x0, 70, x0+bar_w, 70, fill=COLOR_ACCENT, outline="")
            self.bars.append(rect); self.glows.append(glow)

        self.title_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.title_container.place(relx=0.5, rely=0.58, anchor="center")
        ctk.CTkLabel(self.title_container, text="AUDIO", font=("Segoe UI Light", 42), text_color="white").pack(side="left")
        ctk.CTkLabel(self.title_container, text=" ORGANIZER", font=("Segoe UI", 42, "bold"), text_color="white").pack(side="left")

        self.lbl_author = ctk.CTkLabel(self.main_frame, text="by Thiago Griebel • TODOS OS DIREITOS RESERVADOS", font=("Segoe UI", 8, "bold"), text_color="#444")
        self.lbl_author.place(relx=0.5, rely=0.66, anchor="center")
        
        self.lbl_sub = ctk.CTkLabel(self.main_frame, text="NEURAL ENGINE EDITION v2.9", font=("Consolas", 10, "bold"), text_color=COLOR_ACCENT)
        self.lbl_sub.place(relx=0.5, rely=0.73, anchor="center")

        self.lbl_status = ctk.CTkLabel(self.main_frame, text="INITIALIZING NEURAL SYSTEMS...", font=("Consolas", 9), text_color=COLOR_STATUS)
        self.lbl_status.place(relx=0.5, rely=0.84, anchor="center")

        self.prog_canvas = tk.Canvas(self.main_frame, width=400, height=10, bg=COLOR_BG, highlightthickness=0)
        self.prog_canvas.place(relx=0.5, rely=0.92, anchor="center")
        self.prog_bg = self.prog_canvas.create_rectangle(0, 4, 400, 7, fill="#1a1a1a", outline="")
        self.prog_fill = self.prog_canvas.create_rectangle(0, 4, 0, 7, fill=COLOR_ACCENT, outline="")
        self.prog_glow = self.prog_canvas.create_oval(-5, 0, 5, 10, fill="white", outline="")

        self.animating = True; self.phase = 0; self.pulse_val = 0; self.pulse_dir = 1; self.progress_val = 0
        self.animate_elements()
        self.start_boot()

    def draw_radial_gradient(self):
        for i in range(100):
            r = 600 - (i * 4)
            if r < 0: break
            color = f"#{max(5, 12-i//8):02x}{max(5, 12-i//8):02x}{max(5, 12-i//8):02x}"
            self.bg_canvas.create_oval(300-r, 240-r, 300+r, 240+r, fill=color, outline="")

    def animate_elements(self):
        if not self.animating: return
        self.phase += 0.15
        for i, rect in enumerate(self.bars):
            dist = abs(i - len(self.bars)/2) / (len(self.bars)/2)
            att = math.cos(dist * math.pi / 2)
            h = (math.sin(self.phase + i * 0.3) * 40 + 50) * att
            x0, _, x1, _ = self.canvas.coords(rect)
            self.canvas.coords(rect, x0, 70 - h/2, x1, 70 + h/2)
            self.canvas.coords(self.glows[i], x0-2, 70 - h/2 - 2, x1+2, 70 + h/2 + 2)

        self.pulse_val += 0.04 * self.pulse_dir
        if self.pulse_val >= 1.0: self.pulse_dir = -1
        elif self.pulse_val <= 0.4: self.pulse_dir = 1
        gray_val = int(170 * self.pulse_val)
        self.lbl_status.configure(text_color=f"#{gray_val:02x}{gray_val:02x}{gray_val:02x}")

        target_w = 400 * self.progress_val
        c_coords = self.prog_canvas.coords(self.prog_fill)
        new_w = c_coords[2] + (target_w - c_coords[2]) * 0.1
        self.prog_canvas.coords(self.prog_fill, 0, 4, new_w, 7)
        self.prog_canvas.coords(self.prog_glow, new_w-5, 0, new_w+5, 10)
        self.after(30, self.animate_elements)

    def start_boot(self):
        def run():
            steps = ["LOADING NEURAL ALGORITHMS...", "SCANNING DIRECTORIES...", "CONFIGURING UI...", "SYSTEM READY"]
            for i, s in enumerate(steps):
                self.lbl_status.configure(text=s)
                self.progress_val = (i+1)/len(steps)
                time.sleep(0.6)
            self.animating = False
            self.after(200, self.finish)
        threading.Thread(target=run, daemon=True).start()

    def finish(self):
        self.destroy()
        self.on_finish()

# ==============================================================================
# MAIN APPLICATION CLASS
# ==============================================================================

class AudioOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes("-alpha", 0.0)
        
        w, h = 1350, 850
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{int((sw-w)/2)}+{int((sh-h)/2)}")
        self.configure(fg_color=COLOR_BG)
        self.setup_ui()
        self.fade_in()
        
        self.current_root = ""
        self.file_cards = []

    def fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1.0:
            self.attributes("-alpha", alpha + 0.08); self.after(15, self.fade_in)

    def setup_ui(self):
        # Top Bar
        self.bar = ctk.CTkFrame(self, fg_color="#000", height=60, corner_radius=0)
        self.bar.pack(fill="x")
        self.bar.bind("<Button-1>", self.start_move)
        self.bar.bind("<B1-Motion>", self.do_move)
        ctk.CTkLabel(self.bar, text="  ◈  AUDIO ORGANIZER PRO  //  NEURAL ENGINE v2.9", font=("Consolas", 11, "bold"), text_color="#444").pack(side="left", padx=25)
        ctk.CTkButton(self.bar, text="✕", width=60, height=60, fg_color="transparent", hover_color="#c42b1c", corner_radius=0, command=self.destroy).pack(side="right")

        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=25, pady=25)

        # Sidebar
        self.side = ctk.CTkFrame(self.body, fg_color=COLOR_SIDEBAR, width=280, corner_radius=30, border_width=1, border_color="#151515")
        self.side.pack(side="left", fill="y", padx=(0, 25))
        self.side.pack_propagate(False)
        
        self.logo_frame = ctk.CTkFrame(self.side, fg_color="transparent")
        self.logo_frame.pack(pady=50)
        ctk.CTkLabel(self.logo_frame, text="AUDIO", font=("Segoe UI Light", 28), text_color="white").pack(side="left")
        ctk.CTkLabel(self.logo_frame, text="PRO", font=("Segoe UI", 28, "bold"), text_color=COLOR_ACCENT).pack(side="left")

        self.add_nav("NEURAL ORCHESTRATOR", "⚡", active=True)
        self.add_nav("AI CLASSIFIER", "🧠")
        self.add_nav("DEPLOYMENT LOGS", "↺")

        # Content Area
        self.cont = ctk.CTkFrame(self.body, fg_color="transparent")
        self.cont.pack(side="left", fill="both", expand=True)
        
        self.header = ctk.CTkFrame(self.cont, fg_color="transparent")
        self.header.pack(fill="x", pady=(10, 40))
        
        self.title_box = ctk.CTkFrame(self.header, fg_color="transparent")
        self.title_box.pack(side="left")
        ctk.CTkLabel(self.title_box, text="Neural Library", font=("Segoe UI Light", 42), text_color="white").pack(side="left")
        ctk.CTkLabel(self.title_box, text=" SCANS", font=("Segoe UI", 42, "bold"), text_color="white").pack(side="left")
        
        ctk.CTkButton(self.header, text="+ INITIALIZE DIRECTORY", fg_color=COLOR_ACCENT, text_color="black", font=("Segoe UI", 13, "bold"), height=50, corner_radius=15, command=self.select_folder).pack(side="right")

        self.scroll = ctk.CTkScrollableFrame(self.cont, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)

        self.act = ctk.CTkFrame(self, fg_color="#050505", height=140, border_width=1, border_color="#111")
        self.act.pack(fill="x")
        self.btn_run = ctk.CTkButton(self.act, text="DEPLOY NEURAL ORGANIZATION", font=("Segoe UI", 18, "bold"), fg_color=COLOR_ACCENT, text_color="black", height=75, width=600, corner_radius=20, command=self.run_neural_process)
        self.btn_run.place(relx=0.5, rely=0.5, anchor="center")

    def add_nav(self, text, icon, active=False):
        color = "#555" if not active else "white"
        bg_color = "#111" if active else "transparent"
        btn = ctk.CTkButton(self.side, text=f"  {icon}   {text}", font=("Segoe UI", 14, "bold" if active else "normal"), fg_color=bg_color, text_color=color, anchor="w", height=60, corner_radius=18)
        btn.pack(fill="x", padx=25, pady=6)

    def start_move(self, e): self.x, self.y = e.x, e.y
    def do_move(self, e): self.geometry(f"+{self.winfo_x() + (e.x - self.x)}+{self.winfo_y() + (e.y - self.y)}")

    def select_folder(self):
        p = filedialog.askdirectory()
        if p:
            self.current_root = p
            entrada_path = os.path.join(p, PASTA_ENTRADA)
            if not os.path.exists(entrada_path):
                os.makedirs(entrada_path)
                Toast(self, "Folder _ENTRADA_DE_MUSICAS created!")
            
            for w in self.scroll.winfo_children(): w.destroy()
            self.file_cards = []
            all_files = []
            # Busca Recursiva em Subpastas
            for root, dirs, files in os.walk(entrada_path):
                for f in files:
                    if f.lower().endswith(('.mp3', '.wav', '.flac', '.aiff')):
                        full_p = os.path.join(root, f)
                        rel_p = os.path.relpath(full_p, entrada_path)
                        all_files.append((full_p, rel_p))
            
            for f_path, rel_p in all_files:
                card = NeuralCard(self.scroll, f_path, lambda c: None)
                if rel_p != os.path.basename(f_path):
                    card.info_lbl.configure(text=f"NEURAL OBJECT DETECTED IN: ...\\{os.path.dirname(rel_p)}")
                card.pack(fill="x", pady=10, padx=15)
                self.file_cards.append(card)
            Toast(self, f"{len(all_files)} Neural Audio Objects detected.")

    def run_neural_process(self):
        if not self.file_cards:
            Toast(self, "No files found!", color="#ff3333"); return
        
        self.btn_run.configure(state="disabled", text="AI NEURAL ENGINE PROCESSING...")
        
        for pasta in REGRAS_PALAVRAS.keys():
            p_dest = os.path.join(self.current_root, pasta)
            if not os.path.exists(p_dest): os.makedirs(p_dest)
        p_08 = os.path.join(self.current_root, "08_Outros_Nao_Classificados")
        if not os.path.exists(p_08): os.makedirs(p_08)

        def work():
            moved = 0
            for card in self.file_cards:
                origem = card.file_path
                filename = card.filename
                texto_analise = filename.lower()
                try:
                    audio = MutagenFile(origem, easy=True)
                    if audio:
                        if 'artist' in audio: texto_analise += " " + audio['artist'][0].lower()
                        if 'genre' in audio: texto_analise += " " + audio['genre'][0].lower()
                except: pass

                destino = "08_Outros_Nao_Classificados"
                for artista, pasta in ARTISTAS_CONHECIDOS.items():
                    if artista in texto_analise: destino = pasta; break
                
                if destino == "08_Outros_Nao_Classificados":
                    for pasta, keywords in REGRAS_PALAVRAS.items():
                        if any(k in texto_analise for k in keywords): destino = pasta; break
                
                dest_final_path = os.path.join(self.current_root, destino, filename)
                try:
                    if HAS_PYGAME: pygame.mixer.music.unload()
                    shutil.move(origem, dest_final_path)
                    moved += 1
                except: pass
            
            self.after(0, lambda: self.finish_process(moved))
        threading.Thread(target=work, daemon=True).start()

    def finish_process(self, count):
        self.btn_run.configure(state="normal", text="DEPLOY NEURAL ORGANIZATION")
        Toast(self, f"NEURAL SYNC COMPLETE: {count} OBJECTS ORGANIZED")
        for w in self.scroll.winfo_children(): w.destroy()
        self.file_cards = []

def start_main():
    app = AudioOrganizerApp()
    app.mainloop()

if __name__ == "__main__":
    splash = NeuralSplash(on_finish=start_main)
    splash.mainloop()
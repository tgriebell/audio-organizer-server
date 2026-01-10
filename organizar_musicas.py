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

# ==============================================================================
# ENGINE DE SISTEMA (PATH RESOLUTION)
# ==============================================================================
try:
    myappid = 'tgriebell.audioorganizer.neural.v2.9'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except: pass

def get_base_path():
    # Retorna o diretório onde o EXE ou o Script está localizado
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

# ==============================================================================
# DESIGN SYSTEM (NEURAL GRADIENT VIBE)
# ==============================================================================
COLOR_BG_DARK = "#01040a"
COLOR_NEON_BLUE = "#00ccff"
COLOR_ACCENT = "#00ff66"     # Verde Neon
COLOR_SIDEBAR = "#050a15"
COLOR_CARD = "#081020"
COLOR_BORDER = "#102540"
COLOR_STATUS = "#8899aa"

# ==============================================================================
# CONFIGURAÇÃO DE REGRAS
# ==============================================================================
PASTA_ENTRADA_NOME = "_ENTRADA_DE_MUSICAS"

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
    def __init__(self, master, file_path, rel_path):
        super().__init__(master, fg_color=COLOR_CARD, corner_radius=15, border_width=1, border_color=COLOR_BORDER)
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        self.grid_columnconfigure(1, weight=1)
        
        self.icon = ctk.CTkLabel(self, text="◈", font=("Arial", 22), text_color=COLOR_NEON_BLUE)
        self.icon.grid(row=0, column=0, rowspan=2, padx=(20, 15), pady=20)
        
        self.name_lbl = ctk.CTkLabel(self, text=self.filename[:65], font=("Segoe UI", 14, "bold"), text_color="white")
        self.name_lbl.grid(row=0, column=1, sticky="w", pady=(15, 0))
        
        sub_info = f"SOURCE: ...\\{os.path.dirname(rel_path)}" if os.path.dirname(rel_path) else "SOURCE: ROOT"
        self.info_lbl = ctk.CTkLabel(self, text=f"NEURAL OBJECT // {sub_info}", font=("Consolas", 9), text_color=COLOR_STATUS)
        self.info_lbl.grid(row=1, column=1, sticky="w", pady=(0, 15))

        self.bind("<Enter>", lambda e: self.configure(border_color=COLOR_ACCENT, fg_color="#0c1830"))
        self.bind("<Leave>", lambda e: self.configure(border_color=COLOR_BORDER, fg_color=COLOR_CARD))

# ==============================================================================
# SPLASH SCREEN (NEON GRADIENT ALIVE)
# ==============================================================================

class NeuralSplash(ctk.CTk):
    def __init__(self, on_finish):
        super().__init__()
        self.on_finish = on_finish
        self.overrideredirect(True)
        self.configure(fg_color=COLOR_BG_DARK)
        
        w, h = 600, 480
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f'{w}x{h}+{int((sw-w)/2)}+{int((sh-h)/2)}')

        # Fundo Degradê Neon
        self.canvas_bg = tk.Canvas(self, width=600, height=480, bg=COLOR_BG_DARK, highlightthickness=0)
        self.canvas_bg.pack(fill="both", expand=True)
        self.draw_neon_gradient()

        # Waveform Absolute Center
        self.wave_canvas = tk.Canvas(self, height=120, bg=COLOR_BG_DARK, highlightthickness=0)
        self.wave_canvas.place(relx=0.5, y=140, anchor="center", width=500)
        
        self.bars = []; self.glows = []
        num_bars, bar_w, gap = 30, 4, 6
        start_x = (500 - (num_bars * (bar_w + gap))) / 2
        
        for i in range(num_bars):
            x0 = start_x + i * (bar_w + gap)
            glow = self.wave_canvas.create_rectangle(x0-1, 60, x0+bar_w+1, 60, fill="#003322", outline="")
            rect = self.wave_canvas.create_rectangle(x0, 60, x0+bar_w, 60, fill=COLOR_ACCENT, outline="")
            self.bars.append(rect); self.glows.append(glow)

        self.lbl_title = ctk.CTkFrame(self, fg_color="transparent")
        self.lbl_title.place(relx=0.5, y=240, anchor="center")
        ctk.CTkLabel(self.lbl_title, text="AUDIO", font=("Segoe UI Light", 40), text_color="white").pack(side="left")
        ctk.CTkLabel(self.lbl_title, text=" ORGANIZER", font=("Segoe UI", 40, "bold"), text_color="white").pack(side="left")

        ctk.CTkLabel(self, text="by Thiago Griebel • TODOS OS DIREITOS RESERVADOS", font=("Segoe UI", 9, "bold"), text_color=COLOR_NEON_BLUE).place(relx=0.5, y=285, anchor="center")
        
        self.lbl_status = ctk.CTkLabel(self, text="NEURAL BOOTING...", font=("Consolas", 10), text_color=COLOR_STATUS)
        self.lbl_status.place(relx=0.5, y=380, anchor="center")

        self.animating = True; self.phase = 0
        self.animate_elements()
        self.start_boot()

    def draw_neon_gradient(self):
        # Simula degradê neon suave
        for i in range(480):
            r = int(1 + (4 * i/480))
            g = int(8 + (22 * i/480))
            b = int(22 - (8 * i/480))
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas_bg.create_line(0, i, 600, i, fill=color)

    def animate_elements(self):
        if not self.animating: return
        self.phase += 0.15
        for i, rect in enumerate(self.bars):
            dist = abs(i - len(self.bars)/2) / (len(self.bars)/2)
            att = math.cos(dist * math.pi / 2)
            h = (math.sin(self.phase + i * 0.3) * 45 + 50) * att
            try:
                self.wave_canvas.coords(rect, self.wave_canvas.coords(rect)[0], 60 - h/2, self.wave_canvas.coords(rect)[2], 60 + h/2)
                self.wave_canvas.coords(self.glows[i], self.wave_canvas.coords(rect)[0]-2, 60 - h/2 - 2, self.wave_canvas.coords(rect)[2]+2, 60 + h/2 + 2)
            except: pass
        self.after(30, self.animate_elements)

    def start_boot(self):
        def run():
            time.sleep(1.8)
            self.animating = False; self.after(200, self.finish)
        threading.Thread(target=run, daemon=True).start()

    def finish(self):
        self.destroy(); self.on_finish()

# ==============================================================================
# MAIN APP
# ==============================================================================

class AudioOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes("-alpha", 0.0)
        
        w, h = 1300, 820
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{int((sw-w)/2)}+{int((sh-h)/2)}")
        self.configure(fg_color=COLOR_BG_DARK)
        self.setup_ui()
        self.fade_in()
        
        self.current_root = get_base_path() # Fixa na pasta do EXE
        self.file_cards = []
        
        # Auto-Scan Inicial na inicialização
        self.after(800, self.auto_initialize)

    def fade_in(self):
        a = self.attributes("-alpha")
        if a < 1.0: self.attributes("-alpha", a + 0.1); self.after(20, self.fade_in)

    def setup_ui(self):
        # Top Bar
        self.top = ctk.CTkFrame(self, fg_color=COLOR_SIDEBAR, height=70, corner_radius=0)
        self.top.pack(fill="x")
        self.top.bind("<Button-1>", self.start_move)
        self.top.bind("<B1-Motion>", self.do_move)
        ctk.CTkLabel(self.top, text="  ◈  AUDIO ORGANIZER PRO  //  NEURAL ENGINE v2.9", font=("Consolas", 11, "bold"), text_color=COLOR_NEON_BLUE).pack(side="left", padx=30)
        ctk.CTkButton(self.top, text="✕", width=70, height=70, fg_color="transparent", hover_color="#c42b1c", corner_radius=0, command=self.destroy).pack(side="right")

        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=30, pady=30)

        # Sidebar (Results Panel)
        self.side = ctk.CTkFrame(self.body, fg_color=COLOR_SIDEBAR, width=320, corner_radius=25, border_width=1, border_color=COLOR_BORDER)
        self.side.pack(side="left", fill="y", padx=(0, 30))
        self.side.pack_propagate(False)
        
        ctk.CTkLabel(self.side, text="AUDIO", font=("Segoe UI Light", 28), text_color="white").pack(pady=(50, 0))
        ctk.CTkLabel(self.side, text="ORGANIZER", font=("Segoe UI", 28, "bold"), text_color=COLOR_ACCENT).pack()

        # Result Section
        self.res_frame = ctk.CTkFrame(self.side, fg_color="#08101a", corner_radius=20, border_width=1, border_color="#102035")
        self.res_frame.pack(fill="both", expand=True, padx=25, pady=(40, 25))
        
        ctk.CTkLabel(self.res_frame, text="NEURAL RESULTS", font=("Consolas", 11, "bold"), text_color=COLOR_NEON_BLUE).pack(pady=(20, 10))
        self.res_info = ctk.CTkLabel(self.res_frame, text="SYSTEM STANDBY", font=("Segoe UI", 13, "bold"), text_color="#445566")
        self.res_info.pack(pady=15)
        
        self.res_stats = ctk.CTkLabel(self.res_frame, text="Objects: 0\nStatus: Waiting...", font=("Consolas", 10), text_color="#334455", justify="left")
        self.res_stats.pack(pady=10)

        # Content
        self.cont = ctk.CTkFrame(self.body, fg_color="transparent")
        self.cont.pack(side="left", fill="both", expand=True)
        
        self.head = ctk.CTkFrame(self.cont, fg_color="transparent")
        self.head.pack(fill="x", pady=(0, 40))
        ctk.CTkLabel(self.head, text="Neural Library Scan", font=("Segoe UI Light", 38), text_color="white").pack(side="left")
        ctk.CTkButton(self.head, text="REFRESH SCAN", fg_color="#152035", text_color="white", font=("Segoe UI", 12), height=45, corner_radius=12, command=self.scan_source).pack(side="right")

        self.scroll = ctk.CTkScrollableFrame(self.cont, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)

        # Footer
        self.footer = ctk.CTkFrame(self, fg_color=COLOR_SIDEBAR, height=140, border_width=1, border_color=COLOR_BORDER)
        self.footer.pack(fill="x")
        self.btn_run = ctk.CTkButton(self.footer, text="DEPLOY NEURAL ORGANIZATION", font=("Segoe UI", 20, "bold"), fg_color=COLOR_ACCENT, text_color="black", height=80, width=650, corner_radius=25, command=self.run_process)
        self.btn_run.place(relx=0.5, rely=0.5, anchor="center")

    def start_move(self, e): self.x, self.y = e.x, e.y
    def do_move(self, e): self.geometry(f"+{self.winfo_x() + (e.x - self.x)}+{self.winfo_y() + (e.y - self.y)}")

    def auto_initialize(self):
        # Garante que a pasta de entrada exista no local do EXE
        entrada = os.path.join(self.current_root, PASTA_ENTRADA_NOME)
        if not os.path.exists(entrada): os.makedirs(entrada)
        self.scan_source()

    def scan_source(self):
        entrada = os.path.join(self.current_root, PASTA_ENTRADA_NOME)
        for w in self.scroll.winfo_children(): w.destroy()
        self.file_cards = []
        found = []
        
        # Scan apenas na pasta _ENTRADA_DE_MUSICAS do EXE
        if os.path.exists(entrada):
            for root, _, files in os.walk(entrada):
                for f in files:
                    if f.lower().endswith(('.mp3', '.wav', '.flac', '.aiff')):
                        f_full = os.path.join(root, f)
                        f_rel = os.path.relpath(f_full, entrada)
                        found.append((f_full, f_rel))
        
        for f_p, r_p in found:
            card = NeuralCard(self.scroll, f_p, r_p)
            card.pack(fill="x", pady=8, padx=15)
            self.file_cards.append(card)
        
        self.res_info.configure(text="OBJECTS READY", text_color=COLOR_NEON_BLUE)
        self.res_stats.configure(text=f"Objects: {len(found)}\nStatus: Scanned", text_color="#8899aa")

    def run_process(self):
        if not self.file_cards: return
        self.btn_run.configure(state="disabled", text="DEPLOYING...")
        
        # Cria as pastas apenas se não existirem (exist_ok=True)
        for pasta in REGRAS_PALAVRAS.keys():
            os.makedirs(os.path.join(self.current_root, pasta), exist_ok=True)
        os.makedirs(os.path.join(self.current_root, "08_Outros_Nao_Classificados"), exist_ok=True)

        def work():
            count = 0
            for card in self.file_cards:
                orig, name = card.file_path, card.filename
                text = name.lower()
                try:
                    audio = MutagenFile(orig, easy=True)
                    if audio:
                        if 'artist' in audio: text += " " + audio['artist'][0].lower()
                        if 'genre' in audio: text += " " + audio['genre'][0].lower()
                except: pass

                dest = "08_Outros_Nao_Classificados"
                for pasta, keywords in REGRAS_PALAVRAS.items():
                    if any(k in text for k in keywords):
                        dest = pasta; break
                
                try:
                    # Move para a pasta de categoria na RAIZ do executável
                    shutil.move(orig, os.path.join(self.current_root, dest, name))
                    count += 1
                except: pass
            self.after(0, lambda: self.done(count))
        threading.Thread(target=work, daemon=True).start()

    def done(self, c):
        self.btn_run.configure(state="normal", text="DEPLOY NEURAL ORGANIZATION")
        self.res_info.configure(text="DEPLOY SUCCESS", text_color=COLOR_ACCENT)
        self.res_stats.configure(text=f"Processed: {c}\nStatus: SYNCED", text_color=COLOR_ACCENT)
        Toast(self, f"SUCCESS: {c} OBJECTS SYNCED")
        for w in self.scroll.winfo_children(): w.destroy()
        self.file_cards = []

if __name__ == "__main__":
    NeuralSplash(on_finish=lambda: AudioOrganizerApp().mainloop()).mainloop()

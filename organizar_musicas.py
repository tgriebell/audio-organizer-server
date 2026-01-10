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
# ENGINE DE SISTEMA
# ==============================================================================
try:
    myappid = 'tgriebell.audioorganizer.neural.v2.9'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except: pass

# ==============================================================================
# DESIGN SYSTEM (CYBER NEON BLUE & GREEN)
# ==============================================================================
COLOR_BG = "#02040a"        # Azul Marinho Profundo
COLOR_SIDEBAR = "#050a15"    # Azul Escuro
COLOR_CARD = "#081020"       # Azul Deck
COLOR_ACCENT = "#00ff66"     # Verde Neon
COLOR_NEON_BLUE = "#0066ff"  # Azul Neon
COLOR_BORDER = "#102040"
COLOR_STATUS = "#8899aa"

# ==============================================================================
# CONFIGURAÇÃO DE REGRAS
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
        
        sub_info = f"IN: ...\\{os.path.dirname(rel_path)}" if os.path.dirname(rel_path) else "ROOT DIRECTORY"
        self.info_lbl = ctk.CTkLabel(self, text=f"NEURAL OBJECT // {sub_info}", font=("Consolas", 9), text_color=COLOR_STATUS)
        self.info_lbl.grid(row=1, column=1, sticky="w", pady=(0, 15))

        self.bind("<Enter>", lambda e: self.configure(border_color=COLOR_ACCENT, fg_color="#0c1830"))
        self.bind("<Leave>", lambda e: self.configure(border_color=COLOR_BORDER, fg_color=COLOR_CARD))

# ==============================================================================
# SPLASH SCREEN (FIXED ALIGNMENT)
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

        # Layout Centralizado
        self.main_frame = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0, border_width=1, border_color=COLOR_NEON_BLUE)
        self.main_frame.pack(fill="both", expand=True)

        # Waveform Canvas - Centralização Absoluta
        self.canvas = tk.Canvas(self.main_frame, height=120, bg=COLOR_BG, highlightthickness=0)
        self.canvas.place(relx=0.5, y=140, anchor="center", width=500)
        
        self.bars = []; self.glows = []
        num_bars, bar_w, gap = 30, 4, 6
        total_w = (num_bars * bar_w) + ((num_bars - 1) * gap)
        start_x = (500 - total_w) / 2
        
        for i in range(num_bars):
            x0 = start_x + i * (bar_w + gap)
            glow = self.canvas.create_rectangle(x0-1, 60, x0+bar_w+1, 60, fill="#003322", outline="")
            rect = self.canvas.create_rectangle(x0, 60, x0+bar_w, 60, fill=COLOR_ACCENT, outline="")
            self.bars.append(rect); self.glows.append(glow)

        # Título - Ajustado para ficar logo abaixo da onda
        self.lbl_title = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.lbl_title.place(relx=0.5, y=240, anchor="center")
        ctk.CTkLabel(self.lbl_title, text="AUDIO", font=("Segoe UI Light", 40), text_color="white").pack(side="left")
        ctk.CTkLabel(self.lbl_title, text=" ORGANIZER", font=("Segoe UI", 40, "bold"), text_color="white").pack(side="left")

        ctk.CTkLabel(self.main_frame, text="by Thiago Griebel • TODOS OS DIREITOS RESERVADOS", font=("Segoe UI", 9, "bold"), text_color=COLOR_NEON_BLUE).place(relx=0.5, y=285, anchor="center")
        
        self.lbl_sub = ctk.CTkLabel(self.main_frame, text="NEURAL ENGINE EDITION v2.9", font=("Consolas", 11, "bold"), text_color=COLOR_ACCENT)
        self.lbl_sub.place(relx=0.5, y=320, anchor="center")

        self.lbl_status = ctk.CTkLabel(self.main_frame, text="READY TO SCAN", font=("Consolas", 10), text_color=COLOR_STATUS)
        self.lbl_status.place(relx=0.5, y=380, anchor="center")

        self.prog_canvas = tk.Canvas(self.main_frame, width=350, height=4, bg="#0a1530", highlightthickness=0)
        self.prog_canvas.place(relx=0.5, y=420, anchor="center")
        self.prog_fill = self.prog_canvas.create_rectangle(0, 0, 0, 4, fill=COLOR_ACCENT, outline="")

        self.animating = True; self.phase = 0; self.progress_val = 0
        self.animate_elements()
        self.start_boot()

    def animate_elements(self):
        if not self.animating: return
        self.phase += 0.15
        for i, rect in enumerate(self.bars):
            dist = abs(i - len(self.bars)/2) / (len(self.bars)/2)
            att = math.cos(dist * math.pi / 2)
            h = (math.sin(self.phase + i * 0.3) * 45 + 50) * att
            self.canvas.coords(rect, self.canvas.coords(rect)[0], 60 - h/2, self.canvas.coords(rect)[2], 60 + h/2)
            self.canvas.coords(self.glows[i], self.canvas.coords(rect)[0]-2, 60 - h/2 - 2, self.canvas.coords(rect)[2]+2, 60 + h/2 + 2)

        target_w = 350 * self.progress_val
        curr_w = self.prog_canvas.coords(self.prog_fill)[2]
        self.prog_canvas.coords(self.prog_fill, 0, 0, curr_w + (target_w - curr_w) * 0.1, 4)
        self.after(30, self.animate_elements)

    def start_boot(self):
        def run():
            msgs = ["CORE INITIALIZATION...", "NEURAL MAPPING...", "UI SYNC...", "SYSTEM ONLINE"]
            for i, m in enumerate(msgs):
                self.lbl_status.configure(text=m)
                self.progress_val = (i+1)/len(msgs)
                time.sleep(0.7)
            self.animating = False; self.after(300, self.finish)
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
        self.configure(fg_color=COLOR_BG)
        self.setup_ui()
        self.fade_in()
        
        self.current_root = ""
        self.file_cards = []

    def fade_in(self):
        a = self.attributes("-alpha")
        if a < 1.0: self.attributes("-alpha", a + 0.1); self.after(20, self.fade_in)

    def setup_ui(self):
        # Header Pro
        self.top = ctk.CTkFrame(self, fg_color=COLOR_SIDEBAR, height=70, corner_radius=0)
        self.top.pack(fill="x")
        self.top.bind("<Button-1>", self.start_move)
        self.top.bind("<B1-Motion>", self.do_move)
        
        ctk.CTkLabel(self.top, text="  ◈  AUDIO ORGANIZER NEURAL v2.9", font=("Consolas", 12, "bold"), text_color=COLOR_NEON_BLUE).pack(side="left", padx=30)
        ctk.CTkButton(self.top, text="✕", width=70, height=70, fg_color="transparent", hover_color="#c42b1c", corner_radius=0, command=self.destroy).pack(side="right")

        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=30, pady=30)

        # Sidebar Simplificada
        self.side = ctk.CTkFrame(self.body, fg_color=COLOR_SIDEBAR, width=280, corner_radius=25, border_width=1, border_color=COLOR_BORDER)
        self.side.pack(side="left", fill="y", padx=(0, 30))
        self.side.pack_propagate(False)
        
        ctk.CTkLabel(self.side, text="AUDIO", font=("Segoe UI Light", 32), text_color="white").pack(pady=(60, 0))
        ctk.CTkLabel(self.side, text="ORGANIZER", font=("Segoe UI", 24, "bold"), text_color=COLOR_ACCENT).pack()
        
        ctk.CTkLabel(self.side, text="SYSTEM STATUS: ONLINE", font=("Consolas", 10), text_color="#334466").pack(side="bottom", pady=40)

        # Content
        self.cont = ctk.CTkFrame(self.body, fg_color="transparent")
        self.cont.pack(side="left", fill="both", expand=True)
        
        self.head = ctk.CTkFrame(self.cont, fg_color="transparent")
        self.head.pack(fill="x", pady=(0, 40))
        ctk.CTkLabel(self.head, text="Neural Scanning Library", font=("Segoe UI Light", 38), text_color="white").pack(side="left")
        
        self.btn_sel = ctk.CTkButton(self.head, text="+ SELECT ROOT FOLDER", fg_color=COLOR_ACCENT, text_color="black", font=("Segoe UI", 14, "bold"), height=55, corner_radius=15, command=self.select_folder)
        self.btn_sel.pack(side="right")

        self.scroll = ctk.CTkScrollableFrame(self.cont, fg_color="transparent", scrollbar_button_color=COLOR_BORDER)
        self.scroll.pack(fill="both", expand=True)

        # Footer Action
        self.footer = ctk.CTkFrame(self, fg_color=COLOR_SIDEBAR, height=130, border_width=1, border_color=COLOR_BORDER)
        self.footer.pack(fill="x")
        self.btn_run = ctk.CTkButton(self.footer, text="INITIALIZE NEURAL ORGANIZATION", font=("Segoe UI", 20, "bold"), fg_color=COLOR_ACCENT, text_color="black", height=75, width=650, corner_radius=20, command=self.run_process)
        self.btn_run.place(relx=0.5, rely=0.5, anchor="center")

    def start_move(self, e): self.x, self.y = e.x, e.y
    def do_move(self, e): self.geometry(f"+{self.winfo_x() + (e.x - self.x)}+{self.winfo_y() + (e.y - self.y)}")

    def select_folder(self):
        p = filedialog.askdirectory()
        if not p: return
        self.current_root = p
        entrada = os.path.join(p, PASTA_ENTRADA)
        if not os.path.exists(entrada):
            os.makedirs(entrada); Toast(self, "Created _ENTRADA_DE_MUSICAS")
        
        for w in self.scroll.winfo_children(): w.destroy()
        self.file_cards = []
        found = []
        
        # SCAN RECURSIVO ABSOLUTO
        for root, _, files in os.walk(p): # Escaneia a partir da RAIZ selecionada
            for f in files:
                if f.lower().endswith(('.mp3', '.wav', '.flac', '.aiff')):
                    f_full = os.path.join(root, f)
                    f_rel = os.path.relpath(f_full, p)
                    found.append((f_full, f_rel))
        
        for f_p, r_p in found:
            card = NeuralCard(self.scroll, f_p, r_p)
            card.pack(fill="x", pady=8, padx=15)
            self.file_cards.append(card)
        
        Toast(self, f"NEURAL SCAN: {len(found)} OBJECTS LOCATED")

    def run_process(self):
        if not self.file_cards: Toast(self, "NO OBJECTS TO ORGANIZE", "#ff3333"); return
        self.btn_run.configure(state="disabled", text="PROCESSING NEURAL MAPPING...")
        
        # Create categories
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
                    shutil.move(orig, os.path.join(self.current_root, dest, name))
                    count += 1
                except: pass
            self.after(0, lambda: self.done(count))
        threading.Thread(target=work, daemon=True).start()

    def done(self, c):
        self.btn_run.configure(state="normal", text="INITIALIZE NEURAL ORGANIZATION")
        Toast(self, f"SUCCESS: {c} OBJECTS REDEPLOYED")
        for w in self.scroll.winfo_children(): w.destroy()
        self.file_cards = []

if __name__ == "__main__":
    NeuralSplash(on_finish=lambda: AudioOrganizerApp().mainloop()).mainloop()

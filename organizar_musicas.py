import os
import shutil
import re
import time
import sys
import threading
import random
import ctypes
import math
import customtkinter as ctk
from tkinter import filedialog, messagebox
from mutagen import File as MutagenFile

# Tenta carregar Pygame
HAS_PYGAME = False
try:
    import pygame
    pygame.mixer.init()
    HAS_PYGAME = True
except: pass

# ==============================================================================
# DESIGN SYSTEM (PREMIUM NEURAL)
# ==============================================================================
COLOR_BG = "#0a0a0a"
COLOR_SIDEBAR = "#121212"
COLOR_CARD = "#181818"
COLOR_ACCENT = "#00ff66"
COLOR_BORDER = "#222222"

# ==============================================================================
# CONFIGURAÇÃO DE PASTAS E REGRAS (EXATO WORKFLOW SOLICITADO)
# ==============================================================================
PASTA_ENTRADA = "_ENTRADA_DE_MUSICAS"

# Mapeamento Completo das 20 Pastas Profissionais
ARTISTAS_CONHECIDOS = {
    "alexgrohl": "01_Alta_Energia_Impacto_Esportes_Carros_Acao",
    "glories": "01_Alta_Energia_Impacto_Esportes_Carros_Acao",
    "stomp": "01_Alta_Energia_Impacto_Esportes_Carros_Acao",
    "alon ohana": "02_Cinematic_Emocao_Filmes_Documentarios_Drama",
    "kyle preston": "02_Cinematic_Emocao_Filmes_Documentarios_Drama",
    "yehezkel raz": "02_Cinematic_Emocao_Filmes_Documentarios_Drama",
    "rex banner": "03_Good_Vibes_Lifestyle_Vlog_Viagem_Comercial",
    "ben fox": "03_Good_Vibes_Lifestyle_Vlog_Viagem_Comercial",
    "osker wyld": "04_Lounge_Tech_Background_Fundo_Neutro_Lofi",
    "jorge & mateus": "07_Hits_Brasileiros_Copyright_Cuidado",
}

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
        super().__init__(master, fg_color="#111", border_width=1, border_color=color, corner_radius=10)
        ctk.CTkLabel(self, text=f"  {message}  ", font=("Segoe UI", 12, "bold"), text_color="white").pack(padx=20, pady=10)
        self.place(relx=0.5, rely=0.1, anchor="center")
        master.after(3500, self.destroy)

class NeuralCard(ctk.CTkFrame):
    def __init__(self, master, file_path, on_select):
        super().__init__(master, fg_color=COLOR_CARD, corner_radius=15, border_width=1, border_color=COLOR_BORDER)
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        self.grid_columnconfigure(1, weight=1)
        
        self.icon = ctk.CTkLabel(self, text="⚡", font=("Arial", 20), text_color=COLOR_ACCENT)
        self.icon.grid(row=0, column=0, rowspan=2, padx=20, pady=20)
        
        self.name_lbl = ctk.CTkLabel(self, text=self.filename[:50], font=("Segoe UI", 14, "bold"), text_color="white")
        self.name_lbl.grid(row=0, column=1, sticky="w", pady=(15, 0))
        
        self.info_lbl = ctk.CTkLabel(self, text="AWAITING NEURAL CLASSIFICATION", font=("Consolas", 10), text_color="#444")
        self.info_lbl.grid(row=1, column=1, sticky="w", pady=(0, 15))

        for w in [self, self.icon, self.name_lbl, self.info_lbl]:
            w.bind("<Enter>", lambda e: self.configure(border_color=COLOR_ACCENT, fg_color="#222"))
            w.bind("<Leave>", lambda e: self.configure(border_color=COLOR_BORDER, fg_color=COLOR_CARD))
            w.bind("<Button-1>", lambda e: on_select(self))

class AudioOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes("-alpha", 0.0)
        
        w, h = 1350, 850
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{int((sw-w)/2)}+{int((sh-h)/2)}")
        self.configure(fg_color=COLOR_BG)

        self.after(100, self.apply_hack)
        self.setup_ui()
        self.fade_in()
        
        self.current_root = ""
        self.file_cards = []
        self.history = []

    def apply_hack(self):
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
            self.attributes("-alpha", alpha + 0.1); self.after(20, self.fade_in)

    def setup_ui(self):
        # Top Bar
        self.bar = ctk.CTkFrame(self, fg_color="#000", height=50, corner_radius=0)
        self.bar.pack(fill="x")
        self.bar.bind("<Button-1>", self.start_move)
        self.bar.bind("<B1-Motion>", self.do_move)
        
        ctk.CTkLabel(self.bar, text="  AUDIO ORGANIZER PRO • NEURAL ENGINE v2.9", font=("Consolas", 10), text_color="#333").pack(side="left", padx=20)
        ctk.CTkButton(self.bar, text="✕", width=50, height=50, fg_color="transparent", hover_color="#c42b1c", command=self.destroy).pack(side="right")

        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=15, pady=15)

        # Sidebar
        self.side = ctk.CTkFrame(self.body, fg_color=COLOR_SIDEBAR, width=260, corner_radius=25, border_width=1, border_color="#1a1a1a")
        self.side.pack(side="left", fill="y", padx=(0, 15))
        self.side.pack_propagate(False)
        ctk.CTkLabel(self.side, text="SYSTEM NAVIGATION", font=("Segoe UI", 11, "bold"), text_color="#222").pack(pady=45)
        self.add_nav("ORGANIZE", "⚡", active=True)
        self.add_nav("AI ENGINE", "🧠")
        self.add_nav("HISTORY", "↺")

        # Content Area
        self.cont = ctk.CTkFrame(self.body, fg_color="transparent")
        self.cont.pack(side="left", fill="both", expand=True)
        self.header = ctk.CTkFrame(self.cont, fg_color="transparent")
        self.header.pack(fill="x", pady=(10, 30))
        ctk.CTkLabel(self.header, text="Neural Library", font=("Segoe UI", 36, "bold"), text_color="white").pack(side="left")
        ctk.CTkButton(self.header, text="+ SELECT APP FOLDER", fg_color=COLOR_ACCENT, text_color="black", font=("Segoe UI", 12, "bold"), height=45, corner_radius=12, command=self.select_folder).pack(side="right")

        self.scroll = ctk.CTkScrollableFrame(self.cont, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)

        # Action Bar
        self.act = ctk.CTkFrame(self, fg_color="#080808", height=120, border_width=1, border_color="#151515")
        self.act.pack(fill="x")
        self.btn_run = ctk.CTkButton(self.act, text="DEPLOY NEURAL ORGANIZATION", font=("Segoe UI", 16, "bold"), fg_color=COLOR_ACCENT, text_color="black", height=65, width=500, corner_radius=18, command=self.run_neural_process)
        self.btn_run.place(relx=0.5, rely=0.5, anchor="center")

    def add_nav(self, text, icon, active=False):
        color = "#888" if not active else "white"
        btn = ctk.CTkButton(self.side, text=f"  {icon}   {text}", font=("Segoe UI", 14), fg_color="transparent", text_color=color, anchor="w", height=55, corner_radius=15, hover_color="#1a1a1a")
        btn.pack(fill="x", padx=20, pady=8)

    def start_move(self, e): self.x, self.y = e.x, e.y
    def do_move(self, e): self.geometry(f"+{self.winfo_x() + (e.x - self.x)}+{self.winfo_y() + (e.y - self.y)}")

    def select_folder(self):
        # O usuário seleciona a pasta onde está o EXE e a pasta _ENTRADA_DE_MUSICAS
        p = filedialog.askdirectory()
        if p:
            self.current_root = p
            entrada_path = os.path.join(p, PASTA_ENTRADA)
            
            # Se não existir a pasta de entrada, cria uma para o usuário
            if not os.path.exists(entrada_path):
                os.makedirs(entrada_path)
                Toast(self, "Folder _ENTRADA_DE_MUSICAS created!")
            
            # Carregar arquivos da entrada
            for w in self.scroll.winfo_children(): w.destroy()
            self.file_cards = []
            
            all_files = []
            for root, dirs, files in os.walk(entrada_path):
                for f in files:
                    if f.lower().endswith(('.mp3', '.wav', '.flac', '.aiff')):
                        all_files.append(os.path.join(root, f))
            
            for f_path in all_files:
                card = NeuralCard(self.scroll, f_path, lambda c: None)
                card.pack(fill="x", pady=10, padx=15)
                self.file_cards.append(card)
            
            Toast(self, f"{len(all_files)} Neural Audio Objects detected.")

    def run_neural_process(self):
        if not self.file_cards:
            Toast(self, "No files found in _ENTRADA_DE_MUSICAS!", color="#ff3333"); return
        
        self.btn_run.configure(state="disabled", text="AI NEURAL ENGINE PROCESSING...")
        
        # 1. Garantir que as 20 pastas existam antes de começar
        for pasta in REGRAS_PALAVRAS.keys():
            p_dest = os.path.join(self.current_root, pasta)
            if not os.path.exists(p_dest): os.makedirs(p_dest)
        
        # Pasta de fallback 08
        p_08 = os.path.join(self.current_root, "08_Outros_Nao_Classificados")
        if not os.path.exists(p_08): os.makedirs(p_08)

        def work():
            moved = 0
            self.history = []
            for card in self.file_cards:
                origem = card.file_path
                filename = card.filename
                texto_analise = filename.lower()
                
                # Metadados
                try:
                    audio = MutagenFile(origem, easy=True)
                    if audio:
                        if 'artist' in audio: texto_analise += " " + audio['artist'][0].lower()
                        if 'genre' in audio: texto_analise += " " + audio['genre'][0].lower()
                except: pass

                # Lógica Neural de Classificação
                destino = "08_Outros_Nao_Classificados"
                
                # 1. Check Artistas
                for artista, pasta in ARTISTAS_CONHECIDOS.items():
                    if artista in texto_analise:
                        destino = pasta; break
                
                # 2. Check Palavras (20 categorias)
                if destino == "08_Outros_Nao_Classificados":
                    for pasta, keywords in REGRAS_PALAVRAS.items():
                        if any(k in texto_analise for k in keywords):
                            destino = pasta; break
                
                # 3. Lógica Especial Artlist
                if "artlist musical logos" in texto_analise:
                    destino = "05_Vinhetas_Logos_Sonoros_Abaixo_30s"

                dest_final_path = os.path.join(self.current_root, destino, filename)
                
                try:
                    if HAS_PYGAME: pygame.mixer.music.unload()
                    shutil.move(origem, dest_final_path)
                    self.history.append((dest_final_path, origem))
                    moved += 1
                except Exception as e:
                    print(f"Error moving {filename}: {e}")
            
            self.after(0, lambda: self.finish_process(moved))

        threading.Thread(target=work, daemon=True).start()

    def finish_process(self, count):
        self.btn_run.configure(state="normal", text="DEPLOY NEURAL ORGANIZATION")
        Toast(self, f"NEURAL SYNC COMPLETE: {count} OBJECTS ORGANIZED")
        for w in self.scroll.winfo_children(): w.destroy()
        self.file_cards = []

if __name__ == "__main__":
    app = AudioOrganizerApp()
    app.mainloop()

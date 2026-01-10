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
from mutagen import File as MutagenFile

# ==============================================================================
# ENGINE DE SISTEMA (PATH RESOLUTION)
# ==============================================================================
try:
    myappid = 'tgriebell.audioorganizer.neural.v2.9'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except: pass

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

# ==============================================================================
# DESIGN SYSTEM
# ==============================================================================
COLOR_BG = "#05070a"
COLOR_ACCENT = "#00ff66"
COLOR_NEON_BLUE = "#00ccff"
COLOR_TEXT_DIM = "#445566"
COLOR_CONSOLE_BG = "#020408"

PASTA_ENTRADA_NOME = "_ENTRADA_DE_MUSICAS"

# ==============================================================================
# SUPER NEURAL BRAIN (20 PASTAS)
# ==============================================================================
NEURAL_BRAIN = {
    "01_Alta_Energia_Impacto_Esportes_Carros_Acao": ["powerful", "exciting", "rock", "metal", "sport", "action", "extreme", "energy", "stomp", "drums", "driving", "aggressive", "hard", "pumping", "claps", "fast", "impact", "stadium", "power", "zac nelson", "viking", "energy", "pumping"],
    "02_Cinematic_Emocao_Filmes_Documentarios_Drama": ["cinematic", "epic", "dramatic", "score", "trailer", "orchestra", "emotional", "documentary", "sweeping", "heroic", "majestic", "story", "memories", "letter", "depth", "ethereal", "grand", "inspiration", "nidred", "guiding", "atmospheric", "hopeful", "oliver michael", "john isaac"],
    "03_Good_Vibes_Lifestyle_Vlog_Viagem_Comercial": ["uplifting", "happy", "carefree", "pop", "indie", "good vibes", "summer", "beach", "travel", "lifestyle", "commercial", "bright", "optimistic", "vlog", "joy", "look", "me", "sun", "fun", "positive", "ian post", "seth parson", "slpstrm"],
    "04_Lounge_Tech_Background_Fundo_Neutro_Lofi": ["peaceful", "ambient", "lounge", "lofi", "chill", "atmosphere", "background", "calm", "relax", "mellow", "smooth", "minimalist", "subtle", "dreamy", "floating", "morkovkasound", "opaline", "horizons", "chillout", "lo-fi", "evgeny bardyuzha"],
    "05_Vinhetas_Logos_Sonoros_Abaixo_30s": ["logo", "ident", "sting", "bumper", "jingle", "intro", "reveal", "vinheta", "transition", "short", "outro", "sfx", "0-30", "teaser", "loop", "ident", "ma ", "audiojungle"],
    "06_Casamentos_Cerimonias": ["wedding", "casamento", "bride", "noiva", "ceremony", "romantic", "love", "piano", "sweet", "strings", "eternity", "pure", "holy", "sentimental", "proposal", "marriage", "celestial"],
    "07_Hits_Brasileiros_Copyright_Cuidado": ["sertanejo", "pagode", "funk brasil", "mpb", "jorge", "mateus", "brazilian", "samba", "piseiro", "forro", "carnaval", "brasil", "bebe", "情熱"],
    "08_Fashion_Style_Beauty_Luxury": ["fashion", "style", "beauty", "luxury", "elegant", "chic", "catwalk", "model", "stylish", "vogue", "glamour", "high-end", "aesthetic", "trend", "boutique", "runway", "classy"],
    "09_Corporate_Business_Tecnologia": ["corporate", "business", "tech", "technology", "innovation", "success", "professional", "motivational", "modern", "clean", "startup", "productive", "presentation", "nobou", "machine", "echoes", "industrial", "rex banner", "confident", "business guitar"],
    "10_Suspense_Terror_Dark": ["dark", "scary", "tension", "horror", "terror", "suspense", "mystery", "creepy", "fear", "ghost", "thriller", "ominous", "eerie", "haunting", "shadows", "nightmare", "gothic"],
    "11_Comedy_Fun_Quirky": ["funny", "comedy", "quirky", "humor", "cartoon", "animation", "sneaky", "pizzicato", "silly", "playful", "bouncy", "clown", "mischievous"],
    "12_Urban_Trap_HipHop_Modern": ["hip hop", "rap", "trap", "drill", "beat", "urban", "street", "bass", "808", "gangsta", "swagger", "rnb", "city", "modern beat", "lo-fi beat", "curtis cole"],
    "13_Acoustic_Folk_Rustico": ["acoustic", "folk", "country", "roots", "guitar", "rustic", "nature", "organic", "unplugged", "earthy", "mountains", "campfire", "banjo", "the gray havens"],
    "14_World_Music_Cultural_Regional": ["latin", "salsa", "asian", "african", "reggae", "world", "culture", "tribal", "ethnic", "oriental", "exotic", "reggaeton", "indian", "arabic"],
    "15_Holiday_Sazonal_Natal_Feriados": ["christmas", "xmas", "holiday", "santa", "halloween", "seasonal", "jingle bells", "winter", "easter", "spooky", "icel."],
    "16_Kids_Infantil_Games_Escola": ["kids", "children", "game", "8bit", "arcade", "preschool", "cute", "nursery", "tiny", "preschool", "educational"],
    "17_Vocals_Cancoes_Com_Letra": ["lyrical", "vocal", "singer", "lyrics", "song", "voice", "female", "male", "chorus", "harmony", "shouts", "featuring", "moon ft"],
    "18_Jazz_Blues_Classy_Sophisticated": ["jazz", "blues", "saxophone", "swing", "classy", "trumpet", "cocktail", "upscale", "sophisticated", "elegant", "bossa", "smooth jazz", "stanley gurvich"],
    "19_Electronic_Dance_Club_House_Techno": ["edm", "house", "techno", "dubstep", "party", "dance", "club", "rave", "trance", "synthwave", "future", "digital", "electro", "red city hero"],
    "20_Experimental_Abstract_SoundDesign": ["experimental", "abstract", "sound design", "glitch", "texture", "noise", "creative", "unusual", "artistic", "avante-garde", "minimal"]
}

# ==============================================================================
# UI COMPONENTS
# ==============================================================================

class NeuralOrb(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=COLOR_BG, highlightthickness=0, **kwargs)
        self.phase = 0; self.state = "idle" 
        self.animate()

    def animate(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 10: w, h = 300, 300
        cx, cy = w/2, h/2
        self.phase += 0.05
        pulse = (math.sin(self.phase) * 8) + 65
        color = COLOR_NEON_BLUE if self.state == "idle" else COLOR_ACCENT
        if self.state == "success": color = "#fff"
        for i in range(6):
            size = pulse + (i * 12)
            opacity_color = self.lerp_color(COLOR_BG, color, (6-i)/15)
            self.create_oval(cx-size, cy-size, cx+size, cy+size, outline=opacity_color, width=2)
        self.create_oval(cx-pulse, cy-pulse, cx+pulse, cy+pulse, outline=color, width=3)
        if self.state == "busy":
            for i in range(12):
                ang = self.phase*2.5 + (i * (math.pi*2/12))
                px = cx + math.cos(ang) * (pulse + 25); py = cy + math.sin(ang) * (pulse + 25)
                self.create_oval(px-3, py-3, px+3, py+3, fill=COLOR_ACCENT, outline="")
        self.after(30, self.animate)

    def lerp_color(self, c1, c2, t):
        def parse(c): return [int(c[i:i+2], 16) for i in (1, 3, 5)]
        rgb1, rgb2 = parse(c1), parse(c2)
        res = [int(rgb1[i] + (rgb2[i]-rgb1[i])*t) for i in range(3)]
        return f"#{res[0]:02x}{res[1]:02x}{res[2]:02x}"

class NeuralHubApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes("-alpha", 0.0)
        w, h = 900, 750
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{int((sw-w)/2)}+{int((sh-h)/2)}")
        self.configure(fg_color=COLOR_BG)
        self.base_path = get_base_path()
        self.input_folder = os.path.join(self.base_path, PASTA_ENTRADA_NOME)
        self.found_files = []
        self.setup_ui()
        self.fade_in()
        self.after(800, self.auto_scan)

    def fade_in(self):
        a = self.attributes("-alpha")
        if a < 1.0: self.attributes("-alpha", a + 0.1); self.after(20, self.fade_in)

    def setup_ui(self):
        self.header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        self.header.pack(fill="x", padx=20, pady=5)
        self.header.bind("<Button-1>", self.start_move)
        self.header.bind("<B1-Motion>", self.do_move)
        ctk.CTkLabel(self.header, text="NEURAL HUB ENGINE v3.1 // ACTIVE", font=("Consolas", 10, "bold"), text_color=COLOR_TEXT_DIM).pack(side="left")
        ctk.CTkButton(self.header, text="✕", width=40, height=40, fg_color="transparent", hover_color="#c42b1c", command=self.destroy).pack(side="right")

        self.hub_area = ctk.CTkFrame(self, fg_color="transparent")
        self.hub_area.pack(fill="both", expand=True)
        self.orb = NeuralOrb(self.hub_area, width=400, height=350)
        self.orb.pack(pady=(10, 0))
        self.lbl_main = ctk.CTkLabel(self.hub_area, text="SCANNING...", font=("Segoe UI Light", 32), text_color="white")
        self.lbl_main.pack(pady=5)
        self.lbl_sub = ctk.CTkLabel(self.hub_area, text="Awaiting neural objects", font=("Consolas", 12), text_color=COLOR_NEON_BLUE)
        self.lbl_sub.pack()
        
        self.progress_bar = ctk.CTkProgressBar(self.hub_area, width=400, height=2, fg_color="#0a1a30", progress_color=COLOR_ACCENT)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=20)

        self.btn_action = ctk.CTkButton(self.hub_area, text="INITIALIZE NEURAL DEPLOYMENT", font=("Segoe UI", 16, "bold"), fg_color="transparent", border_width=2, border_color=COLOR_NEON_BLUE, text_color=COLOR_NEON_BLUE, height=65, width=350, corner_radius=32, command=self.run_process)
        self.btn_action.pack(pady=(10, 30))

        self.console_frame = ctk.CTkFrame(self, fg_color=COLOR_CONSOLE_BG, height=180, corner_radius=0, border_width=1, border_color="#0a1a30")
        self.console_frame.pack(fill="x")
        self.console_frame.pack_propagate(False)
        self.console_text = ctk.CTkTextbox(self.console_frame, fg_color="transparent", font=("Consolas", 11), text_color=COLOR_ACCENT, activate_scrollbars=False)
        self.console_text.pack(fill="both", expand=True, padx=25, pady=15)

    def log_console(self, msg, type="INFO"):
        prefix = {
            "INFO": "[SYSTEM::LOG]",
            "SUCCESS": "[CORE::SUCCESS]",
            "MOVE": "[NEURAL::MOVE]",
            "WAIT": "[SYSTEM::SCAN]"
        }.get(type, "[LOG]")
        self.console_text.insert("end", f"{prefix} {msg}\n"); self.console_text.see("end")

    def start_move(self, e): self.x, self.y = e.x, e.y
    def do_move(self, e): self.geometry(f"+{self.winfo_x() + (e.x - self.x)}+{self.winfo_y() + (e.y - self.y)}")

    def auto_scan(self):
        if not os.path.exists(self.input_folder): os.makedirs(self.input_folder)
        found = []
        for root, _, files in os.walk(self.input_folder):
            for f in files:
                if f.lower().endswith((".mp3", ".wav", ".flac", ".aiff")):
                    found.append(os.path.join(root, f))
        self.found_files = found
        self.lbl_main.configure(text=f"{len(found)} OBJECTS DETECTED")
        self.lbl_sub.configure(text=f"Neural sorting ready for Thiago Griebel")
        self.log_console(f"Scan complete: {len(found)} objects located.", "WAIT")

    def run_process(self):
        if not self.found_files: return
        self.orb.state = "busy"; self.btn_action.configure(state="disabled", text="DEPLOYING...")
        self.progress_bar.set(0)
        
        def work():
            for pasta in NEURAL_BRAIN.keys():
                os.makedirs(os.path.join(self.base_path, pasta), exist_ok=True)
            
            total = len(self.found_files)
            count = 0
            for i, orig_path in enumerate(self.found_files):
                name = os.path.basename(orig_path)
                # NORMALIZAÇÃO HIPERINTELIGENTE
                text_analise = name.lower()
                text_analise = re.sub(r'[_.\-()\[\]]', ' ', text_analise)
                
                try:
                    audio = MutagenFile(orig_path, easy=True)
                    if audio:
                        for key in ['artist', 'genre', 'comment', 'title', 'album']:
                            if key in audio: 
                                metadata_text = " ".join(audio[key]).lower()
                                text_analise += " " + re.sub(r'[_.\-()\[\]]', ' ', metadata_text)
                except: pass
                
                scores = {cat: 0 for cat in NEURAL_BRAIN.keys()}
                for cat, keywords in NEURAL_BRAIN.items():
                    for word in keywords:
                        if f" {word} " in f" {text_analise} ":
                            scores[cat] += 2
                        elif word in text_analise:
                            scores[cat] += 1
                            
                best_cat = max(scores, key=scores.get) if max(scores.values()) > 0 else None
                if best_cat:
                    try:
                        shutil.move(orig_path, os.path.join(self.base_path, best_cat, name))
                        self.after(0, lambda n=name, c=best_cat: self.log_console(f"{n[:25]}... >> [{c[:12]}]", "MOVE"))
                        count += 1
                    except: pass
                else:
                    self.after(0, lambda n=name: self.log_console(f"{n[:25]}... No neural match.", "INFO"))
                
                # ATUALIZA PROGRESSO
                progress = (i + 1) / total
                self.after(0, lambda p=progress: self.progress_bar.set(p))
                time.sleep(0.04)

            self.after(0, lambda c=count: self.finish(c))
        threading.Thread(target=work, daemon=True).start()

    def finish(self, count):
        self.orb.state = "success"; self.btn_action.configure(state="normal", text="SYSTEM SYNCED", fg_color=COLOR_ACCENT, text_color="black")
        self.lbl_main.configure(text="CORE STABILITY REACHED")
        self.lbl_sub.configure(text=f"{count} Neural objects optimized", text_color=COLOR_ACCENT)
        self.log_console(f"Deployment complete. {count} objects synchronized.", "SUCCESS")

if __name__ == "__main__":
    NeuralHubApp().mainloop()

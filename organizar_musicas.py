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
import queue
import json
import google.generativeai as genai
from dotenv import load_dotenv

# ==============================================================================
# ENGINE DE SISTEMA (WIN32 TASKBAR & ICON HACK)
# ==============================================================================
def set_app_icon(window, icon_path):
    try:
        if sys.platform == "win32":
            hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
            icon_flags = 1 
            hicon = ctypes.windll.user32.LoadImageW(0, icon_path, 1, 0, 0, 0x00000010 | 0x00008000)
            ctypes.windll.user32.SendMessageW(hwnd, 0x0080, icon_flags, hicon)
    except Exception as e:
        print(f"Icon loader error: {e}")

try:
    myappid = 'tgriebell.audioorganizer.neural.v4.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except: pass

def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def log_debug(msg):
    pass

def get_real_run_path():
    # Returns where the .exe is running from, used for the IN/OUT folders!
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

# ==============================================================================
# DESIGN SYSTEM
# ==============================================================================
COLOR_BG = "#03080a" # Mais denso, quase onix escuro
COLOR_ACCENT = "#05d590" # Verde tech sofisticado (Deep Tech Green)
COLOR_NEON_BLUE = "#048a60" # Verde secundário mais profundo
COLOR_TEXT_DIM = "#446655" # Verde-acinzentado sutil
COLOR_CONSOLE_BG = "#010304"

PASTA_ENTRADA_NOME = "_ENTRADA_DE_MUSICAS"

# ==============================================================================
# SUPER NEURAL BRAIN (20 PASTAS)
# ==============================================================================
DEFAULT_NEURAL_BRAIN = {
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

categorias_path = os.path.join(get_base_path(), "categorias.json")
if not os.path.exists(categorias_path):
    try:
        with open(categorias_path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_NEURAL_BRAIN, f, indent=4, ensure_ascii=False)
        NEURAL_BRAIN = DEFAULT_NEURAL_BRAIN.copy()
    except Exception as e:
        print(f"Erro ao salvar categorias.json: {e}")
        NEURAL_BRAIN = DEFAULT_NEURAL_BRAIN.copy()
else:
    try:
        with open(categorias_path, "r", encoding="utf-8") as f:
            NEURAL_BRAIN = json.load(f)
    except Exception as e:
        print(f"Erro ao ler categorias.json: {e}")
        NEURAL_BRAIN = DEFAULT_NEURAL_BRAIN.copy()

# ==============================================================================
# AI GEMINI BATCH CLASSIFICATOR
# ==============================================================================
# CONFIGURAR CHAVE EXTERNA (Seguranca contra vazamentos no Github)
def load_api_key():
    import dotenv
    env_path = os.path.join(get_base_path(), ".env")
    if os.path.exists(env_path):
        dotenv.load_dotenv(env_path)
        key = os.getenv("GEMINI_API_KEY")
        if key: return key.strip()
    return None

GEMINI_API_KEY = load_api_key()

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
    except Exception as e:
        print("Erro ao configurar Gemini:", e)
        gemini_model = None
else:
    gemini_model = None

def get_gemini_batch_classification(tracks_data_list, categorias_dict):
    """ Envia um Lote de N músicas para a IA e retorna um DICIONARIO com as respostas """
    if not gemini_model: return None
    
    cats_str = "\n".join([f"- {k}" for k in categorias_dict.keys()])
    
    prompt = f"""Você é um classificador musical de alta precisão. Sua tarefa é analisar a lista de músicas abaixo, o nome do artista, título e o nome do arquivo, e mapeá-las para a categoria mais apropriada com base na 'vibe'/estilo musical inferido.

Categorias válidas permitidas (escolha apenas UMA para cada música, sendo a chave exata):
{cats_str}

Aqui estão as músicas para classificar:
"""
    log_debug("--- [AI BATCH PROCESSING INICIADO] ---")
    log_debug(f"Prompt base configurado. Total musicas: {len(tracks_data_list)}")
    
    for track in tracks_data_list:
        prompt += f"ID: {track['id']} | Arquivo: {track['file']} | Metadados: {track['meta']}\n"
    
    prompt += """
Responda APENAS com um objeto JSON puro, onde as chaves são os IDs das músicas que te passei e os valores são as categorias escolhidas que pertencem EXATAMENTE à lista que forneci acima. Se não tiver certeza de qual é, defina como null.
Exemplo:
{"1": "02_Cinematic_Emocao_Filmes_Documentarios_Drama", "2": "12_Urban_Trap_HipHop_Modern"}
"""
    log_debug(f"Prompt completo gerado com {len(prompt)} caracteres. Enviando para Google Gemini API...")

    try:
        response = gemini_model.generate_content(prompt)
        log_debug(f"SUCESSO: Resposta bruta do Gemini recebida:\n{response.text}")
        text = response.text.replace('```json', '').replace('```', '').strip()
        result = json.loads(text)
        log_debug(f"JSON Parse com sucesso: {result}")
        return result
    except Exception as e:
        log_debug(f"ERRO CRITICO (Gemini API Falhou): {str(e)}")
        return None

# ==============================================================================
# UI COMPONENTS
# ==============================================================================

class NeuralOrb(tk.Canvas):
    def __init__(self, master, scale=1.0, **kwargs):
        super().__init__(master, bg=COLOR_BG, highlightthickness=0, **kwargs)
        self.phase = 0; self.state = "idle" 
        self.scale = scale
        self.animate()

    def animate(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 10: w, h = int(300*self.scale), int(300*self.scale)
        cx, cy = w/2, h/2
        self.phase += 0.05
        
        pulse = (math.sin(self.phase) * 8 * self.scale) + (65 * self.scale)
        color = COLOR_NEON_BLUE if self.state == "idle" else COLOR_ACCENT
        if self.state == "success": color = "#ffffff"

        # Radial Deep Glow
        r1 = 200 * self.scale
        r2 = 120 * self.scale
        self.create_oval(cx-r1, cy-r1, cx+r1, cy+r1, fill="#040b14", outline="")
        self.create_oval(cx-r2, cy-r2, cx+r2, cy+r2, fill="#071324", outline="")
        
        for i in range(6):
            size = pulse + (i * 12 * self.scale)
            opacity_color = self.lerp_color("#071324", color, (6-i)/15)
            self.create_oval(cx-size, cy-size, cx+size, cy+size, outline=opacity_color, width=max(1, int(2*self.scale)))
        
        self.create_oval(cx-pulse, cy-pulse, cx+pulse, cy+pulse, outline=color, width=max(1, int(3*self.scale)))

        if self.state in ["busy", "success"]:
            num_dots = 12 if self.state == "busy" else 8
            speed = 2.5 if self.state == "busy" else 1.2
            dot_color = COLOR_ACCENT if self.state == "busy" else COLOR_NEON_BLUE
            
            for i in range(num_dots):
                ang = self.phase * speed + (i * (math.pi * 2 / num_dots))
                dist = pulse + (25 * self.scale) if self.state == "busy" else pulse + (40 * self.scale)
                px = cx + math.cos(ang) * dist; py = cy + math.sin(ang) * dist
                self.create_oval(px-3, py-3, px+3, py+3, fill=dot_color, outline="")
                
            if self.state == "success":
                for i in range(5):
                    ang = -self.phase * 0.8 + (i * (math.pi * 2 / 5))
                    px = cx + math.cos(ang) * (pulse + 60 * self.scale); py = cy + math.sin(ang) * (pulse + 60 * self.scale)
                    self.create_oval(px-2, py-2, px+2, py+2, fill="#ffffff", outline="")
                
                # V5.0.0: The Holographic Satisfaction Checkmark (Explicit Segments)
                cs = int(max(15, 30 * self.scale))
                p1x, p1y = int(cx - cs*0.8), int(cy)
                p2x, p2y = int(cx - cs*0.1), int(cy + cs*0.7)
                p3x, p3y = int(cx + cs), int(cy - cs*0.8)
                lw = int(max(3, 6*self.scale))
                self.create_line(p1x, p1y, p2x, p2y, fill=COLOR_ACCENT, width=lw, capstyle="round")
                self.create_line(p2x, p2y, p3x, p3y, fill=COLOR_ACCENT, width=lw, capstyle="round")

        self.after(30, self.animate)

    def lerp_color(self, c1, c2, t):
        def parse(c): return [int(c[i:i+2], 16) for i in (1, 3, 5)]
        rgb1, rgb2 = parse(c1), parse(c2)
        res = [int(rgb1[i] + (rgb2[i]-rgb1[i])*t) for i in range(3)]
        return f"#{res[0]:02x}{res[1]:02x}{res[2]:02x}"

class NeuralHubApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Neural Hub v5.0.0 - True Tech Edition")
        
        # NATIVE MAXIMIZE WITH EXPLICIT DIMENSIONS
        self.sw, self.sh = self.winfo_screenwidth(), self.winfo_screenheight()
        
        # Calculate dynamic global scale multiplier based on standard 1080p
        self.scale = min(self.sw / 1920, self.sh / 1080)
        # Cap scaling so it doesn't become over-crushed on small laptops (floor 0.65) or overly massive on 4k (ceil 1.5)
        self.scale = max(0.65, min(self.scale, 1.5))
        
        self.geometry(f"{self.sw}x{self.sh}+0+0")
        self.attributes("-alpha", 0.0)
        self.after(100, lambda: self.state("zoomed"))
        
        self.bind("<Escape>", lambda e: self.destroy())
        self.configure(fg_color=COLOR_BG)
        
        self.base_path = get_base_path()
        self.run_path = get_real_run_path()
        
        # RENDER BEFORE ICON APPLY (CRITICAL FOR TASKBAR HOOK)
        self.update_idletasks()
        try:
            icon_path = os.path.join(self.base_path, "icone_novo.ico")
            self.iconbitmap(icon_path)
            set_app_icon(self, icon_path)
        except: pass
        
        self.input_folder = os.path.join(self.run_path, PASTA_ENTRADA_NOME)
        self.found_files = []
        self.ui_queue = queue.Queue()
        self.process_ui_queue()
        self.setup_ui()
        # Start fade in IMMEDIATELY because launcher.py is frozen behind us visually
        self.after(100, self.fade_in)
        self.after(1000, self.auto_scan)

    def process_ui_queue(self):
        try:
            while True:
                task_action = self.ui_queue.get_nowait()
                task_action()
        except queue.Empty:
            pass
        self.after(50, self.process_ui_queue)

    def fade_in(self):
        a = self.attributes("-alpha")
        if a < 1.0: 
            self.attributes("-alpha", a + 0.08)
            self.after(20, self.fade_in)
        else:
            import sys
            if hasattr(sys, '_splash_window'):
                try:
                    sys._splash_window.destroy()
                except: pass

    def setup_ui(self):
        # 1. THE QUANTUM CORE STAGE (Center of the screen)
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        # per-fect center, slightly elevated to give the button explicit lower margin
        self.core_area = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.core_area.place(relx=0.5, rely=0.44, anchor="center")

        # The Grand Orb (Dynamically Scaled)
        orb_w = int(450 * self.scale)
        orb_h = int(400 * self.scale)
        self.orb = NeuralOrb(self.core_area, scale=self.scale, width=orb_w, height=orb_h)
        self.orb.pack(pady=(0, int(10 * self.scale)))

        # Minimalist Title (Dynamically Scaled)
        font_main = int(40 * self.scale)
        self.lbl_main = ctk.CTkLabel(self.core_area, text="AWAITING NEURAL LINK", font=("Segoe UI Light", font_main), text_color="white")
        self.lbl_main.pack(pady=(int(5 * self.scale), int(2 * self.scale)))
        
        # Progress Bar (Dynamically Scaled)
        self.progress_bar = ctk.CTkProgressBar(self.core_area, width=int(400 * self.scale), height=max(2, int(3 * self.scale)), fg_color="#0a1a30", progress_color=COLOR_ACCENT)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=int(20 * self.scale))

        # Dynamic Glowing Action Button
        btn_font = int(14 * self.scale)
        btn_w = int(320 * self.scale)
        btn_h = int(50 * self.scale)
        self.btn_action = ctk.CTkButton(self.core_area, text="ACTIVATE MUSIC CORE", font=("Segoe UI Semibold", btn_font), fg_color="#041812", hover_color="#062b1f", border_width=2, border_color=COLOR_NEON_BLUE, text_color=COLOR_ACCENT, text_color_disabled=COLOR_TEXT_DIM, height=btn_h, width=btn_w, corner_radius=12, command=self.run_process)
        self.btn_action.pack(pady=(int(5 * self.scale), int(10 * self.scale)))
        self.btn_action.configure(state="disabled") # Start visible but disabled

        # 3. SLEEK FLOATING STATUS LOG (Bottom Docked)
        self.bottom_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.bottom_container.pack(side="bottom", fill="x", pady=(0, int(10 * self.scale)))
        
        self.report_container = ctk.CTkFrame(self.bottom_container, fg_color="transparent")
        self.report_container.pack(side="top", pady=(0, int(15 * self.scale)))

        font_log = max(10, int(12 * self.scale))
        self.lbl_status = ctk.CTkLabel(self.bottom_container, text="System standing by for Thiago Griebel", font=("Consolas", font_log), text_color=COLOR_TEXT_DIM)
        self.lbl_status.pack(side="bottom")

    def log_console(self, msg, type="INFO"):
        prefix = {"INFO": "SYSTEM", "SUCCESS": "CORE", "MOVE": "SYNC", "WAIT": "SCAN", "ERROR": "ERR"}.get(type, "LOG")
        self.lbl_status.configure(text=f"[{prefix}] {msg}")

    def show_report(self, count):
        self.lbl_status.configure(text=f"[STABLE] Neural objects optimized for Thiago Griebel")
        
        for widget in self.report_container.winfo_children():
            widget.destroy()
            
        stats = [("STATUS", "STABLE", COLOR_ACCENT), ("OBJECTS", f"{count} SYNCED", "#fff"), ("OPTIMIZATION", "100%", COLOR_NEON_BLUE), ("CORE", "ACTIVE", COLOR_ACCENT)]
        font_label = max(8, int(10 * self.scale))
        font_val = max(14, int(18 * self.scale))
        
        for label, val, col in stats:
            f = ctk.CTkFrame(self.report_container, fg_color="transparent"); f.pack(side="left", expand=True, padx=int(20 * self.scale))
            ctk.CTkLabel(f, text=label, font=("Consolas", font_label, "bold"), text_color=COLOR_TEXT_DIM).pack()
            ctk.CTkLabel(f, text=val, font=("Segoe UI", font_val, "bold"), text_color=col).pack()

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
        
        if len(found) > 0:
            self.lbl_main.configure(text="READY TO ORGANIZE")
            self.log_console(f"Scan complete: {len(found)} objects indexed in Neural Library.", "WAIT")
            self.btn_action.configure(state="normal")
        else:
            self.lbl_main.configure(text="LIBRARY EMPTY")
            self.log_console("System Idle. Waiting for neural objects in input directory.", "INFO")
            self.btn_action.configure(state="disabled")

    def run_process(self):
        if not self.found_files: return
        self.orb.state = "busy"; self.btn_action.configure(state="disabled", text="DEPLOYING...")
        self.progress_bar.set(0)
        
        def work():
            for pasta in NEURAL_BRAIN.keys():
                os.makedirs(os.path.join(self.base_path, pasta), exist_ok=True)
            
            total = len(self.found_files)
            count = 0
            
            BATCH_SIZE = 40
            batches = [self.found_files[i:i + BATCH_SIZE] for i in range(0, total, BATCH_SIZE)]
            
            if gemini_model:
                self.ui_queue.put(lambda: self.log_console(f"AI Gemini Activado. Processando em {len(batches)} Lotes.", "INFO"))
            else:
                self.ui_queue.put(lambda: self.log_console(f"Modo Offline Clássico Activado.", "INFO"))
            
            processed_so_far = 0

            for batch_index, batch in enumerate(batches):
                # Fase 1: Coleta Local Extrema e Rápida do Lote
                batch_data_to_ai = []
                batch_local_cache = {} 

                for orig_path in batch:
                    name = os.path.basename(orig_path)
                    text_analise = name.lower()
                    text_analise = re.sub(r'[_.\-()\[\]]', ' ', text_analise)
                    
                    try:
                        audio = MutagenFile(orig_path, easy=True)
                        if audio:
                            for key in ['artist', 'genre', 'title']:
                                if key in audio: 
                                    text_analise += " | " + " ".join(audio[key])
                    except Exception as e:
                        pass
                    
                    # Store ID for AI mapping logic
                    track_id = str(len(batch_data_to_ai) + 1)
                    batch_data_to_ai.append({
                        "id": track_id,
                        "file": name,
                        "meta": text_analise
                    })
                    batch_local_cache[track_id] = {
                        "path": orig_path,
                        "name": name,
                        "local_meta": text_analise  # Usado pro Fallback Offline
                    }
                
                # Fase 2: O Cérebro entra em ação
                gemini_answers = None
                if gemini_model:
                    self.ui_queue.put(lambda bi=batch_index+1, bt=len(batches): self.log_console(f"Enviando Lote {bi}/{bt} para a IA...", "WAIT"))
                    log_debug(f"Iniciando requisicao do lote {batch_index+1}")
                    gemini_answers = get_gemini_batch_classification(batch_data_to_ai, NEURAL_BRAIN)
                    
                    if gemini_answers:
                        self.ui_queue.put(lambda: self.log_console(f"Lote classificado via Rede Neural LLM.", "SUCCESS"))
                    else:
                        self.ui_queue.put(lambda: self.log_console(f"Falha na IA. Tentando Engine Offline pro Lote...", "ERROR"))

                # Fase 3: Movimentação (Híbrida)
                for track_data in batch_data_to_ai:
                    track_id = track_data["id"]
                    cache = batch_local_cache[track_id]
                    orig_path = cache["path"]
                    name = cache["name"]
                    local_meta = cache["local_meta"].lower()
                    best_cat = None

                    if gemini_answers and str(track_id) in gemini_answers and gemini_answers[str(track_id)] in NEURAL_BRAIN:
                        best_cat = gemini_answers[str(track_id)]
                    else:
                        # FALLBACK OFFLINE CLASSICO (Palavras chave ponderadas)
                        scores = {cat: 0 for cat in NEURAL_BRAIN.keys()}
                        for cat, keywords in NEURAL_BRAIN.items():
                            for word in keywords:
                                if f" {word} " in f" {local_meta} ":
                                    scores[cat] += 2
                                elif word in local_meta:
                                    scores[cat] += 1
                        best_cat = max(scores, key=scores.get) if max(scores.values()) > 0 else None

                    # MOVE FÍSICO
                    if best_cat:
                        try:
                            shutil.move(orig_path, os.path.join(self.run_path, best_cat, name))
                            self.ui_queue.put(lambda n=name, c=best_cat: self.log_console(f"{n[:25]}... >> [{c[:12]}]", "MOVE"))
                            count += 1
                        except Exception as e:
                            self.ui_queue.put(lambda n=name, err=str(e): self.log_console(f"Mv err | {n[:15]}...: {err}", "ERROR"))
                    else:
                        self.ui_queue.put(lambda n=name: self.log_console(f"{n[:25]}... No neural match.", "INFO"))
                    
                    processed_so_far += 1
                    progress = processed_so_far / total
                    self.ui_queue.put(lambda p=progress: self.progress_bar.set(p))
                    time.sleep(0.15) # Dramatic slowdown for visual mapping
                
                # Ant-Rate Limit para AI
                if gemini_model and gemini_answers and batch_index < len(batches) - 1:
                    time.sleep(3)

            self.ui_queue.put(lambda c=count: self.finish(c))
        threading.Thread(target=work, daemon=True).start()

    def finish(self, count):
        self.orb.state = "success"; self.btn_action.configure(state="normal", text="NEURAL SYSTEM SYNCED", fg_color=COLOR_ACCENT, text_color="black")
        self.lbl_main.configure(text="CORE STABILITY REACHED")
        self.show_report(count)

if __name__ == "__main__":
    NeuralHubApp().mainloop()

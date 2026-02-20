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
# COLE SUA CHAVE DO GOOGLE ENTRE AS ASPAS ABAIXO:
GEMINI_API_KEY = "AIzaSyC2DcDfF8MRmvYAjUy4HsHV8RsDTlGeciw"

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
    for track in tracks_data_list:
        prompt += f"ID: {track['id']} | Arquivo: {track['file']} | Metadados: {track['meta']}\n"
    
    prompt += """
Responda APENAS com um objeto JSON puro, onde as chaves são os IDs das músicas que te passei e os valores são as categorias escolhidas que pertencem EXATAMENTE à lista que forneci acima. Se não tiver certeza de qual é, defina como null.
Exemplo:
{"1": "02_Cinematic_Emocao_Filmes_Documentarios_Drama", "2": "12_Urban_Trap_HipHop_Modern"}
"""
    try:
        response = gemini_model.generate_content(prompt)
        result = json.loads(response.text)
        return result
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None

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

        if self.state in ["busy", "success"]:
            num_dots = 12 if self.state == "busy" else 8
            speed = 2.5 if self.state == "busy" else 1.2
            dot_color = COLOR_ACCENT if self.state == "busy" else COLOR_NEON_BLUE
            
            for i in range(num_dots):
                ang = self.phase * speed + (i * (math.pi * 2 / num_dots))
                dist = pulse + 25 if self.state == "busy" else pulse + 40
                px = cx + math.cos(ang) * dist; py = cy + math.sin(ang) * dist
                self.create_oval(px-3, py-3, px+3, py+3, fill=dot_color, outline="")
                
            if self.state == "success":
                for i in range(5):
                    ang = -self.phase * 0.8 + (i * (math.pi * 2 / 5))
                    px = cx + math.cos(ang) * (pulse + 60); py = cy + math.sin(ang) * (pulse + 60)
                    self.create_oval(px-2, py-2, px+2, py+2, fill="#fff", outline="")

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
        self.ui_queue = queue.Queue()
        self.process_ui_queue()
        self.setup_ui()
        self.fade_in()
        self.after(800, self.auto_scan)

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
        if a < 1.0: self.attributes("-alpha", a + 0.1); self.after(20, self.fade_in)

    def setup_ui(self):
        self.header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        self.header.pack(fill="x", padx=20, pady=5)
        self.header.bind("<Button-1>", self.start_move)
        self.header.bind("<B1-Motion>", self.do_move)
        ctk.CTkLabel(self.header, text="NEURAL HUB ENGINE v3.3 // ACTIVE", font=("Consolas", 10, "bold"), text_color=COLOR_TEXT_DIM).pack(side="left")
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

        self.bottom_area = ctk.CTkFrame(self, fg_color=COLOR_CONSOLE_BG, height=180, corner_radius=0, border_width=1, border_color="#0a1a30")
        self.bottom_area.pack(fill="x")
        self.bottom_area.pack_propagate(False)
        self.console_text = ctk.CTkTextbox(self.bottom_area, fg_color="transparent", font=("Consolas", 11), text_color=COLOR_ACCENT, activate_scrollbars=False)
        self.console_text.pack(fill="both", expand=True, padx=25, pady=15)

    def log_console(self, msg, type="INFO"):
        prefix = {"INFO": "[SYSTEM::LOG]", "SUCCESS": "[CORE::SUCCESS]", "MOVE": "[NEURAL::MOVE]", "WAIT": "[SYSTEM::SCAN]", "ERROR": "[SYSTEM::ERROR]"}.get(type, "[LOG]")
        self.console_text.insert("end", f"{prefix} {msg}\n"); self.console_text.see("end")

    def show_report(self, count):
        self.console_text.pack_forget()
        report_frame = ctk.CTkFrame(self.bottom_area, fg_color="transparent")
        report_frame.pack(fill="both", expand=True, padx=40, pady=20)
        stats = [("STATUS", "STABLE", COLOR_ACCENT), ("OBJECTS", f"{count} SYNCED", "#fff"), ("OPTIMIZATION", "100%", COLOR_NEON_BLUE), ("CORE", "ACTIVE", COLOR_ACCENT)]
        for label, val, col in stats:
            f = ctk.CTkFrame(report_frame, fg_color="transparent"); f.pack(side="left", expand=True)
            ctk.CTkLabel(f, text=label, font=("Consolas", 10, "bold"), text_color=COLOR_TEXT_DIM).pack()
            ctk.CTkLabel(f, text=val, font=("Segoe UI", 18, "bold"), text_color=col).pack()

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
                            shutil.move(orig_path, os.path.join(self.base_path, best_cat, name))
                            self.ui_queue.put(lambda n=name, c=best_cat: self.log_console(f"{n[:25]}... >> [{c[:12]}]", "MOVE"))
                            count += 1
                        except Exception as e:
                            self.ui_queue.put(lambda n=name, err=str(e): self.log_console(f"Mv err | {n[:15]}...: {err}", "ERROR"))
                    else:
                        self.ui_queue.put(lambda n=name: self.log_console(f"{n[:25]}... No neural match.", "INFO"))
                    
                    processed_so_far += 1
                    progress = processed_so_far / total
                    self.ui_queue.put(lambda p=progress: self.progress_bar.set(p))
                    time.sleep(0.02) # Soft delay pra fluidez visual
                
                # Ant-Rate Limit para AI
                if gemini_model and gemini_answers and batch_index < len(batches) - 1:
                    time.sleep(3)

            self.ui_queue.put(lambda c=count: self.finish(c))
        threading.Thread(target=work, daemon=True).start()

    def finish(self, count):
        self.orb.state = "success"; self.btn_action.configure(state="normal", text="NEURAL SYSTEM SYNCED", fg_color=COLOR_ACCENT, text_color="black")
        self.lbl_main.configure(text="CORE STABILITY REACHED")
        self.lbl_sub.configure(text=f"Neural objects optimized for Thiago Griebel", text_color=COLOR_ACCENT)
        self.show_report(count)

if __name__ == "__main__":
    NeuralHubApp().mainloop()

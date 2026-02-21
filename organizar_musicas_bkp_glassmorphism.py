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
from PIL import Image, ImageTk

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

class AnimatedOrb(ctk.CTkLabel):
    def __init__(self, master, img_path=None, **kwargs):
        super().__init__(master, text="", **kwargs)
        self.frames = []
        self.current_frame = 0
        self.state = "idle"
        
        if img_path and os.path.exists(img_path):
            try:
                pil_img = Image.open(img_path).convert("RGBA")
                for scale in [1.0, 1.01, 1.02, 1.03, 1.02, 1.01]:
                    size = int(320 * scale)
                    resized = pil_img.resize((size, size), Image.Resampling.LANCZOS)
                    self.frames.append(ctk.CTkImage(light_image=resized, dark_image=resized, size=(size, size)))
                self.configure(image=self.frames[0])
            except Exception as e:
                print("Error loading neural orb image:", e)

        self.animate()

    def animate(self):
        if self.frames:
            if self.state == "busy":
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.configure(image=self.frames[self.current_frame])
                self.after(40, self.animate) # Fast pulse processing
            elif self.state == "success":
                self.configure(image=self.frames[-1]) # Max expanded size
            else: # idle
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.configure(image=self.frames[self.current_frame])
                self.after(150, self.animate) # Slow breathing rate
        else:
            self.after(200, self.animate)

class NeuralHubApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Remove overrideredirect to allow default window controls, start maximized
        self.state('zoomed')
        self.title("Neural Hub Engine v3.5")
        
        # Determine screen size for scaling assets
        self.sw, self.sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{self.sw}x{self.sh}")
        self.configure(fg_color=COLOR_BG)
        
        self.base_path = get_base_path()
        
        icon_path = os.path.join(self.base_path, "icone_perfeito.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                print("Failed to load window icon:", e)
                
        self.input_folder = os.path.join(self.base_path, PASTA_ENTRADA_NOME)
        self.found_files = []
        self.ui_queue = queue.Queue()
        
        self.process_ui_queue()
        self.setup_ui()
        self.after(800, self.auto_scan)

    def process_ui_queue(self):
        try:
            while True:
                task_action = self.ui_queue.get_nowait()
                task_action()
        except queue.Empty:
            pass
        self.after(50, self.process_ui_queue)

    def setup_ui(self):
        # 1. Background: Deep Black (Silence visual)
        self.bg_label = ctk.CTkLabel(self, text="", fg_color="#030406")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # 2. Main Hero Area
        self.center_panel = ctk.CTkFrame(self.bg_label, fg_color="transparent", border_width=0)
        self.center_panel.place(relx=0.5, rely=0.5, relwidth=0.6, relheight=0.8, anchor="center")
        
        orb_path = os.path.join(self.base_path, "esfera_neural.png")
        self.orb = AnimatedOrb(self.center_panel, img_path=orb_path)
        self.orb.pack(pady=(40, 30))
        
        # Typography: Inter/SF Pro style (Thin, elegant)
        self.lbl_main = ctk.CTkLabel(self.center_panel, text="NEURAL MUSIC CORE", font=("Helvetica Neue", 36, "bold"), text_color="#FFFFFF")
        self.lbl_main.pack(pady=(0, 5))
        
        self.lbl_sub = ctk.CTkLabel(self.center_panel, text="STANDBY", font=("Inter", 16), text_color="#40C080")
        self.lbl_sub.pack(pady=(0, 50))
        
        self.btn_action = ctk.CTkButton(self.center_panel, text="ORGANIZE LIBRARY", font=("Inter", 15, "bold"), fg_color="#051C10", border_width=1, border_color="#00FF66", hover_color="#0B2B1B", text_color="#00FF66", height=65, width=280, corner_radius=35, command=self.run_process)
        self.btn_action.pack()

    def log_console(self, msg, type="INFO"):
        pass # Silenced. Only updating central UI now.

    def update_status(self, text, color="#40C080"):
        self.lbl_sub.configure(text=text.upper(), text_color=color)
        self.update_idletasks()

    def show_report(self, count):
        self.btn_action.configure(state="normal", text="ORGANIZE LIBRARY", fg_color="#051C10", text_color="#00FF66", border_color="#00FF66")
        self.orb.state = "idle"
        self.update_status("✓ LIBRARY OPTIMIZED", color="#00FF66")

    def auto_scan(self):
        if not os.path.exists(self.input_folder): os.makedirs(self.input_folder)
        found = []
        for root, _, files in os.walk(self.input_folder):
            for f in files:
                if f.lower().endswith((".mp3", ".wav", ".flac", ".aiff")):
                    found.append(os.path.join(root, f))
        self.found_files = found
        if found:
            self.update_status("READY")
        else:
            self.update_status("STANDBY: NO TRACKS", "#666666")

    def run_process(self):
        if not self.found_files: return
        self.btn_action.configure(state="disabled", text="ANALYZING...", text_color="#506070", border_color="#1A2B3C", fg_color="#05080C")
        self.orb.state = "busy"
        self.update_status("SCANNING...", color="#00FF66")
        
        # Start processing via Thread to avoid freezing UI
        threading.Thread(target=self.process_files_thread, daemon=True).start()

    def process_files_thread(self):
        for pasta in NEURAL_BRAIN.keys():
            os.makedirs(os.path.join(self.base_path, pasta), exist_ok=True)
            
        total = len(self.found_files)
        count = 0
        
        BATCH_SIZE = 40
        batches = [self.found_files[i:i + BATCH_SIZE] for i in range(0, total, BATCH_SIZE)]
        
        if gemini_model:
            self.ui_queue.put(lambda: self.update_status(f"AI GEMINI ACTIVATED. PROCESSING {len(batches)} BATCHES.", "INFO"))
        else:
            self.ui_queue.put(lambda: self.update_status(f"OFFLINE MODE ACTIVATED.", "INFO"))
        
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
                self.ui_queue.put(lambda bi=batch_index+1, bt=len(batches): self.update_status(f"SENDING BATCH {bi}/{bt} TO AI...", "WAIT"))
                gemini_answers = get_gemini_batch_classification(batch_data_to_ai, NEURAL_BRAIN)
                
                if gemini_answers:
                    self.ui_queue.put(lambda: self.update_status(f"BATCH CLASSIFIED VIA LLM.", "SUCCESS"))
                else:
                    self.ui_queue.put(lambda: self.update_status(f"AI FAILED. TRYING OFFLINE ENGINE FOR BATCH...", "ERROR"))

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
                        count += 1
                    except Exception as e:
                        pass
                
                processed_so_far += 1
                progress = processed_so_far / total
                self.ui_queue.put(lambda p=progress, c=processed_so_far, t=total: self.update_progress(p, f"SCANNING... {c}/{t} TRACKS INDEXED"))
                time.sleep(0.02) # Soft delay pra fluidez visual
            
            # Ant-Rate Limit para AI
            if gemini_model and gemini_answers and batch_index < len(batches) - 1:
                time.sleep(3)

        self.ui_queue.put(lambda c=count: self.show_report(c))

    def update_progress(self, p, text):
        self.progress_bar.set(p)
        self.update_status(text, "#00FF66")

if __name__ == "__main__":
    NeuralHubApp().mainloop()

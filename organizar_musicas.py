import os
import shutil
import re
import time
import sys
import threading
import customtkinter as ctk
from tkinter import filedialog, END
from mutagen import File as MutagenFile

# ==============================================================================
# DESIGN SYSTEM (CYBERPUNK THEME)
# ==============================================================================
COLOR_BG = "#0a0a0a"       # Fundo Absoluto
COLOR_SURFACE = "#141414"  # Cards/Containers
COLOR_ACCENT = "#00ff66"   # Verde Neon Principal
COLOR_ACCENT_HOVER = "#00cc55"
COLOR_TEXT_MAIN = "#ffffff"
COLOR_TEXT_DIM = "#888888"
FONT_MAIN = "Roboto Medium"
FONT_MONO = "Consolas"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green") # Base, mas vamos sobrescrever

# ==============================================================================
# CONFIGURAÇÃO DE INTELIGÊNCIA (MANTIDA)
# ==============================================================================
# ... (Mantendo sua lógica de Artistas e Regras intacta para economizar linhas, 
# já que o foco agora é visual. A lógica é a mesma da v2.0) ...
PASTA_ENTRADA_PADRAO = "_ENTRADA_DE_MUSICAS"

ARTISTAS_CONHECIDOS = {
    "alexgrohl": "01_Alta_Energia_Impacto_Esportes_Carros_Acao",
    "glories": "01_Alta_Energia_Impacto_Esportes_Carros_Acao",
    "the glories": "01_Alta_Energia_Impacto_Esportes_Carros_Acao",
    "stomp": "01_Alta_Energia_Impacto_Esportes_Carros_Acao",
    "alon ohana": "02_Cinematic_Emocao_Filmes_Documentarios_Drama",
    "kyle preston": "02_Cinematic_Emocao_Filmes_Documentarios_Drama",
    "yehezkel raz": "02_Cinematic_Emocao_Filmes_Documentarios_Drama",
    "break of reality": "02_Cinematic_Emocao_Filmes_Documentarios_Drama",
    "rex banner": "03_Good_Vibes_Lifestyle_Vlog_Viagem_Comercial",
    "ben fox": "03_Good_Vibes_Lifestyle_Vlog_Viagem_Comercial",
    "sourwah": "03_Good_Vibes_Lifestyle_Vlog_Viagem_Comercial",
    "ikoliks": "03_Good_Vibes_Lifestyle_Vlog_Viagem_Comercial",
    "osker wyld": "04_Lounge_Tech_Background_Fundo_Neutro_Lofi",
    "ziggy": "04_Lounge_Tech_Background_Fundo_Neutro_Lofi",
    "jorge & mateus": "07_Hits_Brasileiros_Copyright_Cuidado",
    "sandy & junior": "07_Hits_Brasileiros_Copyright_Cuidado",
    "toquinho": "07_Hits_Brasileiros_Copyright_Cuidado",
    "anbr": "02_Cinematic_Emocao_Filmes_Documentarios_Drama",
    "marko maksimovic": "02_Cinematic_Emocao_Filmes_Documentarios_Drama",
    "just for kicks": "03_Good_Vibes_Lifestyle_Vlog_Viagem_Comercial",
    "roie shpigler": "02_Cinematic_Emocao_Filmes_Documentarios_Drama"
}

REGRAS_PALAVRAS = {
    "05_Vinhetas_Logos_Sonoros_Abaixo_30s": ["logo", "ident", "sting", "bumper", "jingle", "intro", "opener", "transition", "whoosh", "sfx", "vinheta", "reveal"],
    "06_Casamentos_Cerimonias": ["wedding", "casamento", "bride", "noiva", "ceremony", "romantic", "love", "marriage", "sentimental", "valentine"],
    "01_Alta_Energia_Impacto_Esportes_Carros_Acao": ["powerful", "exciting", "angry", "aggressive", "rock", "metal", "heavy", "distortion", "sport", "action", "extreme", "race", "drive", "energy", "intense", "stomp", "drums", "fight", "workout", "adrenaline", "percussion"],
    "02_Cinematic_Emocao_Filmes_Documentarios_Drama": ["cinematic", "epic", "serious", "dramatic", "mysterious", "hopeful", "score", "soundtrack", "trailer", "heroic", "orchestra", "strings", "violin", "cello", "piano", "classical", "fantasy", "emotional", "sad", "inspiring", "documentary"],
    "03_Good_Vibes_Lifestyle_Vlog_Viagem_Comercial": ["uplifting", "happy", "carefree", "playful", "groovy", "pop", "indie", "funk", "holiday", "good vibes", "positive", "upbeat", "summer", "beach", "travel", "viagem", "vlog", "lifestyle", "party", "celebration", "commercial", "fashion"],
    "04_Lounge_Tech_Background_Fundo_Neutro_Lofi": ["peaceful", "ambient", "electronic", "lounge", "lofi", "lo-fi", "chill", "atmosphere", "background", "fundo", "neutral", "calm", "relax", "soft", "study", "meditation", "dreamy", "minimal", "synth"],
    "09_Corporate_Business_Tecnologia": ["corporate", "business", "tech", "technology", "innovation", "presentation", "success", "motivational", "modern", "digital"],
    "10_Suspense_Terror_Dark": ["dark", "scary", "tension", "fear", "horror", "terror", "suspense", "mystery", "crime", "danger", "ominous"],
    "11_Comedy_Fun_Quirky": ["funny", "comedy", "children", "quirky", "humor", "weird", "cartoon", "animation", "sneaky", "mischievous", "goofy", "pizzicato"],
    "12_Urban_Trap_HipHop_Modern": ["hip hop", "hiphop", "rap", "trap", "drill", "beat", "urban", "street", "gangsta", "swagger", "bass", "808", "sexy", "r&b"],
    "13_Acoustic_Folk_Rustico": ["acoustic", "acustico", "folk", "country", "blues", "roots", "guitar", "violao", "rustic", "nature", "campfire", "earthy"],
    "14_World_Music_Cultural_Regional": ["latin", "salsa", "bossa nova", "asian", "k-pop", "celtic", "african", "reggae", "bollywood", "world", "culture", "regional", "flamenco", "tango"],
    "15_Holiday_Sazonal_Natal_Feriados": ["christmas", "xmas", "holiday", "santa", "halloween", "easter", "new year", "festive", "carol"],
    "16_Kids_Infantil_Games_Escola": ["kids", "children", "game", "8bit", "arcade", "cute", "school", "baby", "toy", "nursery"],
    "17_Vocals_Cancoes_Com_Letra": ["lyrical", "vocal", "singer", "lyrics", "song", "voice"],
    "18_Jazz_Blues_Classy_Sophisticated": ["jazz", "blues", "saxophone", "swing", "lounge jazz", "smooth", "noir", "classy", "sophisticated", "bar", "restaurant"],
    "19_Electronic_Dance_Club_House_Techno": ["edm", "house", "techno", "dubstep", "trance", "club", "rave", "party", "dance", "beat", "festival"],
    "20_Experimental_Abstract_SoundDesign": ["experimental", "abstract", "sound design", "glitch", "texture", "drone", "avant garde", "noise", "industrial", "fx", "atmosphere", "weird"]
}

def normalizar_texto(texto):
    if not texto: return ""
    return re.sub(r'[^\w\s]', ' ', texto.lower())

def ler_metadados(caminho_arquivo):
    try:
        audio = MutagenFile(caminho_arquivo, easy=True)
        if audio:
            tags = []
            if 'artist' in audio: tags.extend(audio['artist'])
            elif 'author' in audio: tags.extend(audio['author'])
            if 'genre' in audio: tags.extend(audio['genre'])
            if 'title' in audio: tags.extend(audio['title'])
            return " ".join(tags)
    except: pass
    return ""

# ==============================================================================
# UI COMPONENTS
# ==============================================================================
class AudioOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- CONFIGURAÇÃO DA JANELA FRAMELESS ---
        self.overrideredirect(True) # Remove barra do Windows
        self.geometry("950x700")
        self.configure(fg_color=COLOR_BG)
        
        # Centraliza na tela
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw/2) - (950/2)
        y = (sh/2) - (700/2)
        self.geometry('%dx%d+%d+%d' % (950, 700, x, y))

        # Ícone
        if os.path.exists("icone_perfeito.ico"):
            self.iconbitmap("icone_perfeito.ico")
            self.wm_iconbitmap("icone_perfeito.ico")

        # Layout Grid Principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Área de conteúdo expande

        # 1. BARRA DE TÍTULO CUSTOMIZADA (Header)
        self.title_bar = ctk.CTkFrame(self, height=40, fg_color=COLOR_BG, corner_radius=0)
        self.title_bar.grid(row=0, column=0, sticky="ew")
        
        # Lógica de Arrastar (Drag Window)
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        
        self.lbl_app_title = ctk.CTkLabel(self.title_bar, text=" AI AUDIO ORGANIZER", font=(FONT_MAIN, 14, "bold"), text_color=COLOR_TEXT_DIM)
        self.lbl_app_title.pack(side="left", padx=15, pady=5)
        self.lbl_app_title.bind("<Button-1>", self.start_move) # Permite arrastar pelo texto também

        # Botão Fechar (X)
        self.btn_close = ctk.CTkButton(self.title_bar, text="✕", width=40, height=30, 
                                       fg_color="transparent", hover_color="#c42b1c", 
                                       command=self.encerrar_app)
        self.btn_close.pack(side="right", padx=0, pady=0)

        # 2. CONTROLES (Barra Superior)
        self.top_frame = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0)
        self.top_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(10, 20))
        self.top_frame.grid_columnconfigure(1, weight=1)

        # Botão Pasta
        self.btn_folder = ctk.CTkButton(self.top_frame, text="📁 Selecionar Pasta", 
                                        fg_color=COLOR_SURFACE, hover_color="#222", 
                                        text_color="white", border_width=1, border_color="#333",
                                        command=self.selecionar_pasta, height=45)
        self.btn_folder.grid(row=0, column=0, padx=(0, 10))

        # Input Path (Estilo Card)
        self.entry_path = ctk.CTkEntry(self.top_frame, placeholder_text="Caminho da pasta...", 
                                       fg_color=COLOR_SURFACE, border_color="#333", text_color="gray",
                                       height=45, font=(FONT_MAIN, 12))
        self.entry_path.grid(row=0, column=1, sticky="ew")
        self.entry_path.insert(0, os.path.join(os.getcwd(), PASTA_ENTRADA_PADRAO))

        # CTA (Botão Neon)
        self.btn_run = ctk.CTkButton(self.top_frame, text="⚡ ORGANIZAR AGORA", 
                                     fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, 
                                     text_color="black", font=(FONT_MAIN, 13, "bold"),
                                     height=45, command=self.iniciar_thread_organizacao)
        self.btn_run.grid(row=0, column=2, padx=(10, 0))

        # 3. ÁREA DE VISUALIZAÇÃO (Console/Dashboard)
        self.dashboard_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, corner_radius=10, border_width=1, border_color="#222")
        self.dashboard_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Sub-frames para Log e Status
        self.dashboard_frame.grid_rowconfigure(1, weight=1)
        self.dashboard_frame.grid_columnconfigure(0, weight=1)

        # Barra de Status (Header do Dashboard)
        self.status_header = ctk.CTkLabel(self.dashboard_frame, text="STATUS DO SISTEMA: AGUARDANDO", 
                                          font=(FONT_MONO, 11), text_color=COLOR_ACCENT, anchor="w")
        self.status_header.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        # Área de Log Rolável (Console Limpo)
        self.log_area = ctk.CTkTextbox(self.dashboard_frame, fg_color="transparent", text_color="#ccc",
                                       font=(FONT_MONO, 12), activate_scrollbars=True)
        self.log_area.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.log_area.insert("0.0", ">>> Sistema inicializado.\n>>> Pronto para organizar.\n")

        # 4. BARRA DE PROGRESSO (Bottom)
        self.progress_frame = ctk.CTkFrame(self, height=30, fg_color=COLOR_BG)
        self.progress_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        self.progressbar = ctk.CTkProgressBar(self.progress_frame, height=4, progress_color=COLOR_ACCENT)
        self.progressbar.pack(fill="x", pady=10)
        self.progressbar.set(0)

    # --- LÓGICA DE MOVIMENTAÇÃO DA JANELA ---
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"{x}+{y}")

    def encerrar_app(self):
        self.quit()
        self.destroy()

    # --- LÓGICA DO APP ---
    def log(self, mensagem, tipo="info"):
        prefixo = " [INFO] "
        if tipo == "success": prefixo = " [OK] "
        elif tipo == "error": prefixo = " [ERRO] "
        elif tipo == "warn": prefixo = " [!] "
        
        texto = f"{prefixo}{mensagem}\n"
        self.log_area.insert("end", texto)
        self.log_area.see("end")

    def selecionar_pasta(self):
        folder = filedialog.askdirectory()
        if folder:
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, folder)

    def iniciar_thread_organizacao(self):
        thread = threading.Thread(target=self.organizar)
        thread.start()

    def organizar(self):
        self.btn_run.configure(state="disabled", text="PROCESSANDO...")
        self.status_header.configure(text="STATUS: ANALISANDO BIBLIOTECA...")
        
        caminho_entrada = self.entry_path.get()
        base_destino = os.getcwd() # Sempre organiza na raiz do executável

        if not os.path.exists(caminho_entrada):
            try:
                os.makedirs(caminho_entrada)
            except Exception as e:
                self.log(f"Erro ao criar pasta: {e}", "error")
                self.btn_run.configure(state="normal", text="⚡ ORGANIZAR AGORA")
                return

        # 1. Estrutura
        pastas_necessarias = list(REGRAS_PALAVRAS.keys()) + ["07_Hits_Brasileiros_Copyright_Cuidado", "08_Outros_Nao_Classificados"]
        for pasta in pastas_necessarias:
            p = os.path.join(base_destino, pasta)
            if not os.path.exists(p): os.makedirs(p)

        # 2. Scan
        arquivos_encontrados = []
        exts = ('.mp3', '.wav', '.aiff', '.flac', '.ogg', '.m4a', '.wma')
        for root, dirs, files in os.walk(caminho_entrada):
            for file in files:
                if file.lower().endswith(exts):
                    arquivos_encontrados.append(os.path.join(root, file))

        total = len(arquivos_encontrados)
        if total == 0:
            self.log("Nenhum áudio encontrado.", "warn")
            self.btn_run.configure(state="normal", text="⚡ ORGANIZAR AGORA")
            self.status_header.configure(text="STATUS: AGUARDANDO")
            return

        self.status_header.configure(text=f"STATUS: ORGANIZANDO {total} ARQUIVOS...")
        movidos = 0
        stats = {}

        for i, caminho_origem in enumerate(arquivos_encontrados):
            # UI Update
            perc = (i + 1) / total
            self.progressbar.set(perc)
            
            arquivo = os.path.basename(caminho_origem)
            texto_analise = normalizar_texto(arquivo)
            
            # Metadata Check
            metadados = ler_metadados(caminho_origem)
            if metadados: texto_analise += " " + normalizar_texto(metadados)

            # Lógica de Classificação
            destino_final = None
            motivo = ""

            for artista, pasta in ARTISTAS_CONHECIDOS.items():
                if artista in texto_analise:
                    destino_final = pasta
                    motivo = f"Artista: {artista.title()}"
                    break
            
            if not destino_final:
                for pasta, keywords in REGRAS_PALAVRAS.items():
                    for k in keywords:
                        if re.search(r"\b" + re.escape(k) + r"\b", texto_analise):
                            destino_final = pasta
                            motivo = f"Keyword: {k.upper()}"
                            break
                    if destino_final: break

            if not destino_final and "artlist musical logos" in texto_analise:
                 destino_final = "05_Vinhetas_Logos_Sonoros_Abaixo_30s"
                 motivo = "Logo Artlist"

            # Move
            if destino_final:
                pasta_dest = os.path.join(base_destino, destino_final)
                if not os.path.exists(pasta_dest): os.makedirs(pasta_dest)
                
                dest_file = os.path.join(pasta_dest, arquivo)
                if os.path.exists(dest_file):
                    base, ext = os.path.splitext(arquivo)
                    dest_file = os.path.join(pasta_dest, f"{base}_{int(time.time())}{ext}")

                try:
                    shutil.move(caminho_origem, dest_file)
                    folder_short = destino_final.split('_', 1)[1]
                    self.log(f"{arquivo[:30]}... -> {folder_short}", "success")
                    stats[destino_final] = stats.get(destino_final, 0) + 1
                    movidos += 1
                except Exception as e:
                    self.log(f"Erro: {arquivo} - {e}", "error")
            else:
                self.log(f"Não Classificado: {arquivo[:30]}...", "warn")

        # Limpeza
        try:
             for root, dirs, files in os.walk(caminho_entrada, topdown=False):
                for name in dirs:
                    try: os.rmdir(os.path.join(root, name))
                    except: pass
        except: pass

        self.log("--- FINALIZADO ---")
        self.status_header.configure(text=f"CONCLUÍDO: {movidos} ARQUIVOS ORGANIZADOS")
        self.btn_run.configure(state="normal", text="⚡ ORGANIZAR AGORA")

def main():
    app = AudioOrganizerApp()
    app.mainloop()

if __name__ == "__main__":
    main()
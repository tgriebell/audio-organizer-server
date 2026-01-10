import os
import shutil
import re
import time
import sys
import threading
import customtkinter as ctk
from tkinter import filedialog
from mutagen import File as MutagenFile

# ==============================================================================
# CONFIGURAÇÃO GERAL & INTELIGÊNCIA
# ==============================================================================

# Configuração do CustomTkinter
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

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

# MAPA MESTRE - ARTLIST MOODS & GENRES
REGRAS_PALAVRAS = {
    "05_Vinhetas_Logos_Sonoros_Abaixo_30s": [
        "logo", "ident", "sting", "bumper", "jingle", "intro", "opener", "transition", "whoosh", "sfx", "vinheta", "reveal"
    ],
    "06_Casamentos_Cerimonias": [
        "wedding", "casamento", "bride", "noiva", "ceremony", "romantic", "love", "marriage", "sentimental", "valentine"
    ],
    "01_Alta_Energia_Impacto_Esportes_Carros_Acao": [
        "powerful", "exciting", "angry", "aggressive", "rock", "metal", "heavy", "distortion", "sport", "action", "extreme", "race", "drive", "energy", "intense", "stomp", "drums", "fight", "workout", "adrenaline", "percussion"
    ],
    "02_Cinematic_Emocao_Filmes_Documentarios_Drama": [
        "cinematic", "epic", "serious", "dramatic", "mysterious", "hopeful", "score", "soundtrack", "trailer", "heroic", "orchestra", "strings", "violin", "cello", "piano", "classical", "fantasy", "emotional", "sad", "inspiring", "documentary"
    ],
    "03_Good_Vibes_Lifestyle_Vlog_Viagem_Comercial": [
        "uplifting", "happy", "carefree", "playful", "groovy", "pop", "indie", "funk", "holiday", "good vibes", "positive", "upbeat", "summer", "beach", "travel", "viagem", "vlog", "lifestyle", "party", "celebration", "commercial", "fashion"
    ],
    "04_Lounge_Tech_Background_Fundo_Neutro_Lofi": [
        "peaceful", "ambient", "electronic", "lounge", "lofi", "lo-fi", "chill", "atmosphere", "background", "fundo", "neutral", "calm", "relax", "soft", "study", "meditation", "dreamy", "minimal", "synth"
    ],
    "09_Corporate_Business_Tecnologia": [
        "corporate", "business", "tech", "technology", "innovation", "presentation", "success", "motivational", "modern", "digital"
    ],
    "10_Suspense_Terror_Dark": [
        "dark", "scary", "tension", "fear", "horror", "terror", "suspense", "mystery", "crime", "danger", "ominous"
    ],
    "11_Comedy_Fun_Quirky": [
        "funny", "comedy", "children", "quirky", "humor", "weird", "cartoon", "animation", "sneaky", "mischievous", "goofy", "pizzicato"
    ],
    "12_Urban_Trap_HipHop_Modern": [
        "hip hop", "hiphop", "rap", "trap", "drill", "beat", "urban", "street", "gangsta", "swagger", "bass", "808", "sexy", "r&b"
    ],
    "13_Acoustic_Folk_Rustico": [
        "acoustic", "acustico", "folk", "country", "blues", "roots", "guitar", "violao", "rustic", "nature", "campfire", "earthy"
    ],
    "14_World_Music_Cultural_Regional": [
        "latin", "salsa", "bossa nova", "asian", "k-pop", "celtic", "african", "reggae", "bollywood", "world", "culture", "regional", "flamenco", "tango"
    ],
    "15_Holiday_Sazonal_Natal_Feriados": [
        "christmas", "xmas", "holiday", "santa", "halloween", "easter", "new year", "festive", "carol"
    ],
    "16_Kids_Infantil_Games_Escola": [
        "kids", "children", "game", "8bit", "arcade", "cute", "school", "baby", "toy", "nursery"
    ],
    "17_Vocals_Cancoes_Com_Letra": [
        "lyrical", "vocal", "singer", "lyrics", "song", "voice"
    ],
    "18_Jazz_Blues_Classy_Sophisticated": [
        "jazz", "blues", "saxophone", "swing", "lounge jazz", "smooth", "noir", "classy", "sophisticated", "bar", "restaurant"
    ],
    "19_Electronic_Dance_Club_House_Techno": [
        "edm", "house", "techno", "dubstep", "trance", "club", "rave", "party", "dance", "beat", "festival"
    ],
    "20_Experimental_Abstract_SoundDesign": [
        "experimental", "abstract", "sound design", "glitch", "texture", "drone", "avant garde", "noise", "industrial", "fx", "atmosphere", "weird"
    ]
}

def normalizar_texto(texto):
    if not texto: return ""
    return re.sub(r'[^\w\s]', ' ', texto.lower())

def ler_metadados(caminho_arquivo):
    """
    Tenta ler Artista e Gênero de dentro do arquivo de áudio.
    Retorna uma string combinada para busca.
    """
    try:
        audio = MutagenFile(caminho_arquivo, easy=True)
        if audio:
            # Tenta pegar tags comuns (ID3, Vorbis, MP4)
            # easy=True no MutagenFile tenta simplificar, mas varia por formato.
            # Vamos tentar acessar chaves comuns de forma genérica.
            tags = []
            
            # Artista
            if 'artist' in audio: tags.extend(audio['artist'])
            elif 'author' in audio: tags.extend(audio['author'])
            
            # Gênero
            if 'genre' in audio: tags.extend(audio['genre'])
            
            # Título (às vezes o estilo está no título)
            if 'title' in audio: tags.extend(audio['title'])
            
            return " ".join(tags)
    except Exception:
        pass
    return ""

class AudioOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração da Janela
        self.title("Audio Organizer v2.0 - Ultimate Edition")
        self.geometry("900x650")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Cabeçalho
        self.header_frame = ctk.CTkFrame(self, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="AI AUDIO ORGANIZER", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=10)
        
        self.subtitle_label = ctk.CTkLabel(self.header_frame, text="Metadata Analysis & Smart Sorting", font=ctk.CTkFont(size=14))
        self.subtitle_label.pack(pady=(0, 10))

        # Controles
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
        self.controls_frame.grid_columnconfigure(1, weight=1)

        self.btn_select_folder = ctk.CTkButton(self.controls_frame, text="Selecionar Pasta", command=self.selecionar_pasta)
        self.btn_select_folder.grid(row=0, column=0, padx=10, pady=10)

        self.entry_path = ctk.CTkEntry(self.controls_frame, placeholder_text="Caminho da pasta...")
        self.entry_path.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.entry_path.insert(0, os.path.join(os.getcwd(), PASTA_ENTRADA_PADRAO))

        self.btn_run = ctk.CTkButton(self.controls_frame, text="ORGANIZAR AGORA", fg_color="#2CC985", text_color="black", command=self.iniciar_thread_organizacao)
        self.btn_run.grid(row=0, column=2, padx=10, pady=10)

        # Log Area
        self.log_textbox = ctk.CTkTextbox(self, font=("Consolas", 12))
        self.log_textbox.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.log_textbox.insert("0.0", ">>> Aguardando comando...\n")

        # Barra de Status/Progresso
        self.progressbar = ctk.CTkProgressBar(self)
        self.progressbar.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.progressbar.set(0)

    def log(self, mensagem, tipo="info"):
        """Adiciona mensagens ao log com cores simuladas (via tags se possível ou apenas texto)"""
        prefixo = " [INFO] "
        if tipo == "success": prefixo = " [OK] "
        elif tipo == "error": prefixo = " [ERRO] "
        elif tipo == "warn": prefixo = " [!] "
        
        texto = f"{prefixo}{mensagem}\n"
        self.log_textbox.insert("end", texto)
        self.log_textbox.see("end")

    def selecionar_pasta(self):
        folder = filedialog.askdirectory()
        if folder:
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, folder)

    def iniciar_thread_organizacao(self):
        # Roda em thread separada para não travar a interface
        thread = threading.Thread(target=self.organizar)
        thread.start()

    def organizar(self):
        self.btn_run.configure(state="disabled")
        caminho_entrada = self.entry_path.get()
        
        if not os.path.exists(caminho_entrada):
            try:
                os.makedirs(caminho_entrada)
                self.log(f"Pasta criada: {caminho_entrada}", "info")
            except Exception as e:
                self.log(f"Não foi possível criar a pasta: {e}", "error")
                self.btn_run.configure(state="normal")
                return

        # 1. Criação da Estrutura
        self.log("Verificando estrutura de pastas...", "info")
        pastas_necessarias = list(REGRAS_PALAVRAS.keys()) + ["07_Hits_Brasileiros_Copyright_Cuidado", "08_Outros_Nao_Classificados"]
        root_dir = os.path.dirname(caminho_entrada) if "_ENTRADA" in caminho_entrada else caminho_entrada
        
        # Se o usuário escolheu uma pasta que não é a padrão, criamos as categorias DENTRO dela ou NO MESMO NÍVEL?
        # Lógica original: pastas ficam na raiz do script. Vamos manter para não bagunçar o PC do usuário,
        # MAS se ele selecionou uma pasta específica, o ideal é organizar PARA lá ou DE lá para a raiz?
        # Padrão V1: Organiza da pasta de entrada para pastas na raiz do software.
        # Vamos manter o padrão V1 por segurança, mas permitir que o usuário saiba.
        base_destino = os.getcwd() 

        for pasta in pastas_necessarias:
            caminho_p = os.path.join(base_destino, pasta)
            if not os.path.exists(caminho_p):
                os.makedirs(caminho_p)

        # 2. Varredura
        self.log(f"Escaneando arquivos em: {caminho_entrada}", "info")
        arquivos_encontrados = []
        extensores_validos = ('.mp3', '.wav', '.aiff', '.flac', '.ogg', '.m4a', '.wma')

        for root, dirs, files in os.walk(caminho_entrada):
            for file in files:
                if file.lower().endswith(extensores_validos):
                    arquivos_encontrados.append(os.path.join(root, file))

        total = len(arquivos_encontrados)
        if total == 0:
            self.log("Nenhum arquivo de áudio encontrado.", "warn")
            self.btn_run.configure(state="normal")
            return

        self.log(f"Encontrados {total} arquivos. Iniciando processamento...", "info")
        
        movidos = 0
        stats = {}

        for i, caminho_origem in enumerate(arquivos_encontrados):
            # Atualiza barra de progresso
            progresso = (i + 1) / total
            self.progressbar.set(progresso)

            arquivo = os.path.basename(caminho_origem)
            
            # --- ANÁLISE HÍBRIDA (Nome + Metadados) ---
            
            # 1. Nome do arquivo
            texto_analise = normalizar_texto(arquivo)
            
            # 2. Metadados (se disponível)
            metadados = ler_metadados(caminho_origem)
            if metadados:
                texto_analise += " " + normalizar_texto(metadados)
                # self.log(f"Lendo metadados de {arquivo}: {metadados}", "info") # Verbose debug

            destino_final = None
            motivo = ""

            # Check de Artistas
            for artista, pasta in ARTISTAS_CONHECIDOS.items():
                if artista in texto_analise:
                    destino_final = pasta
                    motivo = f"Artista Detectado ({artista})"
                    break
            
            # Check de Gênero/Keywords
            if not destino_final:
                for pasta, keywords in REGRAS_PALAVRAS.items():
                    for keyword in keywords:
                        padrao = r"\b" + re.escape(keyword) + r"\b"
                        if re.search(padrao, texto_analise):
                            destino_final = pasta
                            motivo = f"Keyword: {keyword.upper()}"
                            break
                    if destino_final: break

            # Regras Especiais
            if not destino_final and "artlist musical logos" in texto_analise:
                 destino_final = "05_Vinhetas_Logos_Sonoros_Abaixo_30s"
                 motivo = "Padrão Artlist Logo"

            # --- MOVIMENTAÇÃO ---
            if destino_final:
                caminho_destino_pasta = os.path.join(base_destino, destino_final)
                if not os.path.exists(caminho_destino_pasta):
                    os.makedirs(caminho_destino_pasta)

                destino = os.path.join(caminho_destino_pasta, arquivo)
                
                # Duplicatas
                if os.path.exists(destino):
                    base, ext = os.path.splitext(arquivo)
                    destino = os.path.join(caminho_destino_pasta, f"{base}_{int(time.time())}{ext}")

                try:
                    shutil.move(caminho_origem, destino)
                    self.log(f"Movido: {arquivo} -> {destino_final.split('_', 1)[1]} [{motivo}]", "success")
                    stats[destino_final] = stats.get(destino_final, 0) + 1
                    movidos += 1
                except Exception as e:
                    self.log(f"Erro ao mover {arquivo}: {str(e)}", "error")
            else:
                self.log(f"Não Classificado: {arquivo}", "warn")

        # Limpeza de pastas vazias
        try:
             # Remove pastas vazias recursivamente na origem, mas com cuidado
             for root, dirs, files in os.walk(caminho_entrada, topdown=False):
                for name in dirs:
                    try:
                        os.rmdir(os.path.join(root, name))
                    except:
                        pass
        except:
            pass

        self.log("-" * 40, "info")
        self.log(f"PROCESSAMENTO CONCLUÍDO. {movidos}/{total} arquivos organizados.", "success")
        self.btn_run.configure(state="normal")

def main():
    app = AudioOrganizerApp()
    app.mainloop()

if __name__ == "__main__":
    main()

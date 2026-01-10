import os
import shutil
import re
import time
import sys

# Ativa cores no Windows 10/11
os.system('color')

# ==============================================================================
# UI & DESIGN SYSTEM
# ==============================================================================
class C:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'
    WHITE = '\033[97m'
    MAGENTA = '\033[95m'

def print_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(C.CYAN + C.BOLD)
    print(r'''
    ██████╗  █████╗  ██████╗██╗  ██╗    ███╗   ███╗██╗   ██╗███████╗██╗ ██████╗ 
    ██╔══██╗██╔══██╗██╔════╝██║ ██╔╝    ████╗ ████║██║   ██║██╔════╝██║██╔════╝ 
    ██████╔╝███████║██║     █████╔╝     ██╔████╔██║██║   ██║███████╗██║██║      
    ██╔═══╝ ██╔══██║██║     ██╔═██╗     ██║╚██╔╝██║██║   ██║╚════██║██║██║      
    ██║     ██║  ██║╚██████╗██║  ██╗    ██║ ╚═╝ ██║╚██████╔╝███████║██║╚██████╗ 
    ╚═╝     ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝ ╚═════╝ 
                                                      AI AUDIO ORGANIZER v3.0
    ''' + C.END)
    print(C.WHITE + "    " + "—" * 70 + C.END)

def loading_bar(total):
    print(f"\n    {C.YELLOW}⚡ INICIALIZANDO SCANNER DE ÁUDIO...{C.END}")
    time.sleep(1)
    # Simulação de carregamento
    sys.stdout.write("    ")
    for i in range(30):
        sys.stdout.write("█")
        sys.stdout.flush()
        time.sleep(0.02)
    print(f" {C.GREEN}100%{C.END}\n")

# ==============================================================================
# CONFIGURAÇÃO GERAL & INTELEGÊNCIA
# ==============================================================================
PASTA_ENTRADA = "_ENTRADA_DE_MUSICAS"

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

# MAPA MESTRE - ARTLIST MOODS & GENRES (Tradução para o Sistema)
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
    return re.sub(r'[^\w\s]', ' ', texto.lower())

def organizar():
    print_banner()
    caminho_entrada = os.path.join(os.getcwd(), PASTA_ENTRADA)
    
    if not os.path.exists(caminho_entrada):
        os.makedirs(caminho_entrada)

    # VARREDURA PROFUNDA (Deep Scan)
    arquivos_encontrados = []
    extensores_validos = ('.mp3', '.wav', '.aiff', '.flac', '.ogg', '.m4a', '.wma')

    print(f"    {C.CYAN}🔎 ESCANEANDO SUBPASTAS...{C.END}")
    
    for root, dirs, files in os.walk(caminho_entrada):
        for file in files:
            if file.lower().endswith(extensores_validos):
                caminho_completo = os.path.join(root, file)
                arquivos_encontrados.append(caminho_completo)
    
    if not arquivos_encontrados:
        print(f"\n    {C.RED}❌ NENHUM ARQUIVO DE ÁUDIO ENCONTRADO EM: {PASTA_ENTRADA} (NEM NAS SUBPASTAS){C.END}")
        return

    loading_bar(len(arquivos_encontrados))
    
    stats = {}
    movidos = 0

    print(f"    {C.WHITE}PROCESSANDO {len(arquivos_encontrados)} ARQUIVO(S)...{C.END}\n")

    for caminho_origem in arquivos_encontrados:
        arquivo = os.path.basename(caminho_origem) # Nome do arquivo
        nome_lower = normalizar_texto(arquivo)
        destino_final = None
        motivo = ""

        # Identificação
        for artista, pasta in ARTISTAS_CONHECIDOS.items():
            if artista in nome_lower:
                destino_final = pasta
                motivo = f"🎤 ARTISTA DETECTADO: {C.CYAN}{artista.title()}{C.END}"
                break
        
        if not destino_final:
            for pasta, keywords in REGRAS_PALAVRAS.items():
                for keyword in keywords:
                    padrao = r"\b" + re.escape(keyword) + r"\b"
                    if re.search(padrao, nome_lower):
                        destino_final = pasta
                        motivo = f"🧠 GENERO IDENTIFICADO: {C.YELLOW}{keyword.upper()}{C.END}"
                        break
                if destino_final: break

        if not destino_final and "artlist musical logos" in nome_lower:
             destino_final = "05_Vinhetas_Logos_Sonoros_Abaixo_30s"
             motivo = "🏷️ PADRAO LOGO ARTLIST"

        # Interface Visual do "Card"
        if destino_final:
            # Cria pasta de destino se não existir (importante para a nova pasta 20)
            caminho_destino_pasta = os.path.join(os.getcwd(), destino_final)
            if not os.path.exists(caminho_destino_pasta):
                os.makedirs(caminho_destino_pasta)

            destino = os.path.join(caminho_destino_pasta, arquivo)
            
            # Tratamento para duplicatas
            if os.path.exists(destino):
                base, ext = os.path.splitext(arquivo)
                destino = os.path.join(caminho_destino_pasta, f"{base}_{int(time.time())}{ext}")

            nome_display = (arquivo[:45] + '..') if len(arquivo) > 45 else arquivo
            pasta_display = destino_final.split('_', 1)[1].replace('_', ' ')

            try:
                shutil.move(caminho_origem, destino)
                print(f"    {C.WHITE}┌── 🎵 {C.BOLD}{nome_display}{C.END}")
                print(f"    {C.WHITE}│   ├── 📂 {C.GREEN}{pasta_display}{C.END}")
                print(f"    {C.WHITE}│   └── ✨ {motivo}")
                print(f"    {C.WHITE}└── {C.GREEN}✅ MOVIDO COM SUCESSO{C.END}\n")
                
                stats[destino_final] = stats.get(destino_final, 0) + 1
                movidos += 1
                time.sleep(0.1) 
            except Exception as e:
                print(f"    {C.RED}┌── ❌ ERRO AO MOVER: {arquivo}{C.END}")
                print(f"    {C.RED}└── {str(e)}{C.END}\n")
        else:
            print(f"    {C.WHITE}┌── 🎵 {C.BOLD}{arquivo}{C.END}")
            print(f"    {C.WHITE}└── ⚠️ {C.RED}NÃO CLASSIFICADO{C.END}\n")

    # Limpeza de pastas vazias na origem (opcional, mas elegante)
    # Tenta remover as pastas de onde os arquivos saíram se elas ficaram vazias
    try:
        if os.path.dirname(caminho_origem) != caminho_entrada:
             os.rmdir(os.path.dirname(caminho_origem))
    except:
        pass # Se não estiver vazia, ignora

    # Resumo Final
    print(f"    {C.WHITE}—" * 70 + C.END)
    print(f"    {C.CYAN}📊 ESTATÍSTICAS DA SESSÃO:{C.END}")
    if stats:
        for pasta, qtd in stats.items():
            nome_pasta_clean = pasta.split('_', 1)[1].replace('_', ' ')
            print(f"       • {str(qtd).zfill(2)} x {C.GREEN}{nome_pasta_clean}{C.END}")
    print(f"\n    {C.MAGENTA}🚀 CONCLUÍDO! {movidos} ARQUIVOS ORGANIZADOS.{C.END}")
    print(f"    {C.WHITE}—" * 70 + C.END)

if __name__ == "__main__":
    organizar()
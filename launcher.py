import os
import time
import sys
import requests
import shutil # Necessário para o script baixado
import re     # Necessário para o script baixado

# Configurações
GITHUB_USER = "tgriebell"
REPO_NAME = "audio-organizer-server"
BRANCH = "main"

# URLs
BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}"
VERSION_URL = f"{BASE_URL}/version.txt"
SCRIPT_URL = f"{BASE_URL}/organizar_musicas.py"

# Arquivos Locais
LOCAL_SCRIPT = "organizar_musicas.py"
LOCAL_VERSION = "version.txt"

# Cores
class C:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'
    WHITE = '\033[97m'
    bg_BLUE = '\033[44m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear_screen()
    print(C.CYAN + "╔════════════════════════════════════════════════════════════════╗")
    print("║                                                                ║")
    print(f"║   {C.BOLD}{C.WHITE}AUDIO ORGANIZER - SYSTEM UPDATE MANAGER{C.END}{C.CYAN}                      ║")
    print("║   v1.1 - Connected to GitHub Server                            ║")
    print("║                                                                ║")
    print("╚════════════════════════════════════════════════════════════════╝" + C.END)
    print("")

def get_remote_version():
    try:
        response = requests.get(VERSION_URL, timeout=5)
        if response.status_code == 200:
            return response.text.strip()
        return None
    except:
        return None

def get_local_version():
    if os.path.exists(LOCAL_VERSION):
        with open(LOCAL_VERSION, "r") as f:
            return f.read().strip()
    return "0.0"

def update_file(url, local_filename):
    print(f"    {C.YELLOW}⚡ BAIXANDO ATUALIZAÇÃO: {local_filename}...{C.END}")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(local_filename, "wb") as f:
                f.write(response.content)
            print(f"    {C.GREEN}✔ DOWNLOAD CONCLUÍDO.{C.END}")
            return True
        else:
            print(f"    {C.RED}❌ FALHA NO DOWNLOAD.{C.END}")
            return False
    except Exception as e:
        print(f"    {C.RED}❌ ERRO DE CONEXÃO: {e}{C.END}")
        return False

def main():
    os.system('color')
    print_header()
    
    print(f"    {C.CYAN}📡 VERIFICANDO ATUALIZAÇÕES...{C.END}")
    time.sleep(1)

    remote_ver = get_remote_version()
    local_ver = get_local_version()

    if remote_ver and remote_ver != local_ver:
        print(f"\n    {C.YELLOW}⚠️  NOVA VERSÃO ENCONTRADA!{C.END}")
        print(f"    {C.WHITE}Versão Atual: {local_ver}  >>>  Nova Versão: {remote_ver}{C.END}\n")
        
        time.sleep(1)
        
        if update_file(SCRIPT_URL, LOCAL_SCRIPT):
            with open(LOCAL_VERSION, "w") as f:
                f.write(remote_ver)
            print(f"\n    {C.GREEN}🚀 SISTEMA ATUALIZADO COM SUCESSO!{C.END}")
            time.sleep(1.5)
        else:
            print(f"\n    {C.RED}❌ ERRO NA ATUALIZAÇÃO. MANTENDO VERSÃO ATUAL.{C.END}")
            time.sleep(2)
    
    else:
        print(f"    {C.GREEN}✔ SEU SISTEMA ESTÁ ATUALIZADO ({local_ver}).{C.END}")
        time.sleep(1)

    print(f"\n    {C.CYAN}🔌 INICIANDO ORGANIZADOR...{C.END}")
    print("    " + "—" * 60 + "\n")
    time.sleep(1)
    
    # MÁGICA: Executa o script baixado dentro deste processo
    try:
        if os.path.exists(LOCAL_SCRIPT):
            with open(LOCAL_SCRIPT, "r", encoding="utf-8") as script_file:
                codigo = script_file.read()
            
            # Cria um escopo seguro e executa o código
            escopo = globals().copy()
            exec(codigo, escopo)
            
            # Se o script tiver a função organizar(), chama ela
            if "organizar" in escopo:
                escopo["organizar"]()
            elif "main" in escopo:
                escopo["main"]()
        else:
            print(f"    {C.RED}❌ ERRO: ARQUIVO DO SISTEMA NÃO ENCONTRADO.{C.END}")
            print(f"    {C.RED}Por favor, verifique sua conexão e reinicie.{C.END}")
            input()
            
    except Exception as e:
        print(f"\n    {C.RED}❌ ERRO FATAL DURANTE A EXECUÇÃO:{C.END}")
        print(f"    {e}")
        print(f"\n    {C.WHITE}Pressione ENTER para sair...{C.END}")
        input()
    
    # Pausa final para o usuário ver o resultado
    print(f"\n    {C.CYAN}✅ SISTEMA ENCERRADO.{C.END}")
    print(f"    {C.WHITE}Pressione ENTER para fechar a janela...{C.END}")
    input()

if __name__ == "__main__":
    main()

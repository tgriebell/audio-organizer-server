import os
import sys
import requests
import time
import threading
import tempfile
import customtkinter as ctk
from PIL import Image, ImageTk

# Imports forçados para o PyInstaller (Hooks)
try:
    import mutagen
except ImportError:
    pass

# Configurações do GitHub
GITHUB_USER = "tgriebell"
REPO_NAME = "audio-organizer-server"
BRANCH = "main"

# URLs
BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}"
VERSION_URL = f"{BASE_URL}/version.txt"
SCRIPT_URL = f"{BASE_URL}/organizar_musicas.py"

# Configuração de Arquivos (MODO SILENCIOSO - PASTA TEMP)
TEMP_DIR = os.path.join(tempfile.gettempdir(), "AudioOrganizer_Cache")
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

LOCAL_SCRIPT = os.path.join(TEMP_DIR, "core_v2.py")
LOCAL_VERSION = os.path.join(TEMP_DIR, "version.txt")

# Interface da Splash Screen (O Launcher Gráfico)
class SplashScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuração da Janela (Sem bordas, centro da tela)
        self.overrideredirect(True) # Remove barra de título e botões
        self.geometry("400x250")
        self.eval('tk::PlaceWindow . center') # Tenta centralizar
        
        # Centralização manual para garantir
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width/2) - (400/2)
        y = (screen_height/2) - (250/2)
        self.geometry('%dx%d+%d+%d' % (400, 250, x, y))

        self.configure(fg_color="#1a1a1a")

        # UI Elements
        self.lbl_title = ctk.CTkLabel(self, text="AUDIO ORGANIZER", font=("Roboto", 24, "bold"), text_color="#2CC985")
        self.lbl_title.pack(pady=(50, 10))

        self.lbl_status = ctk.CTkLabel(self, text="Iniciando...", font=("Roboto", 12), text_color="gray")
        self.lbl_status.pack(pady=5)

        self.progress = ctk.CTkProgressBar(self, width=300, height=10, progress_color="#2CC985")
        self.progress.pack(pady=20)
        self.progress.set(0)

        self.lbl_version = ctk.CTkLabel(self, text="v2.0 Launcher", font=("Roboto", 10), text_color="#444")
        self.lbl_version.pack(side="bottom", pady=10)

        # Inicia o processo em background
        self.after(500, self.start_update_process)

    def update_status(self, text, progress_val):
        self.lbl_status.configure(text=text)
        self.progress.set(progress_val)
        self.update()

    def start_update_process(self):
        thread = threading.Thread(target=self.run_updater)
        thread.start()

    def get_remote_version(self):
        try:
            response = requests.get(VERSION_URL, timeout=5)
            if response.status_code == 200:
                return response.text.strip()
        except:
            pass
        return None

    def get_local_version(self):
        if os.path.exists(LOCAL_VERSION):
            with open(LOCAL_VERSION, "r") as f:
                return f.read().strip()
        return "0.0"

    def download_core(self):
        try:
            response = requests.get(SCRIPT_URL)
            if response.status_code == 200:
                with open(LOCAL_SCRIPT, "wb") as f: # Salva como binário para garantir codificação
                    f.write(response.content)
                return True
        except:
            pass
        return False

    def run_updater(self):
        self.update_status("Conectando ao servidor...", 0.2)
        time.sleep(0.5)

        remote_ver = self.get_remote_version()
        local_ver = self.get_local_version()

        if remote_ver and remote_ver != local_ver:
            self.update_status(f"Atualizando: {local_ver} -> {remote_ver}", 0.5)
            if self.download_core():
                with open(LOCAL_VERSION, "w") as f:
                    f.write(remote_ver)
                self.update_status("Atualização concluída!", 0.9)
            else:
                self.update_status("Falha no download. Usando versão local.", 0.9)
        else:
            self.update_status("Sistema atualizado.", 0.8)
            
        time.sleep(0.5)
        self.update_status("Carregando Interface...", 1.0)
        time.sleep(0.5)
        
        # Fecha a Splash Screen e Inicia o App Principal
        self.destroy()
        self.launch_app()

    def launch_app(self):
        # Executa o script baixado
        if os.path.exists(LOCAL_SCRIPT):
            try:
                # Ler o arquivo garantindo UTF-8
                with open(LOCAL_SCRIPT, "r", encoding="utf-8") as script_file:
                    codigo = script_file.read()
                
                # Prepara o ambiente global
                escopo = globals().copy()
                
                # Executa
                exec(codigo, escopo)
                
                # Tenta chamar a função main se existir
                if "main" in escopo:
                    escopo["main"]()
            except Exception as e:
                # Se der erro no app principal, mostra um popup de erro simples
                import tkinter.messagebox
                tkinter.messagebox.showerror("Erro Fatal", f"Ocorreu um erro ao iniciar o núcleo:\n{e}")
        else:
            import tkinter.messagebox
            tkinter.messagebox.showerror("Erro", "Arquivo do sistema não encontrado.\nVerifique sua internet e tente novamente.")

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    app = SplashScreen()
    app.mainloop()
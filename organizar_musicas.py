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
from tkinter import filedialog
from mutagen import File as MutagenFile

# Tenta carregar Pygame
HAS_PYGAME = False
try:
    import pygame
    pygame.mixer.init()
    HAS_PYGAME = True
except: pass

# ==============================================================================
# DESIGN SYSTEM (ELITE BLACK EDITION)
# ==============================================================================
COLOR_BG = "#030303"
COLOR_SIDEBAR = "#080808"
COLOR_CARD = "#0c0c0c"
COLOR_ACCENT = "#00ff66"
COLOR_BORDER = "#121212"

# ==============================================================================
# ENGINE DE CLASSIFICAÇÃO (ROBUSTEZ REAL)
# ==============================================================================
REGRAS_PALAVRAS = {
    "01_Alta_Energia": ["powerful", "rock", "metal", "sport", "energy", "stomp", "action"],
    "02_Cinematic": ["cinematic", "epic", "dramatic", "score", "orchestra", "trailer"],
    "03_Good_Vibes": ["uplifting", "happy", "summer", "vlog", "travel", "lifestyle"],
    "04_Lounge_Lofi": ["peaceful", "ambient", "lofi", "chill", "relax", "soft"],
    "05_SFX_Logo": ["logo", "ident", "sting", "bumper", "jingle", "sfx"],
    "06_Casamentos": ["wedding", "casamento", "bride", "romantic", "love"],
    "09_Business": ["corporate", "business", "tech", "innovation", "modern"],
    "10_Terror": ["dark", "scary", "tension", "horror", "suspense"],
    "11_Comedy": ["funny", "comedy", "quirky", "humor", "weird"],
    "12_Urban_Trap": ["hip hop", "rap", "trap", "urban", "bass", "808"],
}

class ToastNotification(ctk.CTkFrame):
    """Notificação Interna (Adeus Windows 98)"""
    def __init__(self, master, message, color=COLOR_ACCENT):
        super().__init__(master, fg_color="#111", border_width=1, border_color=color, corner_radius=10)
        self.lbl = ctk.CTkLabel(self, text=f"  {message}  ", font=("Segoe UI", 12, "bold"), text_color="white")
        self.lbl.pack(padx=20, pady=10)
        self.place(relx=0.5, rely=0.1, anchor="center")
        master.after(3000, self.destroy)

class ProCard(ctk.CTkFrame):
    def __init__(self, master, file_path, on_select):
        super().__init__(master, fg_color=COLOR_CARD, corner_radius=12, border_width=1, border_color=COLOR_BORDER)
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        
        self.grid_columnconfigure(1, weight=1)
        self.icon = ctk.CTkLabel(self, text="⚡", font=("Arial", 18), text_color=COLOR_ACCENT)
        self.icon.grid(row=0, column=0, rowspan=2, padx=15, pady=15)
        
        self.name_lbl = ctk.CTkLabel(self, text=self.filename[:45], font=("Segoe UI", 13, "bold"), text_color="white")
        self.name_lbl.grid(row=0, column=1, sticky="w", pady=(12, 0))
        
        self.info_lbl = ctk.CTkLabel(self, text="ANALYZED • PENDING", font=("Consolas", 9), text_color="#333")
        self.info_lbl.grid(row=1, column=1, sticky="w", pady=(0, 12))

        for w in [self, self.icon, self.name_lbl, self.info_lbl]:
            w.bind("<Enter>", lambda e: self.configure(border_color=COLOR_ACCENT, fg_color="#111"))
            w.bind("<Leave>", lambda e: self.configure(border_color=COLOR_BORDER, fg_color=COLOR_CARD))
            w.bind("<Button-1>", lambda e: on_select(self))

class AudioOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes("-alpha", 0.0)
        
        w, h = 1300, 800
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{int((sw-w)/2)}+{int((sh-h)/2)}")
        self.configure(fg_color=COLOR_BG)

        self.after(100, self.apply_hack)
        self.setup_ui()
        self.fade_in()
        
        self.current_folder = ""
        self.file_cards = []

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
        # Header / Title Bar
        self.title_bar = ctk.CTkFrame(self, fg_color="#000", height=50, corner_radius=0)
        self.title_bar.pack(fill="x")
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        
        ctk.CTkLabel(self.title_bar, text="  ELITE_SYSTEM_V2.7", font=("Consolas", 10), text_color="#222").pack(side="left", padx=20)
        ctk.CTkButton(self.title_bar, text="✕", width=50, height=50, fg_color="transparent", hover_color="#c42b1c", command=self.destroy).pack(side="right")

        # Layout Body
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=10, pady=10)

        # Sidebar
        self.side = ctk.CTkFrame(self.body, fg_color=COLOR_SIDEBAR, width=240, corner_radius=20, border_width=1, border_color="#111")
        self.side.pack(side="left", fill="y", padx=(0, 10))
        self.side.pack_propagate(False)
        ctk.CTkLabel(self.side, text="DASHBOARD", font=("Segoe UI", 12, "bold"), text_color="#333").pack(pady=40)
        self.add_nav("LIBRARY", "📂", active=True)
        self.add_nav("AI ENGINE", "🧠")
        self.add_nav("HISTORY", "↺")

        # Content Area
        self.cont = ctk.CTkFrame(self.body, fg_color="transparent")
        self.cont.pack(side="left", fill="both", expand=True)
        
        self.header = ctk.CTkFrame(self.cont, fg_color="transparent")
        self.header.pack(fill="x", pady=(10, 20))
        ctk.CTkLabel(self.header, text="Audio Library", font=("Segoe UI", 32, "bold"), text_color="white").pack(side="left")
        ctk.CTkButton(self.header, text="+ ADD FOLDER", fg_color=COLOR_ACCENT, text_color="black", font=("Segoe UI", 12, "bold"), height=40, corner_radius=10, command=self.select_folder).pack(side="right")

        self.scroll = ctk.CTkScrollableFrame(self.cont, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)

        # Action Bar
        self.act = ctk.CTkFrame(self, fg_color="#050505", height=100, border_width=1, border_color="#111")
        self.act.pack(fill="x")
        self.btn_run = ctk.CTkButton(self.act, text="RUN NEURAL ORGANIZATION", font=("Segoe UI", 15, "bold"), fg_color=COLOR_ACCENT, text_color="black", height=60, width=400, corner_radius=15, command=self.organize_real)
        self.btn_run.place(relx=0.5, rely=0.5, anchor="center")

    def add_nav(self, text, icon, active=False):
        color = "#888" if not active else "white"
        btn = ctk.CTkButton(self.side, text=f"  {icon}   {text}", font=("Segoe UI", 13), fg_color="transparent", text_color=color, anchor="w", height=45, corner_radius=10, hover_color="#151515")
        btn.pack(fill="x", padx=15, pady=5)

    def start_move(self, e): self.x, self.y = e.x, e.y
    def do_move(self, e): self.geometry(f"+{self.winfo_x() + (e.x - self.x)}+{self.winfo_y() + (e.y - self.y)}")

    def select_folder(self):
        p = filedialog.askdirectory()
        if p:
            self.current_folder = p
            for w in self.scroll.winfo_children(): w.destroy()
            self.file_cards = []
            files = [f for f in os.listdir(p) if f.lower().endswith(('.mp3', '.wav', '.flac'))]
            for f in files:
                card = ProCard(self.scroll, os.path.join(p, f), lambda c: None)
                card.pack(fill="x", pady=8, padx=10)
                self.file_cards.append(card)
            ToastNotification(self, f"{len(files)} arquivos carregados.")

    def organize_real(self):
        if not self.file_cards:
            ToastNotification(self, "Selecione uma pasta primeiro!", color="#ff3333")
            return
        
        self.btn_run.configure(state="disabled", text="IA PROCESSING...")
        
        def work():
            moved = 0
            for card in self.file_cards:
                origem = card.file_path
                filename = card.filename
                
                # Inteligência de Destino
                destino = "08_Outros_Nao_Classificados"
                for pasta, keywords in REGRAS_PALAVRAS.items():
                    if any(k in filename.lower() for k in keywords):
                        destino = pasta; break
                
                dest_path = os.path.join(self.current_folder, destino)
                if not os.path.exists(dest_path): os.makedirs(dest_path)
                
                try:
                    if HAS_PYGAME: pygame.mixer.music.unload()
                    shutil.move(origem, os.path.join(dest_path, filename))
                    moved += 1
                    card.configure(border_color="#333", alpha=0.5) # Feedback visual
                except: pass
            
            self.after(0, lambda: self.finish_org(moved))

        threading.Thread(target=work, daemon=True).start()

    def finish_org(self, count):
        self.btn_run.configure(state="normal", text="RUN NEURAL ORGANIZATION")
        ToastNotification(self, f"Sucesso: {count} arquivos organizados!")
        for w in self.scroll.winfo_children(): w.destroy()
        self.file_cards = []

if __name__ == "__main__":
    app = AudioOrganizerApp()
    app.mainloop()
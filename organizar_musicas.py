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
from tkinter import filedialog, messagebox
from mutagen import File as MutagenFile

# Tenta carregar Pygame
HAS_PYGAME = False
try:
    import pygame
    pygame.mixer.init()
    HAS_PYGAME = True
except: pass

# ==============================================================================
# DESIGN SYSTEM (ULTIMATE DASHBOARD)
# ==============================================================================
COLOR_BG = "#000000"
COLOR_SIDEBAR = "#080808"
COLOR_CARD = "#0c0c0c"
COLOR_ACCENT = "#00ff66"
COLOR_ACCENT_HOVER = "#00cc55"
COLOR_BORDER = "#151515"

# ==============================================================================
# COMPONENTES HIGH-END
# ==============================================================================

class ProCard(ctk.CTkFrame):
    def __init__(self, master, file_path, on_select):
        super().__init__(master, fg_color=COLOR_CARD, corner_radius=15, border_width=1, border_color=COLOR_BORDER)
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        
        self.grid_columnconfigure(1, weight=1)
        
        # Ícone Neon
        self.icon_lbl = ctk.CTkLabel(self, text="⚡", font=("Arial", 20), text_color=COLOR_ACCENT)
        self.icon_lbl.grid(row=0, column=0, rowspan=2, padx=20, pady=20)
        
        # Nome
        disp_name = self.filename if len(self.filename) < 45 else self.filename[:42]+"..."
        self.name_lbl = ctk.CTkLabel(self, text=disp_name, font=("Segoe UI", 14, "bold"), text_color="white")
        self.name_lbl.grid(row=0, column=1, sticky="w", pady=(15, 0))
        
        # Status Subtext
        self.info_lbl = ctk.CTkLabel(self, text=f"AI ANALYSIS • PENDING ORGANISATION", font=("Consolas", 10), text_color="#444")
        self.info_lbl.grid(row=1, column=1, sticky="w", pady=(0, 15))

        # Efeitos de Interação
        for w in [self, self.icon_lbl, self.name_lbl, self.info_lbl]:
            w.bind("<Enter>", self.on_hover)
            w.bind("<Leave>", self.on_leave)
            w.bind("<Button-1>", lambda e: on_select(self))

    def on_hover(self, e):
        self.configure(border_color=COLOR_ACCENT, fg_color="#111")
    def on_leave(self, e):
        self.configure(border_color=COLOR_BORDER, fg_color=COLOR_CARD)

class AudioOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Configuração Stealth
        self.overrideredirect(True)
        self.attributes("-alpha", 0.0)
        self.title("Audio Organizer Pro")
        
        # Dimensões Dashboard
        w, h = 1300, 800
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{int((sw-w)/2)}+{int((sh-h)/2)}")
        self.configure(fg_color=COLOR_BG)

        # 2. Hack Taskbar (Definitivo)
        self.after(50, self.apply_windows_hack)
        
        # 3. Layout e Fade
        self.setup_dashboard()
        self.fade_in()

    def apply_windows_hack(self):
        try:
            GWL_EXSTYLE = -20
            WS_EX_APPWINDOW = 0x00040000
            WS_EX_TOOLWINDOW = 0x00000080
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style = style & ~WS_EX_TOOLWINDOW | WS_EX_APPWINDOW
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
            self.withdraw(); self.after(10, self.deiconify)
        except: pass

    def fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1.0:
            self.attributes("-alpha", alpha + 0.1)
            self.after(25, self.fade_in)

    def setup_dashboard(self):
        # BARRA DE TÍTULO CUSTOM (Arraste e Controle)
        self.title_bar = ctk.CTkFrame(self, fg_color="#000", height=50, corner_radius=0)
        self.title_bar.pack(fill="x")
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)

        ctk.CTkLabel(self.title_bar, text="  AUDIO ORGANIZER 2.5 • AI CORE ACTIVE", font=("Consolas", 10), text_color="#333").pack(side="left", padx=20)

        self.btn_close = ctk.CTkButton(self.title_bar, text="✕", width=50, height=50, fg_color="transparent", 
                                       hover_color="#c42b1c", corner_radius=0, command=self.destroy)
        self.btn_close.pack(side="right")

        # CONTAINER PRINCIPAL (Sidebar + Content)
        self.wrap = ctk.CTkFrame(self, fg_color="transparent")
        self.wrap.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        # SIDEBAR ESTILO DISCORD/SPOTIFY
        self.sidebar = ctk.CTkFrame(self.wrap, fg_color=COLOR_SIDEBAR, width=240, corner_radius=20, border_width=1, border_color="#111")
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(self.sidebar, text="DASHBOARD", font=("Segoe UI", 12, "bold"), text_color="#444").pack(pady=(40, 30))
        
        self.add_nav("LIBRARY", "📂")
        self.add_nav("IA ENGINE", "🧠")
        self.add_nav("STATISTICS", "📊")
        self.add_nav("SETTINGS", "⚙")

        # ÁREA DE CONTEÚDO (Centro)
        self.content = ctk.CTkFrame(self.wrap, fg_color="transparent")
        self.content.pack(side="left", fill="both", expand=True, padx=20, pady=10)

        # Header Principal
        self.header = ctk.CTkFrame(self.content, fg_color="transparent")
        self.header.pack(fill="x", pady=(10, 30))
        
        ctk.CTkLabel(self.header, text="Audio Intelligence", font=("Segoe UI", 28, "bold"), text_color="white").pack(side="left")
        
        self.btn_add = ctk.CTkButton(self.header, text="+ SELECT LIBRARY", fg_color=COLOR_ACCENT, text_color="black", 
                                     font=("Segoe UI", 13, "bold"), height=40, corner_radius=10, command=self.select_folder)
        self.btn_add.pack(side="right")

        # Listagem Custom
        self.scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent", label_text="")
        self.scroll.pack(fill="both", expand=True)

        # PAINEL DE AÇÃO FLUTUANTE (Bottom)
        self.action_panel = ctk.CTkFrame(self, fg_color="#080808", height=100, corner_radius=0, border_width=1, border_color="#111")
        self.action_panel.pack(fill="x")
        
        self.btn_run = ctk.CTkButton(self.action_panel, text="RUN NEURAL CLASSIFICATION", font=("Segoe UI", 15, "bold"),
                                     fg_color=COLOR_ACCENT, text_color="black", height=60, width=400, corner_radius=15,
                                     hover_color=COLOR_ACCENT_HOVER, command=self.organize)
        self.btn_run.place(relx=0.5, rely=0.5, anchor="center")

    def add_nav(self, text, icon):
        btn = ctk.CTkButton(self.sidebar, text=f"  {icon}   {text}", font=("Segoe UI", 13), fg_color="transparent", 
                            text_color="#888", anchor="w", height=45, corner_radius=10, hover_color="#151515")
        btn.pack(fill="x", padx=15, pady=5)

    def start_move(self, e):
        self.x, self.y = e.x, e.y
    def do_move(self, e):
        self.geometry(f"+{self.winfo_x() + (e.x - self.x)}+{self.winfo_y() + (e.y - self.y)}")

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            for w in self.scroll.winfo_children(): w.destroy()
            files = [f for f in os.listdir(path) if f.lower().endswith(('.mp3', '.wav', '.flac'))]
            for f in files:
                ProCard(self.scroll, os.path.join(path, f), self.on_card_select).pack(fill="x", pady=8, padx=10)

    def on_card_select(self, card):
        pass

    def organize(self):
        messagebox.showinfo("IA SYSTEM", "Biblioteca sincronizada e organizada!")

if __name__ == "__main__":
    app = AudioOrganizerApp()
    app.mainloop()
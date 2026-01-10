import os
import shutil
import re
import time
import sys
import threading
import random
import ctypes
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
# DESIGN SYSTEM (ULTIMATE PRO)
# ==============================================================================
COLOR_BG = "#000000"
COLOR_SIDEBAR = "#080808"
COLOR_CARD = "#0c0c0c"
COLOR_ACCENT = "#00ff66"
COLOR_ACCENT_HOVER = "#00cc55"
COLOR_BORDER = "#1a1a1a"

# ==============================================================================
# COMPONENTES PRO
# ==============================================================================

class GlassCard(ctk.CTkFrame):
    def __init__(self, master, file_path, on_select):
        super().__init__(master, fg_color=COLOR_CARD, corner_radius=12, border_width=1, border_color="#111")
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        
        # Layout
        self.grid_columnconfigure(1, weight=1)
        
        # Ícone de Audio Estilizado
        self.icon_lbl = ctk.CTkLabel(self, text="⚡", font=("Arial", 18), text_color=COLOR_ACCENT)
        self.icon_lbl.grid(row=0, column=0, rowspan=2, padx=15, pady=15)
        
        # Nome
        disp_name = self.filename if len(self.filename) < 40 else self.filename[:37]+"..."
        self.name_lbl = ctk.CTkLabel(self, text=disp_name, font=("Inter", 13, "bold"), text_color="white")
        self.name_lbl.grid(row=0, column=1, sticky="w", pady=(12, 0))
        
        # Sub-texto (Metadados Falsos/IA para visual)
        self.info_lbl = ctk.CTkLabel(self, text=f"SCANNING SPECTROGRAM • READY", font=("Consolas", 9), text_color="#444")
        self.info_lbl.grid(row=1, column=1, sticky="w", pady=(0, 12))

        # Eventos
        for w in [self, self.icon_lbl, self.name_lbl, self.info_lbl]:
            w.bind("<Enter>", self.on_hover)
            w.bind("<Leave>", self.on_leave)
            w.bind("<Button-1>", lambda e: on_select(self))

    def on_hover(self, e):
        self.configure(border_color=COLOR_ACCENT, fg_color="#111")
    def on_leave(self, e):
        self.configure(border_color="#111", fg_color=COLOR_CARD)

class AudioOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Janela Frameless & Taskbar
        self.overrideredirect(True)
        self.attributes("-alpha", 0.0)
        self.title("Audio Organizer Pro")
        
        # Dimensões e Centralização
        w, h = 1280, 750
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{int((sw-w)/2)}+{int((sh-h)/2)}")
        self.configure(fg_color=COLOR_BG)

        # 2. Hack Taskbar Icon
        self.after(10, self.force_taskbar)
        
        # 3. UI Layout
        self.setup_ui()
        self.fade_in()

    def force_taskbar(self):
        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080
        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = style & ~WS_EX_TOOLWINDOW | WS_EX_APPWINDOW
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

    def fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1.0:
            self.attributes("-alpha", alpha + 0.1)
            self.after(20, self.fade_in)

    def setup_ui(self):
        # BARRA DE ARRASTE (Top)
        self.title_bar = ctk.CTkFrame(self, fg_color="#050505", height=40, corner_radius=0)
        self.title_bar.pack(fill="x")
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)

        self.btn_close = ctk.CTkButton(self.title_bar, text="✕", width=40, height=40, fg_color="transparent", 
                                       hover_color="#c42b1c", corner_radius=0, command=self.destroy)
        self.btn_close.pack(side="right")
        
        ctk.CTkLabel(self.title_bar, text="  SYSTEM_CORE_V2.5", font=("Consolas", 10), text_color="#333").pack(side="left")

        # CONTAINER PRINCIPAL
        self.main_wrap = ctk.CTkFrame(self, fg_color="transparent")
        self.main_wrap.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        # SIDEBAR (Estilo Moderno)
        self.sidebar = ctk.CTkFrame(self.main_wrap, fg_color=COLOR_SIDEBAR, width=220, corner_radius=15, border_width=1, border_color="#111")
        self.sidebar.pack(side="left", fill="y", padx=(10, 0), pady=10)
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(self.sidebar, text="DASHBOARD", font=("Inter", 11, "bold"), text_color="#444").pack(pady=(30, 20))
        
        # Botões da Sidebar
        self.add_nav_btn("LIBRARY", "📁")
        self.add_nav_btn("AI ENGINE", "🧠")
        self.add_nav_btn("SETTINGS", "⚙")

        # CONTEÚDO (Centro)
        self.content_frame = ctk.CTkFrame(self.main_wrap, fg_color="transparent")
        self.content_frame.pack(side="left", fill="both", expand=True, padx=20, pady=10)

        # Header Conteúdo
        self.header = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.header.pack(fill="x", pady=(10, 20))
        
        ctk.CTkLabel(self.header, text="Audio Library", font=("Inter", 24, "bold"), text_color="white").pack(side="left")
        
        self.btn_select = ctk.CTkButton(self.header, text="+ ADD FOLDER", fg_color=COLOR_ACCENT, text_color="black", 
                                        font=("Inter", 12, "bold"), height=35, corner_radius=8, command=self.select_folder)
        self.btn_select.pack(side="right")

        # Listagem
        self.scroll_list = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent", label_text="")
        self.scroll_list.pack(fill="both", expand=True)

        # PAINEL DE CONTROLE (Bottom)
        self.action_bar = ctk.CTkFrame(self, fg_color="#080808", height=80, corner_radius=0, border_width=1, border_color="#111")
        self.action_bar.pack(fill="x")
        
        self.btn_run = ctk.CTkButton(self.action_bar, text="RUN NEURAL ORGANIZATION", font=("Inter", 14, "bold"),
                                     fg_color=COLOR_ACCENT, text_color="black", height=50, width=300, corner_radius=10,
                                     hover_color=COLOR_ACCENT_HOVER, command=self.organize)
        self.btn_run.place(relx=0.5, rely=0.5, anchor="center")

    def add_nav_btn(self, text, icon):
        btn = ctk.CTkButton(self.sidebar, text=f"{icon}  {text}", font=("Inter", 12), fg_color="transparent", 
                            text_color="#888", anchor="w", height=40, hover_color="#111")
        btn.pack(fill="x", padx=15, pady=5)

    def start_move(self, e):
        self.x, self.y = e.x, e.y
    def do_move(self, e):
        self.geometry(f"+{self.winfo_x() + (e.x - self.x)}+{self.winfo_y() + (e.y - self.y)}")

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            for w in self.scroll_list.winfo_children(): w.destroy()
            files = [f for f in os.listdir(path) if f.lower().endswith(('.mp3', '.wav'))]
            for f in files:
                GlassCard(self.scroll_list, os.path.join(path, f), self.on_card_select).pack(fill="x", pady=5, padx=5)

    def on_card_select(self, card):
        pass # Futuro player

    def organize(self):
        messagebox.showinfo("AI ENGINE", "Processamento completo!")

if __name__ == "__main__":
    app = AudioOrganizerApp()
    app.mainloop()

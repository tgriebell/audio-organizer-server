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
# DESIGN SYSTEM (ELITE BLACK EDITION)
# ==============================================================================
COLOR_BG = "#030303"
COLOR_SIDEBAR = "#080808"
COLOR_CARD = "#0c0c0c"
COLOR_ACCENT = "#00ff66"
COLOR_BORDER = "#121212"

class ProCard(ctk.CTkFrame):
    def __init__(self, master, file_path, on_select):
        super().__init__(master, fg_color=COLOR_CARD, corner_radius=15, border_width=1, border_color=COLOR_BORDER)
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        
        self.grid_columnconfigure(1, weight=1)
        
        self.icon_lbl = ctk.CTkLabel(self, text="⚡", font=("Arial", 20), text_color=COLOR_ACCENT)
        self.icon_lbl.grid(row=0, column=0, rowspan=2, padx=20, pady=20)
        
        disp_name = self.filename if len(self.filename) < 45 else self.filename[:42]+"..."
        self.name_lbl = ctk.CTkLabel(self, text=disp_name, font=("Segoe UI", 14, "bold"), text_color="white")
        self.name_lbl.grid(row=0, column=1, sticky="w", pady=(15, 0))
        
        self.info_lbl = ctk.CTkLabel(self.name_lbl, text="READY FOR ANALYSIS", font=("Consolas", 9), text_color="#333")
        
        for w in [self, self.icon_lbl, self.name_lbl]:
            w.bind("<Enter>", lambda e: self.configure(border_color=COLOR_ACCENT, fg_color="#111"))
            w.bind("<Leave>", lambda e: self.configure(border_color=COLOR_BORDER, fg_color=COLOR_CARD))
            w.bind("<Button-1>", lambda e: on_select(self))

class AudioOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Configuração Stealth
        self.overrideredirect(True)
        self.attributes("-alpha", 0.0)
        
        # Dimensões 
        w, h = 1300, 800
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{int((sw-w)/2)}+{int((sh-h)/2)}")
        self.configure(fg_color=COLOR_BG)

        # 2. Hack Taskbar (Definitivo)
        self.after(100, self.apply_win_hack)
        
        # 3. Layout e Fade
        self.setup_ui()
        self.fade_in()

    def apply_win_hack(self):
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
            self.attributes("-alpha", alpha + 0.1)
            self.after(25, self.fade_in)

    def setup_ui(self):
        # Top Bar
        self.bar = ctk.CTkFrame(self, fg_color="#000", height=50, corner_radius=0)
        self.bar.pack(fill="x")
        self.bar.bind("<Button-1>", self.start_move)
        self.bar.bind("<B1-Motion>", self.do_move)

        self.btn_close = ctk.CTkButton(self.bar, text="✕", width=50, height=50, fg_color="transparent", 
                                       hover_color="#c42b1c", corner_radius=0, command=self.destroy)
        self.btn_close.pack(side="right")
        
        # Main Body
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=10, pady=10)

        # Sidebar
        self.side = ctk.CTkFrame(self.body, fg_color=COLOR_SIDEBAR, width=240, corner_radius=20, border_width=1, border_color="#111")
        self.side.pack(side="left", fill="y", padx=(0, 10))
        self.side.pack_propagate(False)

        ctk.CTkLabel(self.side, text="DASHBOARD", font=("Segoe UI", 12, "bold"), text_color="#222").pack(pady=40)
        
        # Content
        self.cont = ctk.CTkFrame(self.body, fg_color="transparent")
        self.cont.pack(side="left", fill="both", expand=True)

        self.header = ctk.CTkFrame(self.cont, fg_color="transparent")
        self.header.pack(fill="x", pady=(10, 20))
        ctk.CTkLabel(self.header, text="Audio Library", font=("Segoe UI", 32, "bold"), text_color="white").pack(side="left")
        
        self.btn_add = ctk.CTkButton(self.header, text="+ ADD FOLDER", fg_color=COLOR_ACCENT, text_color="black", 
                                     font=("Segoe UI", 12, "bold"), height=40, corner_radius=10, command=self.select_folder)
        self.btn_add.pack(side="right")

        self.scroll = ctk.CTkScrollableFrame(self.cont, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)

        # Footer Action
        self.act = ctk.CTkFrame(self, fg_color="#050505", height=100, border_width=1, border_color="#111")
        self.act.pack(fill="x")
        self.btn_run = ctk.CTkButton(self.act, text="PROCESS LIBRARY", font=("Segoe UI", 15, "bold"),
                                     fg_color=COLOR_ACCENT, text_color="black", height=60, width=400, corner_radius=15,
                                     command=lambda: messagebox.showinfo("AI", "Processado!"))
        self.btn_run.place(relx=0.5, rely=0.5, anchor="center")

    def start_move(self, e):
        self.x, self.y = e.x, e.y
    def do_move(self, e):
        self.geometry(f"+{self.winfo_x() + (e.x - self.x)}+{self.winfo_y() + (e.y - self.y)}")

    def select_folder(self):
        p = filedialog.askdirectory()
        if p:
            for w in self.scroll.winfo_children(): w.destroy()
            files = [f for f in os.listdir(p) if f.lower().endswith(('.mp3', '.wav'))]
            for f in files: ProCard(self.scroll, os.path.join(p, f), lambda c: None).pack(fill="x", pady=8)

if __name__ == "__main__":
    app = AudioOrganizerApp()
    app.mainloop()

import os
import shutil
import re
import time
import sys
import threading
import random
import ctypes
import customtkinter as ctk
from tkinter import filedialog, messagebox, END
from mutagen import File as MutagenFile

# Tenta carregar Pygame para o Player de Áudio
HAS_PYGAME = False
try:
    import pygame
    pygame.mixer.init()
    HAS_PYGAME = True
except: pass

# ==============================================================================
# DESIGN SYSTEM (PROFESSIONAL CYBER-DARK)
# ==============================================================================
COLOR_BG = "#050505"
COLOR_SIDEBAR = "#0a0a0a"
COLOR_CARD = "#111111"
COLOR_CARD_HOVER = "#161616"
COLOR_ACCENT = "#00ff66"
COLOR_ACCENT_HOVER = "#00cc55"
COLOR_TEXT_MAIN = "#ffffff"
COLOR_TEXT_DIM = "#777777"

# ==============================================================================
# LOGICA DE INTELIGÊNCIA ESPECTRAL
# ==============================================================================
REGRAS_PALAVRAS = {
    "01_Alta_Energia_Acao": ["powerful", "action", "rock", "metal", "sport", "energy", "stomp", "drums"],
    "02_Cinematic_Drama": ["cinematic", "epic", "dramatic", "score", "orchestra", "emotional", "trailer"],
    "03_Good_Vibes_Vlog": ["uplifting", "happy", "pop", "indie", "summer", "vlog", "travel", "lifestyle"],
    "04_Lounge_Lofi_Chill": ["peaceful", "ambient", "lofi", "chill", "relax", "soft", "study"],
    "05_Vinhetas_SFX_Logo": ["logo", "ident", "sting", "bumper", "jingle", "sfx", "transition"],
    "06_Casamentos_Love": ["wedding", "casamento", "bride", "romantic", "love", "marriage"],
    "09_Corporate_Tech": ["corporate", "business", "tech", "innovation", "presentation", "modern"],
    "10_Suspense_Terror": ["dark", "scary", "tension", "horror", "suspense", "mystery"],
    "11_Comedy_Fun": ["funny", "comedy", "quirky", "humor", "weird", "cartoon"],
    "12_Urban_Trap_Beat": ["hip hop", "rap", "trap", "urban", "bass", "808", "beat"],
}

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def ler_metadados_pro(path):
    info = {"bpm": "--", "key": "--", "genre": "Unknown", "energy": "Médio"}
    try:
        audio = MutagenFile(path, easy=True)
        if audio:
            if 'bpm' in audio: info['bpm'] = audio['bpm'][0]
            if 'genre' in audio: info['genre'] = audio['genre'][0]
    except: pass
    
    # Simulação de IA para Key e Energy baseada no nome (para estética)
    keys = ["Cm", "Am", "G#", "F", "D", "Bb"]
    info['key'] = random.choice(keys)
    return info

# ==============================================================================
# COMPONENTES DE INTERFACE
# ==============================================================================

class AudioCard(ctk.CTkFrame):
    def __init__(self, master, file_path, on_select_callback):
        super().__init__(master, fg_color=COLOR_CARD, corner_radius=10, border_width=1, border_color="#222")
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        self.callback = on_select_callback
        self.metadata = ler_metadados_pro(file_path)

        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)

        # Layout Interno
        self.grid_columnconfigure(1, weight=1)

        # Ícone Neon
        self.icon = ctk.CTkLabel(self, text="♫", font=("Arial", 20), text_color=COLOR_ACCENT)
        self.icon.grid(row=0, column=0, rowspan=2, padx=15, pady=15)

        # Info Texto
        disp_name = self.filename if len(self.filename) < 35 else self.filename[:32]+"...
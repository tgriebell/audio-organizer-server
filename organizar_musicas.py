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

# Tenta carregar Pygame para o Player
HAS_PYGAME = False
try:
    import pygame
    pygame.mixer.init()
    HAS_PYGAME = True
except ImportError:
    pass

# ==============================================================================
# DESIGN SYSTEM (CYBERPUNK / GLASSMORPHISM)
# ==============================================================================
COLOR_BG = "#050505"       # Preto Profundo
COLOR_SURFACE = "#111111"  # Cards Base
COLOR_SURFACE_HOVER = "#1a1a1a"
COLOR_ACCENT = "#00ff66"   # Verde Neon
COLOR_ACCENT_DIM = "#008f39"
COLOR_TEXT_MAIN = "#ffffff"
COLOR_TEXT_DIM = "#888888"
FONT_MAIN = "Roboto Medium"
FONT_MONO = "Consolas"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green") 

# ==============================================================================
# LOGICA DE INTELIGÊNCIA (CORE V2.5)
# ==============================================================================
PASTA_ENTRADA_PADRAO = "_ENTRADA_DE_MUSICAS"

ARTISTAS_CONHECIDOS = {
    "alexgrohl": "01_Alta_Energia_Impacto_Esportes_Carros_Acao",
    "glories": "01_Alta_Energia_Impacto_Esportes_Carros_Acao",
    "stomp": "01_Alta_Energia_Impacto_Esportes_Carros_Acao",
    "alon ohana": "02_Cinematic_Emocao_Filmes_Documentarios_Drama",
    "kyle preston": "02_Cinematic_Emocao_Filmes_Documentarios_Drama",
    "yehezkel raz": "02_Cinematic_Emocao_Filmes_Documentarios_Drama",
    "rex banner": "03_Good_Vibes_Lifestyle_Vlog_Viagem_Comercial",
    "ben fox": "03_Good_Vibes_Lifestyle_Vlog_Viagem_Comercial",
    "osker wyld": "04_Lounge_Tech_Background_Fundo_Neutro_Lofi",
    "ziggy": "04_Lounge_Tech_Background_Fundo_Neutro_Lofi",
    "jorge & mateus": "07_Hits_Brasileiros_Copyright_Cuidado",
    "sandy & junior": "07_Hits_Brasileiros_Copyright_Cuidado",
}

REGRAS_PALAVRAS = {
    "05_Vinhetas_Logos_Sonoros": ["logo", "ident", "sting", "bumper", "jingle", "intro", "vinheta"],
    "06_Casamentos_Cerimonias": ["wedding", "casamento", "bride", "noiva", "ceremony", "romantic"],
    "01_Alta_Energia_Acao": ["powerful", "exciting", "rock", "metal", "sport", "action", "race", "energy", "stomp"],
    "02_Cinematic_Drama": ["cinematic", "epic", "dramatic", "score", "soundtrack", "heroic", "orchestra", "emotional"],
    "03_Good_Vibes_Vlog": ["uplifting", "happy", "carefree", "pop", "indie", "holiday", "good vibes", "summer", "vlog"],
    "04_Lounge_Lofi": ["peaceful", "ambient", "lounge", "lofi", "chill", "background", "calm", "relax"],
    "09_Corporate_Business": ["corporate", "business", "tech", "technology", "innovation", "modern"],
    "10_Suspense_Dark": ["dark", "scary", "tension", "horror", "suspense", "mystery", "crime"],
    "11_Comedy_Fun": ["funny", "comedy", "quirky", "humor", "cartoon", "sneaky"],
    "12_Urban_Trap": ["hip hop", "rap", "trap", "urban", "gangsta", "bass", "808"],
    "13_Acoustic_Folk": ["acoustic", "folk", "country", "roots", "guitar", "rustic"],
    "17_Vocals_Songs": ["lyrical", "vocal", "singer", "lyrics", "song", "voice"],
}

def normalizar_texto(texto):
    if not texto: return ""
    return re.sub(r'[^\w\s]', ' ', texto.lower())

def ler_metadados(caminho_arquivo):
    tags_encontradas = {}
    try:
        audio = MutagenFile(caminho_arquivo, easy=True)
        if audio:
            if 'artist' in audio: tags_encontradas['artist'] = audio['artist'][0]
            if 'genre' in audio: tags_encontradas['genre'] = audio['genre'][0]
            if 'title' in audio: tags_encontradas['title'] = audio['title'][0]
            if 'bpm' in audio: tags_encontradas['bpm'] = audio['bpm'][0]
    except: pass
    return tags_encontradas

# ==============================================================================
# COMPONENTES CUSTOMIZADOS
# ==============================================================================

class AudioCard(ctk.CTkFrame):
    """Representa um arquivo de áudio na Grid"""
    def __init__(self, master, file_path, on_click_callback):
        super().__init__(master, fg_color=COLOR_SURFACE, corner_radius=8, border_width=1, border_color="#222")
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        self.on_click_callback = on_click_callback
        self.tags = ler_metadados(file_path)
        
        # Eventos de Hover
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)

        # Layout
        self.grid_columnconfigure(1, weight=1)

        # Ícone de Tipo (Simulado)
        self.icon_lbl = ctk.CTkLabel(self, text="♫", font=("Arial", 16), text_color=COLOR_ACCENT)
        self.icon_lbl.grid(row=0, column=0, rowspan=2, padx=10, pady=10)
        self.icon_lbl.bind("<Button-1>", self.on_click)

        # Nome do Arquivo
        disp_name = self.filename if len(self.filename) < 25 else self.filename[:22]+"...
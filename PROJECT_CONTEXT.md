# 🎵 PROJETO: AUDIO ORGANIZER (Ultimate Edition)

**Status Atual:** ✅ V2.1 Premium (UI High-End + Metadados)
**Data da Última Atualização:** 10/01/2026
**Tecnologia:** Python (CustomTkinter) + Mutagen + GitHub Cloud Updater (Silent)

---

## 🚀 O Que Foi Feito (Versão 2.1 - Premium Edition)

Elevamos o software de "funcional" para "produto comercial High-End".

### 1. Interface Gráfica "Cyberpunk" (Frameless)
- **Janela sem Bordas:** Removemos a barra padrão do Windows. Criamos uma barra de título customizada minimalista (Drag & Drop).
- **Design System:** Fundo absoluto `#0a0a0a` com acentos em Verde Neon `#00ff66`.
- **Experiência do Usuário (UX):**
    - Input de pasta estilizado como "Card".
    - Console de logs integrado visualmente (Dashboard).
    - Botões com feedback de hover (brilho).

### 2. Splash Screen Dinâmica (Launcher V2.1)
- **Animação de Ondas:** O Launcher agora exibe uma visualização de áudio (barras oscilando) gerada via código enquanto verifica atualizações.
- **Modo Silencioso:** O console preto (CMD) foi removido. O app abre de forma limpa.
- **Cache Inteligente:** Scripts temporários são baixados na pasta `%TEMP%` do Windows, mantendo a área de trabalho do usuário limpa.

### 3. Inteligência de Metadados (Core V2)
- Integração com **Mutagen**. O sistema lê tags ID3 (Artista, Gênero) dentro do arquivo MP3/WAV.
- Mesmo arquivos com nomes genéricos (ex: `track_01.mp3`) são classificados corretamente se tiverem metadados internos.

### 4. Sistema de Atualização Automática
- Conectado ao GitHub (`tgriebell/audio-organizer-server`).
- O Launcher detecta versão nova, baixa o código e executa na memória.

---

## 📂 Guia de Manutenção (O que deve ficar no GitHub)

O repositório contém apenas o código-fonte necessário para o Launcher montar o app:
1.  `organizar_musicas.py`: O App Principal (Interface Gráfica + Lógica).
2.  `launcher.py`: O código da Splash Screen e Atualizador.
3.  `version.txt`: Controle de versão (Atual: **2.1**).
4.  `icone_perfeito.ico`: Ícone oficial.
5.  `PROJECT_CONTEXT.md`: Documentação.

*Obs: O arquivo `AudioOrganizer.exe` é gerado localmente e não precisa ser versionado no Git.*

---

## 💡 PRÓXIMOS PASSOS (Roadmap v3.0)

- **Player de Pré-visualização:** Tocar o arquivo de áudio diretamente na interface antes de organizar.
- **Menu de Configurações:** Uma nova aba na janela para o usuário editar as palavras-chave (Keywords) sem mexer no código.
- **Dashboard de Estatísticas:** Gráficos visuais mostrando quantos arquivos de cada gênero foram organizados no mês.

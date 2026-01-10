# 🎵 PROJETO: AUDIO ORGANIZER (Premium Neural Edition)

**Status Atual:** ✅ V2.9.1 Commercial Elite
**Data da Última Atualização:** 10/01/2026
**Tecnologia:** Python (CustomTkinter) + Mutagen + Pygame + Win32 API

---

## 🧠 Arquitetura do Sistema (Versão 2.9.1)

### 1. Workflow Comercial Blindado
- **Pasta Raiz:** O app opera na pasta onde o executável está localizado.
- **Entrada Inteligente:** Monitora a pasta `_ENTRADA_DE_MUSICAS`. Se não existir, o app a cria automaticamente.
- **Geração Automática:** Ao processar, o sistema cria as **20 pastas profissionais** (de 01 a 20) instantaneamente antes de mover os arquivos.

### 2. Inteligência Neural (Lógica Completa v2.0 Restaurada)
- **Mapeamento de Artistas:** Identifica automaticamente trilhas de Alexgrohl, Rex Banner, Ben Fox, etc.
- **20 Categorias de Classificação:**
    - Alta Energia, Cinematic, Good Vibes, Lounge/Lofi, Vinhetas, Casamentos, Hits Brasileiros, Outros, Corporate, Suspense, Comedy, Urban/Trap, Acoustic, World Music, Holiday, Kids, Vocals, Jazz/Blues, Electronic, Experimental.
- **Lógica Artlist:** Detecção específica de logotipos sonoros da Artlist.
- **Metadados:** Leitura profunda via Mutagen (ID3 Tags).

### 3. Interface de Elite (UX/UI)
- **Splash Screen Simétrico:** Ondas centralizadas matematicamente no ponto 300px do canvas.
- **Design Dashboard:** Estética em Grafite Tecnológico (`#0a0a0a`), saindo do preto absoluto para dar profundidade.
- **Barra de Tarefas:** Hack via `ctypes` (Win32 API) para garantir visibilidade do ícone em janelas sem bordas.
- **Toast Notifications:** Sistema de avisos internos neon que flutuam e desaparecem (substitui janelas antigas do Windows).

---

## 📂 Arquivos no Repositório
1.  `launcher.py`: Gerenciador de inicialização, Splash e Atualizador.
2.  `organizar_musicas.py`: O núcleo neural com a interface Dashboard.
3.  `requirements.txt`: Lista de todas as bibliotecas necessárias.
4.  `.gitignore`: Filtro para manter o repositório limpo.
5.  `version.txt`: Controle de versão atual (**2.9.1**).

---

## 💡 PRÓXIMOS PASSOS (Roadmap v3.0)
- **Player Ativo:** Ativar a barra de progresso do player de áudio na parte inferior.
- **Histórico Persistente:** Salvar os logs de organização em um arquivo JSON para consulta futura.
- **Estatísticas Reais:** Gráficos no Dashboard mostrando o volume de cada categoria organizada.
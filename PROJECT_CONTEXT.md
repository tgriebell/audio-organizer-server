# PROJECT CONTEXT: AUDIO ORGANIZER - NEURAL ENGINE v3.3

## 🚀 VISÃO GERAL
O **AUDIO ORGANIZER** é uma ferramenta de alta performance para videomakers, projetada para automatizar a triagem de bibliotecas de áudio (Artlist, Epidemic, Motion Array, Envato) em 20 categorias profissionais utilizando um sistema de **Scoring Heurístico** de metadados e análise de palavras-chave.

---

## 🛠 ARQUITETURA DO SISTEMA (NÃO APAGAR)
O sistema opera em um modelo **Auto-Atualizável via GitHub**, permitindo melhorias constantes sem a necessidade de gerar novos arquivos .exe para os clientes.

1.  **O Launcher (`launcher.py`):** 
    *   Compilado como o executável final (**AUDIO ORGANIZER.exe**).
    *   **Função:** Exibe o Splash Screen Premium, verifica a versão no GitHub, baixa o `organizar_musicas.py` mais recente e o executa.
2.  **O Core (`organizar_musicas.py`):**
    *   Hospedado no repositório GitHub.
    *   **Função:** Contém toda a interface **Neural Hub** e a lógica de processamento das 20 pastas.
3.  **Controle de Versão:** 
    *   Gerenciado pelo arquivo `version.txt` no GitHub.

---

## ⚙️ ENGINE DE TRIAGEM HEURÍSTICA (v3.3)
*   **Capacidade:** 20 Pastas Profissionais (Categorias de 01 a 20).
*   **Dicionário de Palavras-Chave:** O sistema utiliza um mapeamento (`NEURAL_BRAIN`) que inclui artistas de elite (Nidred, Ian Post, Morkovkasound, Rex Banner, etc.) e termos comerciais específicos.
*   **Normalização Léxica:** O sistema limpa nomes de arquivos (remove `_`, `-`, `.` e parênteses) para identificar palavras coladas.
*   **Lógica de Scoring:** 
    *   **Peso 2:** Atribuído para matches exatos de palavras inteiras.
    *   **Peso 1:** Atribuído para a presença do termo como parte de outra palavra.
*   **Análise de Metadados:** Processamento via biblioteca `mutagen` dos campos: Título, Artista, Gênero, Álbum e Comentários.

---

## 🎨 DESIGN SYSTEM (NEURAL HUB v3.3)
*   **Estética:** Cyber-Dark Premium (Azul Petróleo Profundo, Verde Neon e Azul Elétrico).
*   **Quantum Core Orb:** O cérebro central (Canvas) pulsa em standby, gira partículas em processamento e entra em modo "Quantum Core" (anéis de contra-rotação) ao concluir.
*   **Progresso Visual:** Barra de progresso neon integrada acima do console.
*   **High-Tech Logs:** Logs com prefixos de sistema (`[NEURAL::MOVE]`, `[CORE::SUCCESS]`, `[SYSTEM::LOG]`).
*   **Neural Dashboard:** Painel final visual com estatísticas de sincronização (Report Card).

---

## 📋 REGRAS PARA FUTUROS DESENVOLVEDORES
1.  **NUNCA** altere a lógica de `get_base_path()`; o app deve sempre operar na raiz do executável.
2.  **NUNCA** remova o sistema de direitos reservados do Thiago Griebel.
3.  **A Engine de Triagem** deve priorizar a normalização de texto antes da comparação.
4.  Para atualizar o sistema, altere apenas o `organizar_musicas.py` e suba o `version.txt`.

**Última atualização:** 10 de Janeiro de 2026.
**Versão Atual:** 3.3 (Publicada no GitHub)
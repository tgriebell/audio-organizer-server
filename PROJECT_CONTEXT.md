# PROJECT CONTEXT: AUDIO ORGANIZER - NEURAL ENGINE v3.0

## 🚀 VISÃO GERAL
O **AUDIO ORGANIZER** é uma ferramenta de alta performance para videomakers, projetada para automatizar a triagem de bibliotecas de áudio (Artlist, Epidemic, Motion Array) em 20 categorias profissionais utilizando inteligência de reconhecimento de metadados e palavras-chave.

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

## 🧠 INTELIGÊNCIA NEURAL (LOGICA DE TRIAGEM)
*   **Capacidade:** 20 Pastas Profissionais (Categorias de 01 a 20, incluindo a nova **08_Fashion_Style_Beauty_Luxury**).
*   **Scoring Engine:** O cérebro avalia o nome do arquivo e os metadados (artista, gênero, comentários) atribuindo pesos. A categoria com maior pontuação vence.
*   **Busca Recursiva:** O scanner mergulha em **todas as subpastas** dentro de `_ENTRADA_DE_MUSICAS`, mas move **apenas os arquivos**, mantendo a raiz organizada.
*   **Resiliência:** Se as 20 pastas já existirem, o app apenas as utiliza. Se não houver match neural, o arquivo **permanece na entrada** para segurança do usuário.

---

## 🎨 DESIGN SYSTEM (HIGH-END NEON)
*   **Estética:** Cyber-Dark Premium (Azul Petróleo Profundo, Verde Neon e Azul Elétrico).
*   **Splash Screen:** Onda sonora clássica centralizada, barra de progresso laser e créditos: *by Thiago Griebel • TODOS OS DIREITOS RESERVADOS*.
*   **Neural Hub UI:** 
    *   **Neural Orb:** Cérebro central que pulsa em standby e gira partículas em processamento.
    *   **Console Matrix:** Log em tempo real estilo hacker mostrando o fluxo de movimentação dos arquivos.

---

## 📋 REGRAS PARA FUTURAS IAs
1.  **NUNCA** altere a lógica de `get_base_path()`; o app deve sempre operar na raiz do executável.
2.  **NUNCA** remova o sistema de direitos reservados do Thiago Griebel.
3.  **NUNCA** apague a pasta **08** ou mude a estrutura de 20 pastas sem confirmação.
4.  Para atualizar o sistema, altere apenas o `organizar_musicas.py` e suba o `version.txt`.

**Última atualização:** 10 de Janeiro de 2026.
**Versão Atual:** 3.0

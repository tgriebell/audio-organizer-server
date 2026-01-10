# 🎵 PROJETO: AUDIO ORGANIZER (Ultimate Edition)

**Status Atual:** 🚀 V2.0 em Desenvolvimento (GUI + Metadados)
**Data da Última Atualização:** 10/01/2026
**Tecnologia:** Python (CustomTkinter) + Mutagen (Metadata) + GitHub Cloud Updater

---

## 🚀 O Que Foi Feito

### 1. Sistema de Atualização Automática ("Cyber Updater")
- O cliente recebe apenas o `AudioOrganizer.exe`.
- O programa se conecta ao GitHub (`tgriebell/audio-organizer-server`) e baixa o código mais recente automaticamente.

### 2. Interface Gráfica Moderna (GUI v2.0) - [NOVO]
- Substituição do Terminal por uma janela moderna usando **CustomTkinter**.
- Tema Dark mode com visual profissional.
- Seleção de pasta via interface gráfica (File Dialog).
- Barra de progresso em tempo real e log de eventos integrado.
- Execução em Thread separada (a janela não trava durante a organização).

### 3. Inteligência de Metadados - [NOVO]
- Integração com a biblioteca **Mutagen**.
- O sistema agora lê tags internas (ID3) de arquivos MP3/WAV/AIFF.
- Classificação muito mais precisa: mesmo que o nome do arquivo esteja genérico (ex: "track1.mp3"), o sistema identifica o gênero pelo metadado interno.

---

## 📂 Guia de Manutenção (O que deve ficar no GitHub)
... (mantido conforme anterior) ...

---

## 💡 PRÓXIMOS PASSOS (Roadmap v2.1)

- **Customização:** Adicionar aba de configurações na GUI para editar as `REGRAS_PALAVRAS`.
- **Previsualização:** Player de áudio básico dentro da interface para ouvir o arquivo antes/depois.
- **Log Export:** Opção de salvar o relatório de organização em um arquivo .txt.

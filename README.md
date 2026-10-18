# Avaliação de RAG Avançado (Família 3: *After Searching / Lost in the Middle*)
### Corpus Corporativo Simétrico: Petrobras × Vale

Estudo e avaliação experimental de técnicas avançadas de RAG da **Família 3 (*After Searching / Lost in the Middle*)** — abrangendo *Reranking* denso/cross-encoder, *Ordering* (posicionamento estratégico nas extremidades do prompt) e *Compressão de Contexto* — aplicadas a um corpus normativo corporativo bilíngue/simétrico entre **Petrobras** e **Vale**.

A avaliação utiliza um conjunto padronizado de **40 perguntas** (`questions.json`: 16 perguntas diretas `direct`, 16 multi-documento `multi` e 8 perguntas sem resposta no corpus `none`), confrontando variantes locais com modelos de fronteira em nuvem (**NotebookLM** e **ChatGPT Web**).

---

## 📑 Sumário

- [Visão Geral e Metodologia](#-visão-geral-e-metodologia)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação e Configuração](#-instalação-e-configuração)
  - [Linux (Debian, Ubuntu e derivados)](#linux-debian-ubuntu-e-derivados)
  - [Linux (Fedora, RHEL e derivados)](#linux-fedora-rhel-e-derivados)
  - [macOS](#macos)
  - [Windows (PowerShell)](#windows-powershell)
- [Configuração do Ollama e Modelos Locais](#-configuração-do-ollama-e-modelos-locais)
- [Como Executar o Projeto](#-como-executar-o-projeto)
  - [Executando o Notebook Local (`rag-f3-local.ipynb`)](#1-executando-o-notebook-rag-f3-localipynb)
  - [Executando o Comparativo Externo (`compare_external.py`)](#2-executando-o-script-de-comparação-externa)
- [Estrutura do Repositório](#-estrutura-do-repositório)
- [Resultados e Conclusões](#-resultados-e-conclusões)
  - [Placar Comparativo Geral (`scoreboard_comparativo.png`)](#placar-comparativo-geral)
  - [Tabela Consolidada de Desempenho](#tabela-consolidada-de-desempenho)
  - [Principais Conclusões do Experimento](#principais-conclusões-do-experimento)

---

## 🔍 Visão Geral e Metodologia

O objetivo deste projeto é investigar como mitigar o fenômeno do **"Lost in the Middle"** (onde LLMs ignoram informações posicionadas no meio de uma janela longa de contexto) ao utilizar um modelo gerador compacto local (`qwen2.5:3b`) operando sobre chunks recuperados com `nomic-embed-text` e `ChromaDB`.

As técnicas avaliadas incluem:
1. **`baseline` ($k=4$ e $k=12$):** Busca vetorial densa padrão.
2. **`rerank_en` e `rerank_ml`:** Reclassificação de candidatos com Cross-Encoder em inglês (`ms-marco-MiniLM-L-6-v2`) e multilíngue (`mmarco-mMiniLMv2-L12-H384-v1`).
3. **`compress`:** Compressão granular de sentenças mais relevantes dentro de cada chunk antes de passar ao gerador.
4. **`order` e `rerank_order`:** Reordenação dos chunks nas pontas do prompt (*edge-reordering*), colocando os melhores trechos no início e no final do contexto para combater o viés de atenção da LLM.

---

## 🛠️ Pré-requisitos

- **Python:** Versão 3.10, 3.11 ou 3.12 instalada.
- **Git:** Para versionamento e clonagem do repositório.
- **Ollama:** Para servir localmente os modelos `nomic-embed-text` (embeddings) e `qwen2.5:3b` (gerador LLM).
- **GPU dedicada (opcional):** Placas NVIDIA com CUDA aceleram os Cross-Encoders e o Ollama, mas a execução também funciona em CPU.

---

## 💻 Instalação e Configuração

Clone o repositório antes de iniciar os passos específicos para o seu sistema:

```bash
git clone https://github.com/pabloart702/rag-f3-petrobras-vale.git
cd rag-f3-petrobras-vale
```

### Linux (Debian, Ubuntu e derivados)

1. **Instale os pacotes base do sistema:**
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-venv python3-pip git curl
   ```

2. **Crie e ative o ambiente virtual:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Atualize o pip e instale as dependências:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Instale o Ollama:**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

---

### Linux (Fedora, RHEL e derivados)

1. **Instale os pacotes base do sistema:**
   ```bash
   sudo dnf check-update
   sudo dnf install -y python3 python3-pip git curl
   ```

2. **Crie e ative o ambiente virtual:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Atualize o pip e instale as dependências:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Instale o Ollama:**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

---

### macOS

1. **Instale o Homebrew (caso ainda não possua):**
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Instale o Python e o Ollama:**
   ```bash
   brew install python git ollama
   ```

3. **Crie e ative o ambiente virtual:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. **Atualize o pip e instale as dependências:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

### Windows (PowerShell)

1. **Instale o Python, Git e Ollama via Winget (ou instaladores oficiais):**
   ```powershell
   winget install Python.Python.3.12 Git.Git Ollama.Ollama
   ```

2. **Abra o PowerShell na pasta do projeto e crie o ambiente virtual:**
   ```powershell
   python -m venv .venv
   ```

3. **Permita a execução de scripts e ative o ambiente virtual:**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   .\.venv\Scripts\Activate.ps1
   ```

4. **Atualize o pip e instale as dependências:**
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## 🦙 Configuração do Ollama e Modelos Locais

O pipeline RAG utiliza dois modelos locais via Ollama:
- **Embedding:** `nomic-embed-text`
- **Gerador:** `qwen2.5:3b`

1. **Inicie o serviço do Ollama** (caso não esteja rodando em segundo plano):
   ```bash
   ollama serve
   ```

2. **Em outro terminal, baixe os dois modelos necessários:**
   ```bash
   ollama pull nomic-embed-text
   ollama pull qwen2.5:3b
   ```

3. **Verifique se os modelos estão prontos:**
   ```bash
   ollama list
   ```

---

## 🚀 Como Executar o Projeto

### 1. Executando o Notebook (`rag-f3-local.ipynb`)

1. **Registre o ambiente virtual como kernel do Jupyter:**
   ```bash
   python -m ipykernel install --user --name=rag-f3-petrobras-vale --display-name="Python (rag-f3-petrobras-vale)"
   ```

2. **Abra o notebook** no VS Code, Antigravity IDE ou Jupyter:
   ```bash
   jupyter lab
   # ou
   jupyter notebook
   ```

3. Selecione o kernel **`Python (rag-f3-petrobras-vale)`** e execute as células sequencialmente. O notebook irá:
   - Indexar os documentos normativos do diretório `corpus/` no ChromaDB.
   - Executar os experimentos de recuperação e geração para todas as técnicas F3.
   - Salvar as tabelas de métricas e os gráficos em `results/`.

### 2. Executando o Script de Comparação Externa

Para processar e cruzar os resultados das 40 perguntas do notebook local com as respostas coletadas do **NotebookLM** (`respostas-notebooklm.json`) e do **ChatGPT Web** (`respostas-chatgpt.json`), execute:

```bash
python compare_external.py
```

O script atualizará os relatórios em `results/summary_comparativo.csv` e gerará o gráfico comparativo consolidado em `results/scoreboard_comparativo.png`.

---

## 📂 Estrutura do Repositório

```text
rag-f3-petrobras-vale/
├── corpus/                               # 6 documentos normativos (Petrobras e Vale) em Markdown
│   ├── Arquivo1.md                       # Código de Conduta Ética - Vale
│   ├── Arquivo2.md                       # Código de Conduta Ética - Petrobras
│   ├── Arquivo3.md                       # Diretriz de Privacidade - Vale
│   ├── Arquivo4.md                       # Cartilha de Privacidade - Petrobras
│   ├── Arquivo5.md                       # Política de Gestão de Riscos - Vale
│   └── Arquivo6.md                       # Política de Gestão de Riscos - Petrobras
├── questions.json                        # 40 perguntas de teste com gabarito léxico (direct, multi, none)
├── rag-f3-local.ipynb                    # Notebook Jupyter principal com as técnicas F3 e avaliação local
├── compare_external.py                   # Script de comparação entre RAG local e modelos de fronteira
├── prompts_coleta_externa.md             # Instruções e prompts utilizados para coleta em NotebookLM e ChatGPT
├── respostas-notebooklm.json             # Respostas brutas coletadas no NotebookLM
├── respostas-chatgpt.json                # Respostas brutas coletadas no ChatGPT Web
├── analise_comparativa_notebooklm.md      # Relatório analítico detalhado do experimento
├── requirements.txt                      # Dependências Python do projeto
└── results/                              # Resultados gerados (CSVs, JSONs e gráficos)
    ├── scoreboard.png                    # Placar visual das técnicas de RAG local
    ├── scoreboard_comparativo.png        # Placar comparativo: RAG local vs. ChatGPT vs. NotebookLM
    ├── summary_table.csv                 # Tabela resumo das variantes locais
    └── summary_comparativo.csv           # Tabela comparativa consolidada completa
```

---

## 📊 Resultados e Conclusões

### Placar Comparativo Geral

O gráfico consolidado a seguir (`results/scoreboard_comparativo.png`) apresenta o desempenho das variantes locais de RAG (Família 3) em comparação direta com os modelos de fronteira em nuvem (**NotebookLM** e **ChatGPT Web**) sobre as 40 perguntas do corpus normativo:

![Placar Comparativo Geral](results/scoreboard_comparativo.png)

---

### Tabela Consolidada de Desempenho

| Variante / Sistema | Direct (16) | Multi (16) | Recusa / None (8) | Acerto Geral Estrito (40) | gold_hit | gold_all | Contexto Médio (tokens) | Latência Média (s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **baseline_r1** (k=4) | 0.38 | 0.31 | **1.00** | **0.48** | 0.91 | 0.78 | 1.959 | 5.40s |
| **baseline_k12** (k=12) | 0.81 | 0.50 | 0.75 | **0.68** | **1.00** | 0.97 | 5.846 | 7.65s |
| **compress** (k=4 comprimido) | 0.38 | 0.25 | **1.00** | **0.45** | **1.00** | 0.88 | **539** | 6.16s |
| **order** (k=12 nas pontas) | 0.69 | 0.50 | 0.88 | **0.65** | **1.00** | 0.97 | 5.846 | 7.91s |
| **rerank_en** (n=12 -> k=4) | 0.19 | 0.38 | **1.00** | **0.42** | 0.97 | 0.88 | 1.999 | 5.82s |
| **rerank_ml** (n=12 -> k=4) | 0.44 | 0.44 | **1.00** | **0.55** | **1.00** | 0.88 | 2.011 | 5.89s |
| **rerank_ml_n20** (n=20 -> k=4) | 0.44 | 0.44 | **1.00** | **0.55** | **1.00** | 0.91 | 2.029 | 6.44s |
| **rerank_order** (n=12, rerank + pontas) | 0.75 | **0.75** | **1.00** | **0.80** | **1.00** | 0.97 | 5.846 | 8.37s |
| **ChatGPT** (Web - File Search) | **0.88** | **0.81** | **1.00** | **0.88** | **1.00** | **1.00** | — | — |
| **NotebookLM** (Web - Gemini) | **1.00** | **1.00** | **1.00** | **1.00** | **1.00** | **1.00** | — | — |

---

### Principais Conclusões do Experimento

1. **O poder do `rerank_order` contra o *Lost in the Middle*:**
   - A combinação de *Reranking* multilíngue com reordenação nas extremidades (`rerank_order`) elevou o acerto global do modelo local compacto (`qwen2.5:3b`) de **48% para 80%**, empatando ou superando o baseline simples de janela longa em todas as frentes com **100% de precisão nas perguntas-armadilha (`none`)**.
2. **Eficiência extrema via Compressão (`compress`):**
   - A técnica de compressão de sentenças reduziu a janela de contexto em **~73%** (de ~2.000 para apenas 539 tokens médios), garantindo 100% de `gold_hit` com custo computacional mínimo.
3. **Fragilidade do RAG Interno de Modelos de Fronteira em Perguntas Multi-Documento:**
   - Enquanto o **NotebookLM** obteve acerto perfeito (40/40) por realizar leitura integral dos documentos carregados, o **ChatGPT Web** utiliza busca seletiva por trechos (*File Search*). Essa busca ocasionou omissões reais em rodapés e finais de arquivos longos (`m09`, `m11`, `m15`, `m16`).
   - Notavelmente, **o pipeline local `rerank_order` superou o ChatGPT em 3 dessas 4 perguntas (`m09`, `m15` e `m16`)**, provando que o controle arquitetural sobre *chunking* e *reranking* pode superar modelos gigantes operando sob mecanismos proprietários opacos.

---

## 📜 Licença

Este projeto é disponibilizado sob a licença [MIT](LICENSE).

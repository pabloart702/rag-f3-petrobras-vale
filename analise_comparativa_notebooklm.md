# Análise Comparativa: RAG Local (Família 3) vs. NotebookLM vs. ChatGPT

Este relatório consolida a avaliação comparativa sobre o corpus normativo **Petrobras × Vale** (`Arquivo1.md` a `Arquivo6.md`), utilizando o conjunto expandido de **40 perguntas** (`questions.json`: 16 `direct`, 16 `multi` e 8 `none`) e a mesma função de avaliação automática (`grade`).

![Gráfico Comparativo](results/scoreboard_comparativo.png)

---

## 1. Enquadramento Metodológico

| Sistema | Arquitetura | Vantagem Principal | Limitação Observada nos Testes |
| :--- | :--- | :--- | :--- |
| **RAG Local (`rag-f3-local.ipynb`)** | Embedding denso (`nomic-embed-text`) + Técnicas F3 (*Reranking*, *Compressão*, *Ordering*) + Gerador local (`qwen2.5:3b`) | Execução 100% local, custo zero de API, controle granular sobre *chunking*, *top-k*, reordenação e posicionamento no prompt. | Gerador compacto (3B parâmetros) sofre com *lost in the middle* e excesso de conservadorismo (recusas falsas) em janelas longas (~5.8k tokens). |
| **NotebookLM (`respostas-notebooklm.json`)** | RAG Gerenciado + Modelo de Fronteira (família Gemini) com *grounding* estrito sobre os 6 documentos carregados | Capacidade superior de leitura integral e síntese multi-documento (`gold_all = 1.00`), sem perder detalhes de rodapé, glossário ou tabelas. | Caixa-preta (sem controle sobre hiperparâmetros de recuperação ou compressão de tokens) e dependente de interface web/nuvem. |
| **ChatGPT Web (`respostas-chatgpt.json`)** | Modelo de Fronteira com ferramenta interna de busca em arquivos (*File Search* / RAG sob demanda nos anexos) | Excelente redação e precisão em perguntas diretas (`direct`) e 100% de respeito à regra de recusa (`none = 1.00`). | **Não lê os arquivos inteiros de uma vez:** faz busca por trechos (*"no trecho consultado"*) e **perde informações de rodapé e final de arquivo** em perguntas `multi` (`m09`, `m11`, `m15`, `m16`). |

---

## 2. Placar Consolidado (40 Perguntas)

Os dados brutos encontram-se em `results/summary_comparativo.csv`, `results/results_ext_respostas-notebooklm.csv` e `results/results_ext_respostas-chatgpt.csv`.

| Variante / Sistema | Direct (16) | Multi (16) | Recusa / None (8) | **Acerto Geral Estrito (40)** | **Acerto Semântico / Judge (40)** | `gold_hit` | `gold_all` | Contexto Médio (tokens) | Latência Média (s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`baseline_r1` ($k=4$)** | 0.38 | 0.31 | 1.00 | **0.48** | — | 0.91 | 0.78 | 1.959 | 5.40s |
| **`rerank_en` ($n=12 \to k=4$)** | 0.19 | 0.38 | 1.00 | **0.42** | — | 0.97 | 0.88 | 1.999 | 5.82s |
| **`compress` ($k=4$ comprimido)** | 0.38 | 0.25 | 1.00 | **0.45** | — | 1.00 | 0.88 | 539 | 6.16s |
| **`rerank_ml` ($n=12 \to k=4$)** | 0.44 | 0.44 | 1.00 | **0.55** | — | 1.00 | 0.88 | 2.011 | 5.89s |
| **`rerank_ml_n20` ($n=20 \to k=4$)** | 0.44 | 0.44 | 1.00 | **0.55** | — | 1.00 | 0.91 | 2.029 | 6.44s |
| **`order` ($k=12$ nas pontas)** | 0.69 | 0.50 | 0.88 | **0.65** | — | 1.00 | 0.97 | 5.846 | 7.91s |
| **`baseline_k12` ($k=12$)** | 0.81 | 0.50 | 0.75 | **0.68** | — | 1.00 | 0.97 | 5.846 | 7.65s |
| **`rerank_order` ($n=12$, rerank + pontas)** | 0.75 | **0.75** | **1.00** | **0.80** | — | 1.00 | 0.97 | 5.846 | 8.37s |
| **ChatGPT (Web)** | **0.88** *(1.00)* | **0.81** *(0.88)* | **1.00** | **0.88** | **0.93** *(ou 0.88 real)* | **1.00** | **1.00** | — | — |
| **NotebookLM (Web)** | **1.00** | **1.00** | **1.00** | **1.00** | **1.00** | **1.00** | **1.00** | — | — |

---

## 3. Análise Crítica do ChatGPT: Grader Léxico vs. Falhas Reais de RAG Interno

A avaliação do `respostas-chatgpt.json` trouxe um achado metodológico riquíssimo para o trabalho, pois separa claramente **falsos negativos do grader léxico** de **falhas reais de recuperação (RAG interno) do ChatGPT**:

### 3.1. Falsos Negativos do Grader Léxico (3 casos em que o ChatGPT acertou semanticamente)
O arquivo `results/external/para_auditar_judge.json` apontou 5 reprovações do ChatGPT no `grade` estrito. Dessas 5, **3 foram apenas variações de formatação/paráfrase**:
- **`d09` (`direct`):** O gabarito exigia `"28/04/2026"`, e o ChatGPT escreveu por extenso: `"28 de abril de 2026, DCA nº 019/2026. [Arquivo1.md]"`.
- **`d16` (`direct`):** O gabarito exigia `"16/12/2020"`, e o ChatGPT escreveu por extenso: `"...em 16 de dezembro de 2020. [Arquivo6.md]"`.
- **`m08` (`multi`):** O gabarito exigia o substantivo `"confirmação"`, e o ChatGPT usou o verbo `"confirmar a existência de tratamento"`.

Considerando esses 3 acertos semânticos, o ChatGPT atinge **100% nas perguntas `direct` (16/16)**.

### 3.2. Falhas Reais do RAG Interno do ChatGPT em Perguntas Multi-Documento (4 casos!)
Mesmo sendo um modelo de fronteira, o ChatGPT na interface web **não injeta os 6 arquivos inteiros no prompt**: ele utiliza sua ferramenta interna de busca em chunks (*File Search*). A própria resposta do ChatGPT em `m07` e `m16` entrega esse comportamento ao dizer ***"no trecho consultado"***. Isso causou **4 falhas reais em perguntas `multi`**:

1. **`m11` (Reprovado no Grader e no Judge — Falha de Rodapé):**
   - *Pergunta:* Comparar a data de aprovação do Código de Conduta da Vale (`28/04/2026`) com o da Petrobras (`27/09/2024`, que fica na linha 481 — última linha do `Arquivo2.md`).
   - *Resposta do ChatGPT:* *"O Código de Conduta da Vale registra aprovação pelo Conselho de Administração em 28/04/2026... **Os documentos fornecidos não informam a data específica de aprovação do Código de Conduta Ética da Petrobras.** [Arquivo2.md]"*
   - *Diagnóstico:* Como o `Arquivo2.md` é o maior documento do corpus (~50 KB), o retriever interno do ChatGPT não recuperou o último chunk do arquivo e afirmou falsamente que a informação não existe! *(Nota: o `rerank_order` local cometeu exatamente o mesmo erro em `m11` pelo mesmo motivo).*

2. **`m15` (Reprovado no Grader — Omissão de Políticas do Final do Documento):**
   - *Pergunta:* Quais códigos `POL` aparecem tanto no `Arquivo1.md` quanto nas Referências do `Arquivo5.md`?
   - *Resposta do ChatGPT:* Listou apenas as políticas do início do documento (`POL-0001-G`, `POL-0005-G`, `POL-0012-G`, `POL-0016-G`, `POL-0019-G`), omitindo `POL-0035-G`, `POL-0037-G` e `POL-0041-G`!
   - *Destaque:* Aqui o **seu RAG local com `rerank_order` superou o ChatGPT**, pois recuperou os chunks certos e listou `POL-0041-G` e `POL-0037-G` corretamente!

3. **`m09` (Falso Positivo Léxico, mas Erro Conceitual do ChatGPT):**
   - *Resposta do ChatGPT:* *"Os documentos **não estabelecem uma conexão expressa** entre o valor 'A vida em primeiro lugar' e diretrizes específicas da Política de Gestão de Riscos."*
   - *Diagnóstico:* O ChatGPT passou no grader léxico apenas porque repetiu a expressão `'A vida em primeiro lugar'` do enunciado ao negar a conexão! Na realidade, o 2º parágrafo do `Arquivo5.md` (Política de Gestão de Riscos da Vale) diz literalmente: *"'A Vida em Primeiro Lugar' é um valor primordial que norteia as atividades da Vale."* Tanto o **NotebookLM** quanto o **seu `rerank_order` local** encontraram essa conexão que o ChatGPT perdeu.

4. **`m16` (Falso Positivo Léxico, mas Recuperação Incompleta do ChatGPT no `Arquivo4.md`):**
   - *Resposta do ChatGPT:* Citou corretamente a definição e a `biometria facial` do `Arquivo3.md` (Vale), mas sobre a Petrobras escreveu: *"A cartilha da Petrobras trata dados pessoais sensíveis como uma categoria que exige atenção específica, **mas a definição completa e os exemplos solicitados não foram identificados no trecho consultado.** [Arquivo4.md]"*
   - *Diagnóstico:* Novamente, o chunk da página 1 da cartilha da Petrobras (`Arquivo4.md`, linha 33) ficou de fora da busca interna do ChatGPT, enquanto o **NotebookLM** e o **seu `rerank_order` local** recuperaram a definição completa de ambos os documentos.

---

## 4. Comparativo Direto dos 3 Sistemas nas Perguntas Críticas

| Caso | RAG Local (`rerank_order` - Qwen 3B) | ChatGPT Web (File Search) | NotebookLM (Gemini Grounded) |
| :--- | :--- | :--- | :--- |
| **`d09` e `d16` (Datas de aprovação)** | Acertou `d09` (`28/04/2026`); omitiu data em `d16` | Acertou ambas (escreveu a data por extenso) | Acertou ambas no formato exato (`28/04/2026` e `16/12/2020`) |
| **`m09` (Conexão 'A vida em primeiro lugar' e Riscos)** | **Acertou** (encontrou o trecho no `Arquivo5.md`) | **Errou** (disse que não havia conexão expressa) | **Acertou** |
| **`m11` (Datas no rodapé de `Arquivo1` e `Arquivo2`)** | **Errou** (recusou por perder o rodapé no meio de 12 chunks) | **Errou** (disse que `Arquivo2.md` não informa a data) | **Acertou** (`28/04/2026` e `27/09/2024`) |
| **`m15` (Cruzamento exaustivo de códigos `POL`)** | **Acertou** (incluiu `POL-0041-G` e `POL-0037-G`) | **Incompleto** (omitiu `POL-0041-G`, `POL-0035-G`, `POL-0037-G`) | **Acertou** (listou todas as 8 políticas em comum) |
| **`m16` (Dados Sensíveis em `Arquivo3` e `Arquivo4`)** | **Acertou** (trouxe a definição da Vale e da Petrobras) | **Incompleto** (disse que não achou a definição no trecho consultado de `Arquivo4.md`) | **Acertou** |
| **`n01` a `n08` (8 Perguntas-Armadilha sem resposta)** | **100% de recusa correta (8/8)** | **100% de recusa correta (8/8)** | **100% de recusa correta (8/8)** |

---

## 5. Conclusão Geral do Experimento

1. **O NotebookLM foi o único sistema 100% consistente (40/40)** tanto na avaliação léxica quanto na semântica, demonstrando que sua indexação dedicada para documentos mantém visibilidade completa inclusive sobre rodapés (`m11`) e cruzamentos exaustivos de listas (`m15`).
2. **Subir arquivos no ChatGPT Web não garante leitura integral do corpus:** O uso de *File Search* interno fez o ChatGPT falhar justamente em perguntas `multi` que exigiam varrer múltiplos trechos ou ler o rodapé de documentos longos (`m09`, `m11`, `m15`, `m16`). Em **3 dessas 4 perguntas (`m09`, `m15` e `m16`), o pipeline RAG local com `rerank_order` (`qwen2.5:3b`) superou o ChatGPT!**
3. **Importância da Avaliação Dupla (Léxica + Semântica/Judge):** O grader léxico (`must_contain`) subestimou o ChatGPT em `d09`, `d16` e `m08` (por escrever datas por extenso ou usar verbo em vez de substantivo), mas superestimou o ChatGPT em `m09` e `m16` (onde as palavras-chave apareceram dentro de uma frase que dizia não ter encontrado a informação no trecho consultado).

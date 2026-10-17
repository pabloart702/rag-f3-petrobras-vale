# Análise Comparativa: RAG Local (Família 3) vs. NotebookLM

Este relatório consolida a avaliação comparativa sobre o corpus normativo **Petrobras × Vale** (`Arquivo1.md` a `Arquivo6.md`), utilizando o conjunto expandido de **40 perguntas** (`questions.json`: 16 `direct`, 16 `multi` e 8 `none`) e a mesma função de avaliação automática (`grade`).

![Gráfico Comparativo](results/scoreboard_comparativo.png)

---

## 1. Enquadramento Metodológico

| Sistema | Arquitetura | Vantagem Principal | Limitação Observada |
| :--- | :--- | :--- | :--- |
| **RAG Local (`rag-f3-local.ipynb`)** | Embedding denso (`nomic-embed-text`) + Técnicas F3 (*Reranking*, *Compressão*, *Ordering*) + Gerador local (`qwen2.5:3b`) | Execução 100% local, custo zero de API, controle granular sobre *chunking*, *top-k*, reordenação e posicionamento no prompt. | Gerador compacto (3B parâmetros) sofre com *lost in the middle* e excesso de conservadorismo (recusas falsas) em janelas longas (~5.8k tokens). |
| **NotebookLM (`respostas-notebooklm.json`)** | RAG Gerenciado + Modelo de Fronteira (família Gemini) com *grounding* estrito sobre os 6 documentos carregados na íntegra | Capacidade superior de leitura integral e síntese multi-documento (`gold_all = 1.00`), sem perder detalhes de rodapé, glossário ou tabelas. | Caixa-preta (sem controle sobre hiperparâmetros de recuperação ou compressão de tokens) e dependente de interface web/nuvem. |

---

## 2. Placar Consolidado (40 Perguntas)

Os dados brutos encontram-se em `results/summary_comparativo.csv` e `results/results_ext_respostas-notebooklm.csv`.

| Variante / Sistema | Direct (16) | Multi (16) | Recusa / None (8) | **Acerto Geral (40)** | `gold_hit` | `gold_all` | Contexto Médio (tokens) | Latência Média (s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`baseline_r1` ($k=4$)** | 0.38 | 0.31 | 1.00 | **0.48** | 0.91 | 0.78 | 1.959 | 5.40s |
| **`rerank_en` ($n=12 \to k=4$)** | 0.19 | 0.38 | 1.00 | **0.42** | 0.97 | 0.88 | 1.999 | 5.82s |
| **`compress` ($k=4$ comprimido)** | 0.38 | 0.25 | 1.00 | **0.45** | 1.00 | 0.88 | 539 | 6.16s |
| **`rerank_ml` ($n=12 \to k=4$)** | 0.44 | 0.44 | 1.00 | **0.55** | 1.00 | 0.88 | 2.011 | 5.89s |
| **`rerank_ml_n20` ($n=20 \to k=4$)** | 0.44 | 0.44 | 1.00 | **0.55** | 1.00 | 0.91 | 2.029 | 6.44s |
| **`order` ($k=12$ nas pontas)** | 0.69 | 0.50 | 0.88 | **0.65** | 1.00 | 0.97 | 5.846 | 7.91s |
| **`baseline_k12` ($k=12$)** | 0.81 | 0.50 | 0.75 | **0.68** | 1.00 | 0.97 | 5.846 | 7.65s |
| **`rerank_order` ($n=12$, rerank + pontas)** | 0.75 | **0.75** | **1.00** | **0.80** | 1.00 | 0.97 | 5.846 | 8.37s |
| **NotebookLM (Web)** | **1.00** | **1.00** | **1.00** | **1.00** | **1.00** | **1.00** | — | — |

---

## 3. Principais Conclusões sobre as Técnicas da Família 3 (F3)

1. **Impacto do Reranker Multilíngue (`rerank_en` vs. `rerank_ml`):**
   - O cross-encoder em inglês (`ms-marco-MiniLM-L-6-v2`) degradou o acerto em perguntas diretas de **38% para 19%**, pois rebaixou chunks em português que continham termos técnicos e siglas.
   - A troca pelo cross-encoder multilíngue (`mmarco-mMiniLMv2-L12-H384-v1`) elevou `gold_hit` para **100%**, `gold_all` de **78% para 88%** e subiu o acerto geral de **48% para 55%** mantendo apenas $k=4$ chunks no prompt.

2. **Diagnóstico do *Lost in the Middle* (`baseline_k12` vs. `rerank_order`):**
   - Aumentar a janela para $k=12$ (`baseline_k12`) resolveu quase toda a recuperação (`gold_all = 97%`) e subiu o acerto em perguntas `direct` para **81%**, mas causou dois efeitos colaterais clássicos:
     - **Queda nas recusas (`none` caiu de 1.00 para 0.75):** Com muito ruído no contexto, o modelo deixou de recusar em `n02` e `n04`.
     - **Estagnação nas perguntas `multi` (50%):** Quando o segundo documento necessário caía no meio do prompt (posições 5 a 9), o `qwen2.5:3b` ignorava uma das empresas.
   - Ao aplicar o **Reranking + Ordering nas pontas (`rerank_order`)**, colocando os melhores chunks no início e no fim do prompt:
     - O acerto em `multi` saltou de **50% para 75%** (recuperando `m01`, `m04`, `m12` e `m15`).
     - A taxa de recusa correta em `none` voltou para **100%**.
     - O acerto geral atingiu **80%** (+32 pontos percentuais acima do `baseline_r1`).

3. **Compressão Extrativa (`compress`):**
   - Reduziu o consumo de contexto em **73%** (de 1.959 para **539 tokens** em média), mas perdeu detalhes em perguntas compostas (`multi` = 25%) porque o filtro por frases isoladas descarta cabeçalhos ou linhas vizinhas de tabelas/glossários.

---

## 4. Diagnóstico Detalhado: Onde o Melhor RAG Local (`rerank_order` = 80%) Perdeu para o NotebookLM (100%)

Dos 40 casos, o `rerank_order` errou apenas **8 perguntas** frente ao gabarito estrito, enquanto o NotebookLM acertou todas as 40. A inspeção linha a linha revela a natureza exata desses 8 erros:

| ID | Tier | `gold_all` no `rerank_order` | Posições dos Chunks Gold | Tipo de Falha no RAG Local (`qwen2.5:3b`) | Como o NotebookLM Respondeu |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **`d04`** | `direct` | `True` | `1` | **Recusa indevida (Falso Negativo):** Mesmo com `Arquivo6.md` no topo (posição 1), o `qwen2.5:3b` respondeu *"Os documentos corporativos não cobrem esta informação."* | Identificou diretamente o `Conselho de Administração (CA)` no item 5.1.1 de `[Arquivo6.md]`. |
| **`d05`** | `direct` | `True` | `2` | **Recusa indevida (Falso Negativo):** O chunk de `Arquivo4.md` estava na posição 2, mas o gerador 3B recusou. | Identificou o `Gerente Geral de Privacidade` em `[Arquivo4.md]`. |
| **`d06`** | `direct` | `True` | `1\|2\|3\|8\|11` | **Recusa indevida (Falso Negativo):** `Arquivo5.md` estava nas posições 1, 2 e 3, mas o gerador 3B recusou. | Listou `ISO 31000`, `ISO 55000`, `COSO-ERM` e `RBPS` citando `[Arquivo5.md]`. |
| **`d16`** | `direct` | `True` | `1\|7` | **Resposta parcial (Omissão da 2ª metade):** Citou o `artigo 16` do Estatuto Social, mas esqueceu de informar a data de aprovação (`16/12/2020`) pedida no final da pergunta. | Respondeu ambos os fatos (`artigo 16` e `16/12/2020`) citando `[Arquivo6.md]`. |
| **`m02`** | `multi` | `False` | `1` | **Falha de Recuperação Parcial:** Único caso da bateria em que faltou 1 documento gold entre os 12 candidatos (`Arquivo3.md` ficou de fora; só entrou `Arquivo4.md`). | Cruzou a definição conceitual do DPO em `[Arquivo3.md]` (canal com a `ANPD`) com o cargo em `[Arquivo4.md]` (`Gerente Geral de Privacidade`). |
| **`m10`** | `multi` | `True` | `1\|2\|3\|5..12` | **Recusa indevida em pergunta de síntese:** O `qwen2.5:3b` iniciou com a frase de recusa por achar que a conexão não estava explícita. | Articulou o princípio 3.3 de `[Arquivo6.md]` (atuar de forma `ética`) com a análise de riscos na tomada de decisão em `[Arquivo2.md]`. |
| **`m11`** | `multi` | `True` | `2\|3\|4..12` | **Detalhe de rodapé perdido no meio do contexto:** A data de aprovação está na última linha de `Arquivo1.md` e `Arquivo2.md`; o gerador 3B não localizou ambas e recusou. | Extraiu com precisão `28/04/2026` (`[Arquivo1.md]`) e `27/09/2024` (`[Arquivo2.md]`). |
| **`m13`** | `multi` | `True` | `1\|2\|3\|4\|6\|9\|11\|12` | **Confusão entre entidades na síntese:** Atribuiu `Comitê Executivo` tanto para a Vale quanto para a Petrobras, omitindo a `Diretoria Executiva` da Petrobras. | Distinguiu claramente `Comitê Executivo` (`[Arquivo5.md]`) e `Diretoria Executiva (DE)` (`[Arquivo6.md]`). |

---

## 5. Síntese Executiva

- **A recuperação local + F3 é altamente eficaz:** Com `rerank_order`, o pipeline local entregou todos os documentos necessários no contexto em **97% das perguntas respondíveis (`gold_all = 0.97`)** e eliminou 100% das alucinações nas perguntas sem resposta (`none = 1.00`).
- **A diferença entre 80% (`rerank_order`) e 100% (`NotebookLM`) é majoritariamente de capacidade do modelo gerador, e não de recuperação:** Em **7 dos 8 erros** do `rerank_order`, os documentos corretos estavam presentes no prompt (`gold_all = True`), mas o modelo compacto (`qwen2.5:3b`) recusou por excesso de cautela ou omitiu a segunda parte de perguntas compostas.


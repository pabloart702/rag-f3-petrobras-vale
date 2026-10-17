# Prompts para Coleta Externa (NotebookLM, Claude, Gemini) e LLM-as-a-Judge

Este arquivo contém os **2 lotes de 20 perguntas** (total de **40 perguntas**: 16 `direct`, 16 `multi`, 8 `none`, sem o gabarito) prontos para copiar e colar na interface web do **NotebookLM**, **Claude** ou **Gemini**, além de um lote avulso apenas com `n01` a `n08` e o prompt de **LLM-as-a-Judge**.

---

## Como coletar as respostas na interface Web

1. Faça upload dos 6 arquivos da pasta `corpus/` (`Arquivo1.md` a `Arquivo6.md`) no NotebookLM e no Claude/Gemini.
2. Envie **um lote por vez** (copiando o bloco completo do Lote 1 e depois do Lote 2).
3. Salve os blocos JSON devolvidos por cada ferramenta em:
   - `results/external/notebooklm.json` (ou `respostas-notebooklm.json`)
   - `results/external/claude.json`
   - `results/external/gemini.json`
   *(Dica: o script `compare_external.py` aceita tanto um único JSON `[...]` com as 40 respostas quanto os blocos `[...]` colados um embaixo do outro no mesmo arquivo!)*

---

## Lote 1 de 2 (`d01` a `d16` e `m01` a `m04` — 20 perguntas)

Copie e cole o bloco abaixo:

```text
Você é o assistente especialista em governança, conformidade e políticas corporativas da Petrobras e da Vale.
Responda às 20 perguntas abaixo utilizando APENAS o contexto dos 6 documentos fornecidos (Arquivo1.md a Arquivo6.md).
Regras obrigatórias:
1. Se os documentos fornecidos não contiverem a resposta, responda exatamente: "Os documentos corporativos não cobrem esta informação."
2. Cite a fonte de cada fato entre colchetes usando o nome exato do arquivo, como por exemplo [Arquivo1.md].
3. Responda APENAS com um array JSON válido no formato [{"id": "d01", "answer": "..."}, ...], mantendo exatamente os IDs fornecidos.

Perguntas (Lote 1/2):
[
  {"id": "d01", "question": "Qual é o papel do Encarregado de Dados (DPO) segundo o Aviso Externo de Privacidade da Vale?"},
  {"id": "d02", "question": "De quanto em quanto tempo o Código de Conduta da Vale deve ser revisado no máximo?"},
  {"id": "d03", "question": "Qual é o número de telefone do Canal de Acolhimento disponibilizado para a força de trabalho da Petrobras?"},
  {"id": "d04", "question": "Qual órgão da Petrobras é responsável por aprovar o apetite a risco da companhia?"},
  {"id": "d05", "question": "Quem exerce a função de Encarregado pelo tratamento de dados pessoais na estrutura da Petrobras?"},
  {"id": "d06", "question": "Quais são as referências de normas e padrões internacionais adotadas na gestão de riscos da Vale?"},
  {"id": "d07", "question": "Quem é o Presidente do Conselho de Administração da Vale citado na mensagem de liderança do Código de Conduta?"},
  {"id": "d08", "question": "Qual sistema eletrônico da CGU é indicado pela Petrobras para realizar consultas sobre conflito de interesses?"},
  {"id": "d09", "question": "Qual é a data e o código da deliberação (DCA) de aprovação da revisão do Código de Conduta da Vale pelo Conselho de Administração?"},
  {"id": "d10", "question": "No glossário do Código de Conduta da Vale, como é definido o termo 'Tipping' (Informações Privilegiadas)?"},
  {"id": "d11", "question": "Qual é o endereço de e-mail da Comissão de Ética da Petrobras para esclarecer dúvidas de interpretação sobre o Código de Conduta Ética?"},
  {"id": "d12", "question": "Segundo o glossário do Código de Conduta Ética da Petrobras, qual é a diferença entre 'informação confidencial' e 'informação secreta'?"},
  {"id": "d13", "question": "Em que data foi revisado o Aviso Externo de Privacidade do Brasil da Vale e qual lei de registros da internet além da LGPD é mencionada nele?"},
  {"id": "d14", "question": "Na cartilha de Proteção de Dados Pessoais da Petrobras, qual exemplo prático do cotidiano é usado para ilustrar os papéis de Titular, Controlador e Operador?"},
  {"id": "d15", "question": "Segundo a Política de Gestão de Riscos da Vale, como são definidos os 'Riscos Emergentes' e qual o horizonte temporal em que não se espera sua materialização?"},
  {"id": "d16", "question": "Qual artigo do Estatuto Social da Petrobras é citado na seção de Aplicação e Abrangência da Política de Gestão de Riscos Empresariais e qual a data de sua aprovação pelo CA?"},
  {"id": "m01", "question": "Qual a diferença na periodicidade máxima de revisão do Código de Conduta entre a Petrobras e a Vale?"},
  {"id": "m02", "question": "Como o papel do Encarregado (DPO) é definido no documento da Vale em comparação com quem ocupa essa função na Petrobras?"},
  {"id": "m03", "question": "Qual é o período regular de revisão da Política de Gestão de Riscos na Vale e qual a ata de aprovação da política da Petrobras?"},
  {"id": "m04", "question": "Quais são os valores centrais declarados no Código de Conduta da Vale e no Código de Conduta Ética da Petrobras?"}
]
```

---

## Lote 2 de 2 (`m05` a `m16` e `n01` a `n08` — 20 perguntas)

Copie e cole o bloco abaixo:

```text
Continue respondendo às últimas 20 perguntas utilizando APENAS os 6 documentos fornecidos (Arquivo1.md a Arquivo6.md).
Regras obrigatórias:
1. Se os documentos fornecidos não contiverem a resposta, responda exatamente: "Os documentos corporativos não cobrem esta informação."
2. Cite a fonte de cada fato entre colchetes usando o nome exato do arquivo, como por exemplo [Arquivo1.md].
3. Responda APENAS com um array JSON válido no formato [{"id": "m05", "answer": "..."}, ...], mantendo exatamente os IDs fornecidos.

Perguntas (Lote 2/2):
[
  {"id": "m05", "question": "Quais são as multas administrativas máximas previstas na LGPD segundo o guia da Petrobras e quais medidas técnicas de segurança (como criptografia e backups) são destacadas no Aviso de Privacidade da Vale?"},
  {"id": "m06", "question": "Como o modelo de Linhas de Defesa é estruturado na gestão de riscos da Vale em comparação com a diretriz de segregação de funções e o papel da Auditoria Interna na Política de Gestão de Riscos da Petrobras?"},
  {"id": "m07", "question": "Quais são os canais oficiais para realizar denúncias de desvios de conduta na Vale e na Petrobras?"},
  {"id": "m08", "question": "Quais direitos dos titulares de dados pessoais são destacados tanto no aviso da Vale quanto no guia da Petrobras?"},
  {"id": "m09", "question": "De que forma o valor 'A vida em primeiro lugar' da Vale se conecta com suas diretrizes de Gestão de Riscos?"},
  {"id": "m10", "question": "Como a Petrobras articula o compromisso ético de seu Código de Conduta com a sua Política de Gestão de Riscos Empresariais?"},
  {"id": "m11", "question": "Compare a data de aprovação pelo Conselho de Administração do Código de Conduta da Vale com a data de aprovação do Código de Conduta Ética da Petrobras."},
  {"id": "m12", "question": "Como o 'Assédio Moral' é definido no glossário do Código de Conduta da Vale em comparação com o glossário do Código de Conduta Ética da Petrobras?"},
  {"id": "m13", "question": "Quem é responsável por propor o Apetite a Risco ao Conselho de Administração na Política de Gestão de Riscos da Vale e na Política de Gestão de Riscos Empresariais da Petrobras?"},
  {"id": "m14", "question": "Qual o papel do Comitê de Auditoria e Riscos na Vale e do Comitê de Auditoria Estatutário na Petrobras segundo suas respectivas políticas de gestão de riscos?"},
  {"id": "m15", "question": "Quais políticas corporativas (códigos POL) são referenciadas tanto no Código de Conduta da Vale quanto na seção de Referências da Política de Gestão de Riscos da Vale?"},
  {"id": "m16", "question": "Como são definidos os 'Dados Pessoais Sensíveis' no Aviso Externo de Privacidade da Vale e na cartilha de Proteção de Dados Pessoais da Petrobras, e que exemplos específicos (como biometria facial) o aviso da Vale traz?"},
  {"id": "n01", "question": "Qual é o valor numérico exato do orçamento anual destinado ao plano de investimentos em segurança de barragens da Vale para o ano de 2026?"},
  {"id": "n02", "question": "Qual é o nome completo e o cargo do Gerente Geral do Canal de Denúncias da Petrobras mencionado nos normativos?"},
  {"id": "n03", "question": "Qual é o limite máximo em reais (R$) permitido para o recebimento de brindes ou hospitalidades por empregados da Vale e da Petrobras segundo os Códigos de Conduta?"},
  {"id": "n04", "question": "Qual é o prazo máximo em horas que a Petrobras e a Vale têm para notificar a ANPD após a detecção de um vazamento de dados pessoais nos documentos fornecidos?"},
  {"id": "n05", "question": "Qual é o endereço de e-mail e o nome completo do Encarregado de Dados (DPO) da Vale informados no Aviso Externo de Privacidade?"},
  {"id": "n06", "question": "Quantos relatos de desvios de conduta a Vale recebeu no último ano segundo o Relatório do Programa de Ética & Compliance citado no Código de Conduta?"},
  {"id": "n07", "question": "Qual é a taxa de desconto financeiro aplicada aos fornecedores da Petrobras que não assinam o Guia de Conduta Ética para Fornecedores?"},
  {"id": "n08", "question": "Quais são os 5 Temas de Risco Prioritários listados nominalmente no Mapa Integrado de Riscos da Política de Gestão de Riscos da Vale (POL-0009-G)?"}
]
```

---

## Lote Avulso: Apenas `n01` a `n08`

```text
Continue respondendo às últimas 8 perguntas utilizando APENAS os 6 documentos fornecidos (Arquivo1.md a Arquivo6.md).
Regras obrigatórias:
1. Se os documentos fornecidos não contiverem a resposta, responda exatamente: "Os documentos corporativos não cobrem esta informação."
2. Cite a fonte de cada fato entre colchetes usando o nome exato do arquivo, como por exemplo [Arquivo1.md].
3. Responda APENAS com um array JSON válido no formato [{"id": "n01", "answer": "..."}, ...], mantendo exatamente os IDs fornecidos.

Perguntas (n01 a n08):
[
  {"id": "n01", "question": "Qual é o valor numérico exato do orçamento anual destinado ao plano de investimentos em segurança de barragens da Vale para o ano de 2026?"},
  {"id": "n02", "question": "Qual é o nome completo e o cargo do Gerente Geral do Canal de Denúncias da Petrobras mencionado nos normativos?"},
  {"id": "n03", "question": "Qual é o limite máximo em reais (R$) permitido para o recebimento de brindes ou hospitalidades por empregados da Vale e da Petrobras segundo os Códigos de Conduta?"},
  {"id": "n04", "question": "Qual é o prazo máximo em horas que a Petrobras e a Vale têm para notificar a ANPD após a detecção de um vazamento de dados pessoais nos documentos fornecidos?"},
  {"id": "n05", "question": "Qual é o endereço de e-mail e o nome completo do Encarregado de Dados (DPO) da Vale informados no Aviso Externo de Privacidade?"},
  {"id": "n06", "question": "Quantos relatos de desvios de conduta a Vale recebeu no último ano segundo o Relatório do Programa de Ética & Compliance citado no Código de Conduta?"},
  {"id": "n07", "question": "Qual é a taxa de desconto financeiro aplicada aos fornecedores da Petrobras que não assinam o Guia de Conduta Ética para Fornecedores?"},
  {"id": "n08", "question": "Quais são os 5 Temas de Risco Prioritários listados nominalmente no Mapa Integrado de Riscos da Política de Gestão de Riscos da Vale (POL-0009-G)?"}
]
```

---

## Prompt Opcional: LLM-as-a-Judge (Avaliação Semântica com Gabarito)

Depois de coletar as respostas e rodar o script `compare_external.py`, o próprio script exporta apenas os casos em que o grader léxico marcou `False` (em `results/external/para_auditar_judge.json`) para você auditar se foi erro real ou apenas paráfrase:

```text
Você é um avaliador rigoroso de sistemas RAG (LLM-as-a-Judge).
Você receberá:
1. O gabarito oficial (`questions.json`), onde cada item possui:
   - `id`, `tier` ("direct", "multi", "none"), `question`
   - `gold_docs`: documentos de onde a informação deve vir
   - `must_contain`: conceitos/termos obrigatórios (quando for uma sublista, basta um dos termos equivalentes)
   - `expect_refusal`: se `true`, a resposta DEVE recusar responder afirmando que os documentos não cobrem a informação, sem inventar ou inferir valores externos.
2. As respostas geradas por um sistema (`[{"id": "...", "answer": "..."}]`).

Sua tarefa é avaliar cada resposta semanticamente:
- Para itens com `expect_refusal: false`: marque `"judge_correct": true` se a resposta contiver todos os fatos/conceitos exigidos em `must_contain` (mesmo que escritos com sinônimos, por extenso ou paráfrase fiel aos documentos) e não se recusar a responder. Caso falte algum fato exigido, marque `false`.
- Para itens com `expect_refusal: true`: marque `"judge_correct": true` se o modelo deixar claro que a informação exata pedida não consta nos documentos fornecidos (mesmo que não use a frase literal padrão), desde que não invente o dado pedido.

Retorne APENAS um array JSON no formato:
[
  {"id": "d01", "judge_correct": true, "reason": "Breve justificativa de 1 linha"}
]
```

"""
Script para processar e comparar as respostas coletadas externamente
(NotebookLM, Claude, Gemini, etc.) com os resultados do notebook RAG local.

Como usar (após coletar as respostas):
1. Coloque os arquivos com as respostas em `results/external/`, por exemplo:
   - `results/external/notebooklm.json`
   - `results/external/claude.json`
   - `results/external/gemini.json`
   (Você pode colar os 3 lotes JSON no mesmo arquivo, mesmo com blocos ```json, que o parser junta automaticamente!)
2. Se tiver rodado o prompt de LLM-as-a-Judge, salve em:
   - `results/external/notebooklm_judge.json` (opcional)
   - `results/external/claude_judge.json` (opcional)
   - `results/external/gemini_judge.json` (opcional)
3. Execute:
   python compare_external.py
"""

import glob
import json
import os
import re
import sys
import unicodedata
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

QUESTIONS_PATH = "questions.json"
RESULTS_DIR = "results"
EXTERNAL_DIR = os.path.join(RESULTS_DIR, "external")


def norm(s: str) -> str:
    """Minúsculas, sem acento, espaços colapsados (idêntico ao lesson09_F3_v2.ipynb)."""
    s = unicodedata.normalize("NFKD", str(s).lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip()


REFUSAL = norm("Os documentos corporativos não cobrem esta informação")
REFUSAL_CORE = "nao cobrem esta informacao"

# Padrões adicionais de recusa comuns em interfaces web (NotebookLM / Claude / Gemini)
WEB_REFUSAL_PATTERNS = [
    "nao cobrem esta informacao",
    "nao consta nos documentos",
    "nao constam nos documentos",
    "nao ha informacao nos documentos",
    "nao mencionam",
    "nao menciona",
    "nao fornecem essa informacao",
    "nao trazem essa informacao",
    "nao especificam",
    "nao informa o valor",
    "nao e mencionado",
    "nao e mencionada",
]


def _kw_ok(answer_n: str, kw) -> bool:
    alts = kw if isinstance(kw, (list, tuple)) else [kw]
    return any(norm(a) in answer_n for a in alts)


def grade_strict(answer: str, q: dict) -> tuple[bool, bool]:
    """Grader estrito idêntico ao notebook."""
    a = norm(answer)
    refused = REFUSAL in a or REFUSAL_CORE in a
    if q["expect_refusal"]:
        return refused, refused
    return all(_kw_ok(a, kw) for kw in q["must_contain"]) and not refused, refused


def grade_web_lenient_refusal(answer: str, q: dict) -> tuple[bool, bool]:
    """Igual ao grader do notebook, mas aceita frases equivalentes de recusa caso a IA web não use a frase literal."""
    a = norm(answer)
    refused = any(pat in a for pat in WEB_REFUSAL_PATTERNS)
    if q["expect_refusal"]:
        return refused, refused
    strict_refused = REFUSAL in a or REFUSAL_CORE in a
    return all(_kw_ok(a, kw) for kw in q["must_contain"]) and not strict_refused, strict_refused


def extract_cited_docs(answer: str) -> list[str]:
    """Extrai menções a Arquivo1.md .. Arquivo6.md na resposta para medir citação das fontes gold."""
    found = re.findall(r"Arquivo[1-6](?:\.md)?", str(answer), flags=re.IGNORECASE)
    docs = []
    for f in found:
        num = re.search(r"[1-6]", f).group(0)
        doc_name = f"Arquivo{num}.md"
        if doc_name not in docs:
            docs.append(doc_name)
    return docs


def parse_flexible_json_file(path: str) -> dict[str, dict]:
    """
    Lê um arquivo contendo um ou mais arrays JSON (ex.: os 3 lotes colados em sequência,
    com ou sem cercas markdown ```json) e devolve um dicionário {id: item_dict}.
    """
    raw = open(path, encoding="utf-8").read()
    # Remove cercas ```json ... ``` e escapamentos inválidos como \$
    cleaned = re.sub(r"```(?:json)?", "", raw, flags=re.IGNORECASE).replace(r"\$", "$").strip()

    items_by_id = {}
    decoder = json.JSONDecoder()
    idx = 0
    while idx < len(cleaned):
        # Procura início de lista '[' ou objeto '{'
        m = re.search(r"[\[\{]", cleaned[idx:])
        if not m:
            break
        start = idx + m.start()
        try:
            obj, end = decoder.raw_decode(cleaned, start)
            if isinstance(obj, list):
                for entry in obj:
                    if isinstance(entry, dict) and "id" in entry:
                        items_by_id[str(entry["id"]).strip()] = entry
            elif isinstance(obj, dict) and "id" in obj:
                items_by_id[str(obj["id"]).strip()] = obj
            idx = end
        except json.JSONDecodeError:
            idx = start + 1
    return items_by_id


def evaluate_external_model(
    model_label: str,
    answers_path: str,
    questions: list[dict],
    judge_path: str | None = None,
) -> pd.DataFrame:
    """Avalia as respostas de um modelo externo e gera DataFrame compatível com os CSVs do notebook."""
    ans_map = parse_flexible_json_file(answers_path)
    judge_map = parse_flexible_json_file(judge_path) if (judge_path and os.path.exists(judge_path)) else {}

    records = []
    missing_ids = []

    for q in questions:
        qid = q["id"]
        item = ans_map.get(qid, {})
        if not item:
            missing_ids.append(qid)
        answer = str(item.get("answer", "")).strip()

        correct_strict, refused_strict = grade_strict(answer, q)
        correct_lenient, _ = grade_web_lenient_refusal(answer, q)

        # Verifica se há avaliação do LLM-as-a-Judge no próprio item ou em arquivo separado
        judge_val = item.get("judge_correct")
        judge_reason = item.get("reason", "")
        if judge_val is None and qid in judge_map:
            judge_val = judge_map[qid].get("judge_correct")
            judge_reason = judge_map[qid].get("reason", "")

        # Citações extraídas da resposta
        cited_docs = extract_cited_docs(answer)
        gold = set(q["gold_docs"])
        gold_hit = bool(gold.intersection(cited_docs)) if gold else False
        gold_all = gold.issubset(set(cited_docs)) if gold else None

        # Define nota final: se houver judge_correct explícito, salva na coluna dedicada
        final_correct = bool(judge_val) if judge_val is not None else correct_strict

        missing_kws = []
        if not q["expect_refusal"]:
            ans_n = norm(answer)
            for kw in q["must_contain"]:
                if not _kw_ok(ans_n, kw):
                    missing_kws.append(kw)

        records.append({
            "label": model_label,
            "run": 1,
            "temperature": np.nan,
            "k": "web",
            "id": qid,
            "tier": q["tier"],
            "question": q["question"],
            "retrieved_ids": "",
            "retrieved_docs": "|".join(cited_docs),
            "n_hits": len(cited_docs),
            "gold_docs": "|".join(q["gold_docs"]),
            "gold_hit": gold_hit,
            "gold_all": gold_all,
            "gold_rank": 1 if (cited_docs and cited_docs[0] in gold) else None,
            "gold_positions": "",
            "answer": answer,
            "correct": final_correct,
            "correct_strict": correct_strict,
            "correct_lenient_refusal": correct_lenient,
            "judge_correct": judge_val,
            "judge_reason": judge_reason,
            "missing_keywords": json.dumps(missing_kws, ensure_ascii=False) if missing_kws else "",
            "refused": refused_strict,
            "llm_calls": 1,
            "latency_s": np.nan,
            "ctx_tokens": np.nan,
        })

    if missing_ids:
        print(f"  ⚠ [{model_label}] {len(missing_ids)} perguntas sem resposta no JSON: {missing_ids}")

    return pd.DataFrame(records)


def export_candidates_for_llm_judge(df_ext: pd.DataFrame, questions: list[dict], out_path: str):
    """
    Gera um arquivo JSON enxuto apenas com as respostas que reprovaram no grader léxico estrito,
    facilitando a revisão rápida via LLM-as-a-Judge.
    """
    q_by_id = {q["id"]: q for q in questions}
    failed = df_ext[~df_ext["correct_strict"].astype(bool)]
    payload = []
    for _, row in failed.iterrows():
        q = q_by_id[row["id"]]
        payload.append({
            "model": row["label"],
            "id": row["id"],
            "tier": row["tier"],
            "question": row["question"],
            "gold_docs": q["gold_docs"],
            "must_contain": q["must_contain"],
            "expect_refusal": q["expect_refusal"],
            "answer": row["answer"],
            "missing_keywords": row["missing_keywords"],
        })
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"  → Salvo arquivo de auditoria para LLM Judge ({len(payload)} casos): {out_path}")


def build_comparative_summary(dfs: list[pd.DataFrame]) -> pd.DataFrame:
    """Gera a tabela comparativa consolidada (variantes do notebook + IAs externas)."""
    df = pd.concat(dfs, ignore_index=True)
    df["correct"] = df["correct"].astype(float)

    ans = df[df["tier"] != "none"].copy()
    ans["gold_hit"] = ans["gold_hit"].astype(float)
    ans["gold_all"] = pd.to_numeric(
        ans["gold_all"].map({True: 1.0, False: 0.0, "True": 1.0, "False": 0.0}),
        errors="coerce",
    )

    acc = df.pivot_table(index="label", columns="tier", values="correct", aggfunc="mean")
    for t in ["direct", "multi", "none"]:
        if t not in acc.columns:
            acc[t] = np.nan

    extra = df.groupby("label").agg(
        overall=("correct", "mean"),
        ctx_tokens=("ctx_tokens", "mean"),
        latency_s=("latency_s", "mean"),
    )
    retr = ans.groupby("label").agg(
        gold_hit=("gold_hit", "mean"),
        gold_all=("gold_all", "mean"),
    )

    out = acc.join(extra).join(retr)[
        ["direct", "multi", "none", "overall", "gold_hit", "gold_all", "ctx_tokens", "latency_s"]
    ].round(2)
    return out


def plot_comparative_scoreboard(summary: pd.DataFrame, n_questions: int, out_path: str):
    """Plota gráfico comparando as variantes locais do notebook com NotebookLM / Claude / Gemini."""
    tiers = ["direct", "multi", "none", "overall"]
    tier_labels = ["Direct", "Multi", "Recusa (None)", "Geral (Overall)"]
    labels = [l for l in summary.index if not str(l).startswith("baseline_t03")]

    x = np.arange(len(tiers))
    w = min(0.85 / max(len(labels), 1), 0.15)

    fig, ax = plt.subplots(figsize=(13, 5.5))
    palette = [
        "#9A9A9A", "#6E6E6E", "#E6B566", "#C98A2B", "#2F7D5B",
        "#4C78A8", "#8E5BA8", "#D95F02", "#1B9E77", "#7570B3", "#E7298A",
    ]

    for j, lab in enumerate(labels):
        vals = [summary.loc[lab, t] for t in tiers]
        offset = (j - (len(labels) - 1) / 2) * w
        bars = ax.bar(x + offset, vals, w, label=lab, color=palette[j % len(palette)])
        for b in bars:
            h = b.get_height()
            if not np.isnan(h):
                ax.text(
                    b.get_x() + b.get_width() / 2,
                    h + 0.015,
                    f"{h:.2f}",
                    ha="center",
                    va="bottom",
                    fontsize=7,
                    rotation=90 if len(labels) > 6 else 0,
                )

    ax.set_xticks(x)
    ax.set_xticklabels(tier_labels)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Taxa de Acerto")
    ax.set_title(f"Comparativo RAG Local (F3) vs. Sistemas Externos ({n_questions} perguntas)", loc="left")
    ax.legend(frameon=False, fontsize=8.5, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.10))
    ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    print(f"Gráfico salvo em: {out_path}")


def main():
    os.makedirs(EXTERNAL_DIR, exist_ok=True)
    with open(QUESTIONS_PATH, encoding="utf-8") as f:
        questions = json.load(f)
    print(f"Carregadas {len(questions)} perguntas de {QUESTIONS_PATH}")

    all_dfs = []

    # 1. Carrega resultados existentes do notebook em results/ (se compatíveis)
    notebook_csvs = [
        ("baseline_r1", os.path.join(RESULTS_DIR, "baseline_r1.csv")),
        ("baseline_k12", os.path.join(RESULTS_DIR, "results_baseline_k12.csv")),
        ("rerank_en", os.path.join(RESULTS_DIR, "results_rerank_en.csv")),
        ("rerank_ml", os.path.join(RESULTS_DIR, "results_rerank_ml.csv")),
        ("compress", os.path.join(RESULTS_DIR, "results_compress.csv")),
        ("order", os.path.join(RESULTS_DIR, "results_order.csv")),
        ("rerank_order", os.path.join(RESULTS_DIR, "results_rerank_order.csv")),
        ("rerank_ml_n20", os.path.join(RESULTS_DIR, "results_rerank_ml_n20.csv")),
    ]
    for label, csv_path in notebook_csvs:
        if os.path.exists(csv_path):
            df_nb = pd.read_csv(csv_path)
            all_dfs.append(df_nb)
            print(f"  ✓ Notebook CSV lido: {csv_path} ({len(df_nb)} linhas)")

    # 2. Procura respostas externas em results/external/*.json e respostas-*.json na raiz
    ext_files = sorted(
        glob.glob(os.path.join(EXTERNAL_DIR, "*.json"))
        + glob.glob("respostas-*.json")
    )
    ext_answer_files = [
        p for p in ext_files
        if not os.path.basename(p).endswith("_judge.json")
        and os.path.basename(p) != "para_auditar_judge.json"
    ]

    ext_dfs = []
    for ans_path in ext_answer_files:
        base = os.path.splitext(os.path.basename(ans_path))[0]
        judge_path = os.path.join(EXTERNAL_DIR, f"{base}_judge.json")
        df_ext = evaluate_external_model(base, ans_path, questions, judge_path=judge_path)
        out_csv = os.path.join(RESULTS_DIR, f"results_ext_{base}.csv")
        df_ext.to_csv(out_csv, index=False)
        all_dfs.append(df_ext)
        ext_dfs.append(df_ext)
        print(
            f"  ✓ Externo [{base}]: acerto estrito = {df_ext['correct_strict'].mean():.2f} | "
            f"acerto c/ recusa flexível = {df_ext['correct_lenient_refusal'].mean():.2f} | "
            f"salvo em {out_csv}"
        )

    if ext_dfs:
        export_candidates_for_llm_judge(
            pd.concat(ext_dfs, ignore_index=True),
            questions,
            os.path.join(EXTERNAL_DIR, "para_auditar_judge.json"),
        )
    else:
        print(
            f"\nNenhum arquivo JSON encontrado em '{EXTERNAL_DIR}/'.\n"
            f"Quando coletar as respostas no NotebookLM / Claude / Gemini, salve-as como:\n"
            f"  - {os.path.join(EXTERNAL_DIR, 'notebooklm.json')}\n"
            f"  - {os.path.join(EXTERNAL_DIR, 'claude.json')}\n"
            f"  - {os.path.join(EXTERNAL_DIR, 'gemini.json')}"
        )

    if all_dfs:
        summary = build_comparative_summary(all_dfs)
        summary_path = os.path.join(RESULTS_DIR, "summary_comparativo.csv")
        summary.to_csv(summary_path)
        print("\n=== TABELA COMPARATIVA ===")
        print(summary.to_string())
        print(f"\nTabela salva em: {summary_path}")
        plot_comparative_scoreboard(
            summary,
            len(questions),
            os.path.join(RESULTS_DIR, "scoreboard_comparativo.png"),
        )


if __name__ == "__main__":
    main()


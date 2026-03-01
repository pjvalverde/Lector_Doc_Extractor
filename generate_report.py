"""
generate_report.py — Generate a consolidated Markdown report from LangExtract results.

Takes the extraction results from all 5 tasks and produces a readable
Markdown report organized by section.
"""

import json
import os
from pathlib import Path


def _load_jsonl(filepath: str) -> list[dict]:
    """Load extractions from a JSONL file."""
    results = []
    if not os.path.exists(filepath):
        return results
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                results.append(json.loads(line))
    return results


def _extract_entities(data: list[dict]) -> list[dict]:
    """Pull out individual extractions from the JSONL data."""
    entities = []
    for doc in data:
        for ext in doc.get("extractions", []):
            if ext and ext.get("extraction_text"):
                entities.append(ext)
    return entities


def _attrs(entity: dict) -> dict:
    """Safely get attributes dict, handling None values."""
    return entity.get("attributes", {}) or {}


def generate_report(book_name: str, results_dir: str, output_path: str) -> str:
    """
    Generate a Markdown report from all extraction results for a book.

    Args:
        book_name: Stem name of the book (without extension).
        results_dir: Directory containing the JSONL result files.
        output_path: Path to write the Markdown report.

    Returns:
        The path of the generated report.
    """
    lines = []
    lines.append(f"# 📚 Análisis: {book_name}\n")
    lines.append(f"*Reporte generado automáticamente con LangExtract + Gemini*\n")
    lines.append("---\n")

    # ── SECTION 4: Central Message (first so reader gets the big picture) ──
    _add_central_message(lines, book_name, results_dir)

    # ── SECTION 1: Main Ideas ──
    _add_main_ideas(lines, book_name, results_dir)

    # ── SECTION 2: Social Media ──
    _add_social_media(lines, book_name, results_dir)

    # ── SECTION 3: Teaching Material ──
    _add_teaching_material(lines, book_name, results_dir)

    # ── SECTION 5: Knowledge Base ──
    _add_knowledge_base(lines, book_name, results_dir)

    report_content = "\n".join(lines)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return output_path


def _add_central_message(lines: list, book_name: str, results_dir: str):
    """Add central message section."""
    filepath = os.path.join(results_dir, f"{book_name}_central_message.jsonl")
    entities = _extract_entities(_load_jsonl(filepath))
    if not entities:
        return

    lines.append("## 🎯 Mensaje Central\n")

    theses = [e for e in entities if e.get("extraction_class") == "thesis"]
    core_msgs = [e for e in entities if e.get("extraction_class") == "core_message"]
    evidence = [e for e in entities if e.get("extraction_class") == "supporting_evidence"]

    for t in theses:
        attrs = _attrs(t)
        lines.append(f"### Tesis principal")
        lines.append(f"> *\"{t.get('extraction_text', '')}\"*\n")
        if attrs.get("summary"):
            lines.append(f"**Resumen:** {attrs['summary']}\n")

    for cm in core_msgs:
        attrs = _attrs(cm)
        lines.append(f"**Mensaje clave:** *\"{cm.get('extraction_text', '')}\"*")
        if attrs.get("centrality"):
            lines.append(f"  - {attrs['centrality']}\n")

    if evidence:
        lines.append("\n### Evidencia de soporte\n")
        for ev in evidence:
            attrs = _attrs(ev)
            strength = attrs.get("strength", "")
            lines.append(f"- *\"{ev.get('extraction_text', '')}\"*")
            if strength:
                lines.append(f"  - Fuerza: **{strength}**")
            if attrs.get("type"):
                lines.append(f"  - Tipo: {attrs['type']}")

    lines.append("\n---\n")


def _add_main_ideas(lines: list, book_name: str, results_dir: str):
    """Add main ideas section."""
    filepath = os.path.join(results_dir, f"{book_name}_main_ideas.jsonl")
    entities = _extract_entities(_load_jsonl(filepath))
    if not entities:
        return

    lines.append("## 💡 Ideas Principales\n")

    ideas = [e for e in entities if e.get("extraction_class") == "main_idea"]
    arguments = [e for e in entities if e.get("extraction_class") == "argument"]
    conclusions = [e for e in entities if e.get("extraction_class") == "conclusion"]

    if ideas:
        lines.append("### Ideas clave\n")
        for i, idea in enumerate(ideas, 1):
            attrs = _attrs(idea)
            importance = attrs.get("importance", "")
            imp_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(importance, "⚪")
            lines.append(f"{i}. {imp_icon} *\"{idea.get('extraction_text', '')}\"*")
            if attrs.get("summary"):
                lines.append(f"   - {attrs['summary']}")
        lines.append("")

    if arguments:
        lines.append("### Argumentos principales\n")
        for arg in arguments:
            attrs = _attrs(arg)
            lines.append(f"- *\"{arg.get('extraction_text', '')}\"*")
            if attrs.get("summary"):
                lines.append(f"  - {attrs['summary']}")
        lines.append("")

    if conclusions:
        lines.append("### Conclusiones\n")
        for con in conclusions:
            attrs = _attrs(con)
            lines.append(f"> *\"{con.get('extraction_text', '')}\"*")
            if attrs.get("summary"):
                lines.append(f"> — {attrs['summary']}")
        lines.append("")

    lines.append("---\n")


def _add_social_media(lines: list, book_name: str, results_dir: str):
    """Add social media section."""
    filepath = os.path.join(results_dir, f"{book_name}_social_media.jsonl")
    entities = _extract_entities(_load_jsonl(filepath))
    if not entities:
        return

    lines.append("## 📱 Contenido para Redes Sociales\n")

    quotes = [e for e in entities if e.get("extraction_class") == "quote"]
    insights = [e for e in entities if e.get("extraction_class") == "insight"]
    hooks = [e for e in entities if e.get("extraction_class") == "hook"]

    if quotes:
        lines.append("### 🐦 Posts para X (Twitter)\n")
        for i, q in enumerate(quotes, 1):
            attrs = _attrs(q)
            lines.append(f"**Post {i}:**")
            if attrs.get("tweet"):
                lines.append(f"```\n{attrs['tweet']}\n```")
            lines.append(f"*Fuente original:* \"{q.get('extraction_text', '')}\"\n")

        lines.append("### 📸 Posts para Instagram\n")
        for i, q in enumerate(quotes, 1):
            attrs = _attrs(q)
            if attrs.get("instagram_caption"):
                lines.append(f"**Post {i}:**")
                lines.append(f"```\n{attrs['instagram_caption']}\n```\n")

    if insights:
        lines.append("### 💎 Insights clave\n")
        for ins in insights:
            attrs = _attrs(ins)
            lines.append(f"- *\"{ins.get('extraction_text', '')}\"*")
            if attrs.get("takeaway"):
                lines.append(f"  - **Takeaway:** {attrs['takeaway']}")
            if attrs.get("hashtags"):
                lines.append(f"  - **Hashtags:** {attrs['hashtags']}")
        lines.append("")

    if hooks:
        lines.append("### 🪝 Hooks de atención\n")
        for h in hooks:
            attrs = _attrs(h)
            lines.append(f"- *\"{h.get('extraction_text', '')}\"*")
            if attrs.get("attention_reason"):
                lines.append(f"  - {attrs['attention_reason']}")
            if attrs.get("platform"):
                lines.append(f"  - Plataforma: {attrs['platform']}")
        lines.append("")

    lines.append("---\n")


def _add_teaching_material(lines: list, book_name: str, results_dir: str):
    """Add teaching material section."""
    filepath = os.path.join(results_dir, f"{book_name}_teaching_material.jsonl")
    entities = _extract_entities(_load_jsonl(filepath))
    if not entities:
        return

    lines.append("## 🎓 Material para Clases\n")

    concepts = [e for e in entities if e.get("extraction_class") == "concept"]
    definitions = [e for e in entities if e.get("extraction_class") == "definition"]
    examples = [e for e in entities if e.get("extraction_class") == "example"]
    questions = [e for e in entities if e.get("extraction_class") == "discussion_question"]

    if concepts:
        lines.append("### Conceptos clave\n")
        lines.append("| Concepto | Explicación | Nivel |")
        lines.append("|----------|-------------|-------|")
        for c in concepts:
            attrs = _attrs(c)
            text = c.get("extraction_text", "").replace("\n", " ")[:80]
            explanation = attrs.get("explanation", "").replace("\n", " ")
            difficulty = attrs.get("difficulty", "")
            lines.append(f"| {text} | {explanation} | {difficulty} |")
        lines.append("")

    if definitions:
        lines.append("### Definiciones\n")
        for d in definitions:
            attrs = _attrs(d)
            term = attrs.get("term", "Término")
            lines.append(f"- **{term}:** *\"{d.get('extraction_text', '')}\"*")
            if attrs.get("explanation"):
                lines.append(f"  - {attrs['explanation']}")
        lines.append("")

    if examples:
        lines.append("### Ejemplos ilustrativos\n")
        for ex in examples:
            attrs = _attrs(ex)
            lines.append(f"- *\"{ex.get('extraction_text', '')}\"*")
            if attrs.get("illustrates"):
                lines.append(f"  - Ilustra: {attrs['illustrates']}")
        lines.append("")

    if questions:
        lines.append("### 🤔 Preguntas de discusión\n")
        for i, q in enumerate(questions, 1):
            attrs = _attrs(q)
            question = attrs.get("suggested_question", q.get("extraction_text", ""))
            lines.append(f"{i}. **{question}**")
            if attrs.get("learning_outcome"):
                lines.append(f"   - *Objetivo de aprendizaje:* {attrs['learning_outcome']}")
            if attrs.get("difficulty"):
                lines.append(f"   - *Nivel:* {attrs['difficulty']}")
        lines.append("")

    lines.append("---\n")


def _add_knowledge_base(lines: list, book_name: str, results_dir: str):
    """Add knowledge base section."""
    filepath = os.path.join(results_dir, f"{book_name}_knowledge_base.jsonl")
    entities = _extract_entities(_load_jsonl(filepath))
    if not entities:
        return

    lines.append("## 🤖 Base de Conocimiento (Bot Profesor)\n")

    facts = [e for e in entities if e.get("extraction_class") == "fact"]
    explanations = [e for e in entities if e.get("extraction_class") == "concept_explanation"]
    qa_pairs = [e for e in entities if e.get("extraction_class") == "qa_pair"]

    if facts:
        lines.append("### Hechos verificables\n")
        for fact in facts:
            attrs = _attrs(fact)
            fact_type = attrs.get("type", "dato")
            lines.append(f"- 📌 *\"{fact.get('extraction_text', '')}\"*")
            if attrs.get("topic"):
                lines.append(f"  - Tema: {attrs['topic']}")
            lines.append(f"  - Tipo: {fact_type}")
        lines.append("")

    if explanations:
        lines.append("### Explicaciones de conceptos\n")
        for exp in explanations:
            attrs = _attrs(exp)
            concept = attrs.get("concept", "Concepto")
            lines.append(f"#### {concept}")
            lines.append(f"*\"{exp.get('extraction_text', '')}\"*\n")
            if attrs.get("explanation"):
                lines.append(f"**Explicación:** {attrs['explanation']}\n")
            if attrs.get("related_concepts"):
                lines.append(f"**Conceptos relacionados:** {attrs['related_concepts']}\n")

    if qa_pairs:
        lines.append("### ❓ Preguntas y Respuestas\n")
        for i, qa in enumerate(qa_pairs, 1):
            attrs = _attrs(qa)
            question = attrs.get("question", "")
            answer = attrs.get("answer", qa.get("extraction_text", ""))
            lines.append(f"**P{i}: {question}**\n")
            lines.append(f"**R:** {answer}\n")
            if attrs.get("critical_note"):
                lines.append(f"> ⚠️ **Nota crítica:** {attrs['critical_note']}\n")

    lines.append("---\n")


# ── Export Q&A as JSON for chatbot ingestion ──

def export_qa_json(book_name: str, results_dir: str, output_path: str) -> str:
    """Export knowledge base as a JSON file suitable for chatbot training."""
    filepath = os.path.join(results_dir, f"{book_name}_knowledge_base.jsonl")
    entities = _extract_entities(_load_jsonl(filepath))

    qa_data = {
        "book": book_name,
        "facts": [],
        "concepts": [],
        "qa_pairs": [],
        "teaching_material": _extract_entities(_load_jsonl(os.path.join(results_dir, f"{book_name}_teaching_material.jsonl"))),
        "main_ideas": _extract_entities(_load_jsonl(os.path.join(results_dir, f"{book_name}_main_ideas.jsonl"))),
        "central_message": _extract_entities(_load_jsonl(os.path.join(results_dir, f"{book_name}_central_message.jsonl"))),
        "social_media": _extract_entities(_load_jsonl(os.path.join(results_dir, f"{book_name}_social_media.jsonl"))),
    }

    for e in entities:
        attrs = _attrs(e)
        cls = e.get("extraction_class", "")
        text = e.get("extraction_text", "")

        if cls == "fact":
            qa_data["facts"].append({
                "text": text,
                "topic": attrs.get("topic", ""),
                "type": attrs.get("type", ""),
            })
        elif cls == "concept_explanation":
            qa_data["concepts"].append({
                "concept": attrs.get("concept", ""),
                "source_text": text,
                "explanation": attrs.get("explanation", ""),
                "related": attrs.get("related_concepts", ""),
            })
        elif cls == "qa_pair":
            qa_data["qa_pairs"].append({
                "question": attrs.get("question", ""),
                "answer": attrs.get("answer", text),
                "critical_note": attrs.get("critical_note", ""),
                "source_text": text,
            })

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(qa_data, f, ensure_ascii=False, indent=2)

    return output_path


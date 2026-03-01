"""
api/main.py — FastAPI backend for the Lector Doc Extractor Dashboard.

Pipeline (v2):
  1. Read / Transcribe document text
  2. Extract main_ideas with LangExtract (Gemini 2.5 Flash) — Aha! moments + parent-child
  3. Generate social_media posts from ideas   (Gemini direct call — max 10 posts)
  4. Generate teaching_material lecture notes (Gemini direct call — title/subtitle/Aha!/key point)

Endpoints:
  POST /api/jobs           — Upload file + select tasks → returns job_id
  GET  /api/jobs/{job_id}  — Poll job status + results when done
  GET  /api/jobs/{job_id}/download/markdown    — Markdown report
  GET  /api/jobs/{job_id}/download/json        — Extraction JSON
  GET  /api/jobs/{job_id}/download/transcript  — Scientific LaTeX transcript

Run with:
  uvicorn api.main:app --reload --port 8000
  (from the project root: D:/Apps-2026/ExtractBooks)
"""

import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# ── Project root on Python path ───────────────────────────────────────────────
ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv
load_dotenv(ROOT_DIR / ".env")

# ── Directories ───────────────────────────────────────────────────────────────
UPLOADS_DIR = ROOT_DIR / "uploads"
JOBS_DIR    = ROOT_DIR / "jobs"
RESULTS_DIR = ROOT_DIR / "results"

for d in (UPLOADS_DIR, JOBS_DIR, RESULTS_DIR):
    d.mkdir(exist_ok=True)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="Lector Doc Extractor API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Valid user-selectable tasks (modules 1 and 5 removed)
VALID_TASKS = {"main_ideas", "social_media", "teaching_material"}

# Gemini models
VISION_MODEL  = "gemini-2.0-flash"   # used for scientific PDF transcription + social/teaching generation
EXTRACT_MODEL = "gemini-2.5-flash"   # used for LangExtract (main_ideas)
BATCH_SIZE    = 15     # pages per vision batch
DPI_SCALE     = 1.5   # render quality (1.0 = 72dpi, 1.5 = 108dpi, 2.0 = 144dpi)


# ── Job state helpers ─────────────────────────────────────────────────────────

def save_job(job_id: str, state: dict) -> None:
    job_file = JOBS_DIR / f"{job_id}.json"
    with open(job_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def load_job(job_id: str) -> Optional[dict]:
    job_file = JOBS_DIR / f"{job_id}.json"
    if not job_file.exists():
        return None
    with open(job_file, encoding="utf-8") as f:
        return json.load(f)


# ── Results loaders ───────────────────────────────────────────────────────────

def _load_jsonl(filepath: str) -> list[dict]:
    results: list[dict] = []
    if not os.path.exists(filepath):
        return results
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                results.append(json.loads(line))
    return results


def _extract_entities(data: list[dict]) -> list[dict]:
    entities: list[dict] = []
    for doc in data:
        for ext in doc.get("extractions", []):
            if ext and ext.get("extraction_text"):
                entities.append(ext)
    return entities


def load_extraction_results(book_stem: str, output_dir: str) -> dict:
    """
    Load extraction results for the 3 active tasks.
    - main_ideas: from JSONL (LangExtract output)
    - social_media: from JSON (Gemini generated), fallback to JSONL
    - teaching_material: from JSON (Gemini generated), fallback to JSONL
    """
    results: dict[str, list] = {}

    # main_ideas — always JSONL from LangExtract
    jsonl_path = os.path.join(output_dir, f"{book_stem}_main_ideas.jsonl")
    results["main_ideas"] = _extract_entities(_load_jsonl(jsonl_path))

    # social_media — JSON first (new generated format), fallback to JSONL
    social_json = os.path.join(output_dir, f"{book_stem}_social_media.json")
    social_jsonl = os.path.join(output_dir, f"{book_stem}_social_media.jsonl")
    if os.path.exists(social_json):
        with open(social_json, encoding="utf-8") as f:
            results["social_media"] = json.load(f)
    else:
        results["social_media"] = _extract_entities(_load_jsonl(social_jsonl))

    # teaching_material — JSON first (new generated format), fallback to JSONL
    teaching_json = os.path.join(output_dir, f"{book_stem}_teaching_material.json")
    teaching_jsonl = os.path.join(output_dir, f"{book_stem}_teaching_material.jsonl")
    if os.path.exists(teaching_json):
        with open(teaching_json, encoding="utf-8") as f:
            results["teaching_material"] = json.load(f)
    else:
        results["teaching_material"] = _extract_entities(_load_jsonl(teaching_jsonl))

    return results


# ── Scientific Mode: PDF pages → Gemini Vision → LaTeX text ──────────────────

def transcribe_pdf_scientific(filepath: str, job_id: str, base_state: dict) -> str:
    """
    Render each PDF page as an image and send to Gemini Vision for transcription.
    Returns clean Markdown text with LaTeX formulas and matrix notation.
    """
    try:
        import fitz  # PyMuPDF
        from google import genai
    except ImportError as e:
        raise RuntimeError(
            f"Dependencia faltante para Modo Científico: {e}. "
            f"Instala: pip install pymupdf google-genai"
        )

    client = genai.Client()
    doc    = fitz.open(filepath)
    total  = len(doc)
    chunks: list[str] = []

    TRANSCRIPTION_PROMPT = """\
You are a scientific textbook transcription assistant.
Transcribe the content of these pages EXACTLY as it appears.

Rules:
- Preserve all text, headings, and paragraphs faithfully.
- Convert ALL mathematical expressions to LaTeX:
    Inline: $E = mc^2$  |  Block: $$\\int_0^\\infty e^{{-x^2}}\\,dx = \\frac{{\\sqrt{{\\pi}}}}{{2}}$$
- Convert matrices to LaTeX block form:
    $$\\begin{{pmatrix}} a_{{11}} & a_{{12}} \\\\ a_{{21}} & a_{{22}} \\end{{pmatrix}}$$
- For game theory payoff matrices use LaTeX tabular or pmatrix.
- Describe figures/graphs as: [FIGURA: brief description]
- Mark each page boundary as: --- Página N ---
- Do NOT add commentary or summaries. Just transcribe.

Transcribe pages {start} to {end} of {total}:
"""

    mat = fitz.Matrix(DPI_SCALE, DPI_SCALE)

    for batch_start in range(0, total, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, total)
        pct       = int((batch_start / total) * 100)

        save_job(job_id, {
            **base_state,
            "progress": f"🔬 Transcribiendo páginas {batch_start + 1}–{batch_end} de {total} ({pct}%)",
            "phase":    "transcription",
            "pct":      pct,
        })

        parts = []
        for page_num in range(batch_start, batch_end):
            pix      = doc[page_num].get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            parts.append(
                genai.types.Part.from_bytes(data=img_data, mime_type="image/png")
            )

        prompt_text = TRANSCRIPTION_PROMPT.format(
            start=batch_start + 1, end=batch_end, total=total
        )
        parts.append(genai.types.Part.from_text(prompt_text))

        for attempt in range(1, 4):
            try:
                response = client.models.generate_content(
                    model=VISION_MODEL,
                    contents=parts,
                )
                chunks.append(response.text)
                break
            except Exception as e:
                err = str(e)
                if attempt < 3 and any(k in err.lower() for k in ["rate", "quota", "429", "resource"]):
                    time.sleep(30 * attempt)
                else:
                    chunks.append(f"\n[TRANSCRIPCIÓN FALLIDA págs {batch_start+1}–{batch_end}: {err}]\n")
                    break

        time.sleep(2)

    doc.close()
    return "\n\n".join(chunks)


# ── Gemini generation helpers (social media + teaching from main_ideas) ───────

def _parse_json_response(text: str) -> list:
    """Robustly parse a JSON array from a Gemini text response."""
    text = text.strip()
    # Strip markdown code fences
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            stripped = part.strip()
            if stripped.startswith("json"):
                stripped = stripped[4:].strip()
            if stripped.startswith("["):
                text = stripped
                break
    # Extract the first [...] block
    start = text.find("[")
    end   = text.rfind("]")
    if start >= 0 and end > start:
        text = text[start : end + 1]
    return json.loads(text)


def _ideas_to_text(entities: list[dict], max_chars: int = 8000) -> str:
    """Convert main_ideas entities to a readable text summary for Gemini prompts."""
    lines = []
    for e in entities:
        text = e.get("extraction_text", "").strip()
        if not text:
            continue
        attrs       = e.get("attributes") or {}
        aha         = attrs.get("aha_moment", "")
        framework   = attrs.get("framework", "")
        cls         = e.get("extraction_class", "")
        label       = {"main_idea": "💡 IDEA", "argument": "  → Argumento", "conclusion": "  ✓ Conclusión"}.get(cls, "•")
        line = f"{label}: {text}"
        if aha:
            line += f"\n    Aha!: {aha}"
        if framework:
            line += f"\n    Framework: {framework}"
        lines.append(line)
    result = "\n".join(lines)
    return result[:max_chars]


def _generate_social_from_ideas(ideas_entities: list[dict], n_posts: int = 10) -> list[dict]:
    """
    Generate up to n_posts social media posts from extracted main ideas using Gemini.
    Returns a list of entity dicts with extraction_class='post'.
    """
    try:
        from google import genai
    except ImportError:
        return [{"extraction_class": "post", "extraction_text": "Error: google-genai no instalado", "attributes": {}}]

    ideas_text = _ideas_to_text(ideas_entities)
    if not ideas_text:
        return []

    prompt = f"""You are a social media expert specializing in educational content.
Based on the following key ideas extracted from a book, create {n_posts} engaging social media posts.

KEY IDEAS FROM THE BOOK:
{ideas_text}

Generate exactly {n_posts} posts. Return a JSON array where each item has:
- "tweet": a concise X/Twitter post (max 280 characters), punchy and direct, with relevant emojis
- "instagram_caption": a richer Instagram caption with line breaks, storytelling, and 4-6 hashtags
- "hashtags": 4-6 relevant hashtags (e.g. "#leadership #growth #mindset")
- "idea_source": a brief phrase identifying which main idea this post is based on

Rules:
- Each post must be based on a SPECIFIC idea from the list above, not a generic restatement
- Tweets must be under 280 characters (count carefully)
- Instagram captions should be 3-5 sentences, engaging and educational
- Vary the tone: some informative, some provocative, some inspirational

Return ONLY the raw JSON array. No markdown code fences, no explanation, no preamble."""

    try:
        client   = genai.Client()
        response = client.models.generate_content(model=VISION_MODEL, contents=prompt)
        posts    = _parse_json_response(response.text)

        entities = []
        for post in posts[:n_posts]:
            tweet = (post.get("tweet") or "").strip()
            if not tweet:
                continue
            entities.append({
                "extraction_class": "post",
                "extraction_text":  tweet,
                "attributes": {
                    "instagram_caption": (post.get("instagram_caption") or "").strip(),
                    "hashtags":          (post.get("hashtags") or "").strip(),
                    "idea_source":       (post.get("idea_source") or "").strip(),
                },
            })
        return entities
    except Exception as e:
        return [{
            "extraction_class": "post",
            "extraction_text":  f"Error al generar posts: {e}",
            "attributes":       {},
        }]


def _generate_teaching_from_ideas(ideas_entities: list[dict]) -> list[dict]:
    """
    Generate lecture notes from extracted main ideas using Gemini.
    Returns a list of entity dicts with extraction_class='lecture_note'.
    """
    try:
        from google import genai
    except ImportError:
        return [{"extraction_class": "lecture_note", "extraction_text": "Error: google-genai no instalado", "attributes": {}}]

    ideas_text = _ideas_to_text(ideas_entities)
    if not ideas_text:
        return []

    # Estimate number of lecture notes from number of main ideas
    n_ideas = sum(1 for e in ideas_entities if e.get("extraction_class") == "main_idea")
    n_notes = max(3, min(n_ideas, 10))

    prompt = f"""You are a world-class professor and educational designer.
Based on the following key ideas extracted from a book, create structured lecture notes
that you would use to teach this material to university students.

KEY IDEAS FROM THE BOOK:
{ideas_text}

Create {n_notes} lecture note sections. Return a JSON array where each item has:
- "title": a compelling, specific lecture title for this section (not generic)
- "subtitle": a brief module or subtopic description (1 short line)
- "aha_moment": the key 'Aha!' insight students should walk away with
                (what will make them say 'I never thought of it that way!')
- "key_author_point": the most important thing the author conveys about this idea
                      (quote or close paraphrase from the ideas above)
- "example": a specific example, analogy, or framework to make this concrete
             (use examples from the book if available; otherwise create an apt analogy)

Rules:
- Each lecture note should cover a DISTINCT main idea
- Be specific and educational — avoid vague or generic statements
- Write as a professor who truly understands this material
- The Aha! moment should be genuinely surprising or counterintuitive

Return ONLY the raw JSON array. No markdown code fences, no explanation, no preamble."""

    try:
        client   = genai.Client()
        response = client.models.generate_content(model=VISION_MODEL, contents=prompt)
        notes    = _parse_json_response(response.text)

        entities = []
        for note in notes:
            key_point = (note.get("key_author_point") or note.get("title") or "").strip()
            if not key_point:
                continue
            entities.append({
                "extraction_class": "lecture_note",
                "extraction_text":  key_point,
                "attributes": {
                    "title":       (note.get("title") or "").strip(),
                    "subtitle":    (note.get("subtitle") or "").strip(),
                    "aha_moment":  (note.get("aha_moment") or "").strip(),
                    "example":     (note.get("example") or "").strip(),
                },
            })
        return entities
    except Exception as e:
        return [{
            "extraction_class": "lecture_note",
            "extraction_text":  f"Error al generar lecture notes: {e}",
            "attributes":       {},
        }]


# ── Background extraction ─────────────────────────────────────────────────────

def run_extraction(
    job_id: str,
    file_path: str,
    tasks: list[str],
    scientific_mode: bool = False,
) -> None:
    """
    Run the full extraction pipeline as a background task.

    Pipeline:
      1. Read or transcribe text (scientific mode uses Gemini Vision for LaTeX)
      2. Extract main_ideas with LangExtract (always, feeds steps 3 & 4)
      3. Generate social_media posts from ideas (if selected)
      4. Generate teaching_material lecture notes from ideas (if selected)
      5. Generate Markdown report + JSON export
    """
    import langextract as lx
    from book_reader import read_book
    from extraction_tasks import TASK_MAIN_IDEAS
    from generate_report import export_ideas_json, generate_report

    MAX_WORKERS       = 10
    EXTRACTION_PASSES = 2
    DELAY_BETWEEN     = 5
    MAX_RETRIES       = 3
    RETRY_BASE_DELAY  = 30

    try:
        book_stem  = Path(file_path).stem
        output_dir = str(RESULTS_DIR / job_id)
        os.makedirs(output_dir, exist_ok=True)
        fname = Path(file_path).name

        base_state = {
            "status":          "processing",
            "file":            fname,
            "book_stem":       book_stem,
            "tasks":           tasks,
            "scientific_mode": scientific_mode,
        }

        save_job(job_id, {**base_state, "progress": "Iniciando..."})

        # ── 1. Read / Transcribe ──────────────────────────────────────────────
        if scientific_mode and file_path.lower().endswith(".pdf"):
            save_job(job_id, {
                **base_state,
                "progress": "🔬 Iniciando transcripción científica con Gemini Vision...",
                "phase":    "transcription",
                "pct":      0,
            })
            text = transcribe_pdf_scientific(file_path, job_id, base_state)
            transcript_path = os.path.join(output_dir, f"{book_stem}_transcript.md")
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(text)
        else:
            save_job(job_id, {**base_state, "progress": "Leyendo documento..."})
            text = read_book(file_path)

        if len(text.strip()) < 100:
            save_job(job_id, {"status": "failed", "error": "El archivo tiene muy poco texto extraíble."})
            return

        # ── 2. Extract main_ideas with LangExtract ────────────────────────────
        # main_ideas always runs — it feeds social_media and teaching_material generation
        total_steps = len(tasks)
        step        = tasks.index("main_ideas") + 1 if "main_ideas" in tasks else 1

        save_job(job_id, {
            **base_state,
            "progress": "💡 Extrayendo Ideas Principales con Gemini AI (Aha! moments)...",
            "phase":    "extraction",
            "step":     step,
            "total":    total_steps,
        })

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                result = lx.extract(
                    text_or_documents=text,
                    prompt_description=TASK_MAIN_IDEAS.prompt,
                    examples=TASK_MAIN_IDEAS.examples,
                    model_id=EXTRACT_MODEL,
                    max_workers=MAX_WORKERS,
                    extraction_passes=EXTRACTION_PASSES,
                )
                lx.io.save_annotated_documents(
                    [result],
                    output_name=f"{book_stem}_main_ideas.jsonl",
                    output_dir=output_dir,
                )
                break
            except Exception as e:
                err = str(e)
                if attempt < MAX_RETRIES and any(
                    k in err.lower() for k in ["retry", "rate", "quota", "429", "resource"]
                ):
                    time.sleep(RETRY_BASE_DELAY * attempt)
                else:
                    break

        # Load entities for downstream generation
        jsonl_path         = os.path.join(output_dir, f"{book_stem}_main_ideas.jsonl")
        main_ideas_entities = _extract_entities(_load_jsonl(jsonl_path))

        time.sleep(DELAY_BETWEEN)

        # ── 3. Generate social_media posts from ideas ─────────────────────────
        if "social_media" in tasks:
            step = tasks.index("social_media") + 1
            save_job(job_id, {
                **base_state,
                "progress": "📱 Generando posts para redes sociales desde las ideas...",
                "phase":    "extraction",
                "step":     step,
                "total":    total_steps,
            })
            social_entities = _generate_social_from_ideas(main_ideas_entities, n_posts=10)
            social_path     = os.path.join(output_dir, f"{book_stem}_social_media.json")
            with open(social_path, "w", encoding="utf-8") as f:
                json.dump(social_entities, f, ensure_ascii=False, indent=2)
            time.sleep(2)

        # ── 4. Generate teaching_material lecture notes from ideas ────────────
        if "teaching_material" in tasks:
            step = tasks.index("teaching_material") + 1
            save_job(job_id, {
                **base_state,
                "progress": "🎓 Generando lecture notes desde las ideas principales...",
                "phase":    "extraction",
                "step":     step,
                "total":    total_steps,
            })
            teaching_entities = _generate_teaching_from_ideas(main_ideas_entities)
            teaching_path     = os.path.join(output_dir, f"{book_stem}_teaching_material.json")
            with open(teaching_path, "w", encoding="utf-8") as f:
                json.dump(teaching_entities, f, ensure_ascii=False, indent=2)

        # ── 5. Generate reports ───────────────────────────────────────────────
        report_path = os.path.join(output_dir, f"{book_stem}_REPORTE.md")
        generate_report(book_stem, output_dir, report_path)

        qa_path = os.path.join(output_dir, f"{book_stem}_extraction.json")
        export_ideas_json(book_stem, output_dir, qa_path)

        # ── 6. Save final state ───────────────────────────────────────────────
        results = load_extraction_results(book_stem, output_dir)
        save_job(job_id, {
            "status":          "completed",
            "file":            fname,
            "book_stem":       book_stem,
            "output_dir":      output_dir,
            "tasks":           tasks,
            "scientific_mode": scientific_mode,
            "results":         results,
            "report_path":     report_path,
            "qa_path":         qa_path,
        })

    except Exception as e:
        save_job(job_id, {
            "status": "failed",
            "error":  str(e),
            "file":   Path(file_path).name if file_path else "unknown",
        })


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "Lector Doc Extractor API v2.0 running 🚀"}


@app.post("/api/jobs")
async def create_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    tasks: str = Form(default="main_ideas,social_media,teaching_material"),
    scientific_mode: bool = Form(default=False),
):
    """
    Upload a document and start extraction in the background.

    - tasks: comma-separated list. Valid: main_ideas, social_media, teaching_material
             (central_message and knowledge_base removed in v2)
    - scientific_mode: if True, uses Gemini Vision to transcribe formulas/matrices as LaTeX
    """
    # Validate file type
    allowed_exts = {".pdf", ".epub", ".txt"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Formato '{file_ext}' no soportado. Usa PDF, EPUB o TXT."
        )

    if scientific_mode and file_ext != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="El Modo Científico solo funciona con archivos PDF."
        )

    # Validate and normalise tasks
    task_list = [t.strip() for t in tasks.split(",") if t.strip()]
    invalid   = [t for t in task_list if t not in VALID_TASKS]
    if invalid:
        raise HTTPException(status_code=400, detail=f"Tareas inválidas: {invalid}")
    if not task_list:
        task_list = ["main_ideas", "social_media", "teaching_material"]

    # main_ideas must always run (social + teaching depend on it)
    if "main_ideas" not in task_list:
        task_list.insert(0, "main_ideas")

    # Save uploaded file
    job_id      = str(uuid.uuid4())
    upload_dir  = UPLOADS_DIR / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    upload_path = upload_dir / file.filename

    content = await file.read()
    with open(upload_path, "wb") as f:
        f.write(content)

    # Save initial state
    save_job(job_id, {
        "status":          "pending",
        "file":            file.filename,
        "tasks":           task_list,
        "scientific_mode": scientific_mode,
    })

    # Kick off extraction
    background_tasks.add_task(
        run_extraction, job_id, str(upload_path), task_list, scientific_mode
    )

    return {
        "job_id":          job_id,
        "status":          "pending",
        "file":            file.filename,
        "scientific_mode": scientific_mode,
    }


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    """Poll job status and get results when completed."""
    state = load_job(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    return state


@app.get("/api/jobs/{job_id}/download/markdown")
async def download_markdown(job_id: str):
    """Download the Markdown report."""
    state = load_job(job_id)
    if not state or state.get("status") != "completed":
        raise HTTPException(status_code=404, detail="Reporte no disponible aún")
    report_path = state.get("report_path", "")
    if not report_path or not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Archivo de reporte no encontrado")
    return FileResponse(
        report_path,
        media_type="text/markdown",
        filename=f"reporte_{state.get('book_stem', 'libro')}.md",
    )


@app.get("/api/jobs/{job_id}/download/json")
async def download_json(job_id: str):
    """Download the extraction JSON."""
    state = load_job(job_id)
    if not state or state.get("status") != "completed":
        raise HTTPException(status_code=404, detail="JSON no disponible aún")
    qa_path = state.get("qa_path", "")
    if not qa_path or not os.path.exists(qa_path):
        raise HTTPException(status_code=404, detail="Archivo JSON no encontrado")
    return FileResponse(
        qa_path,
        media_type="application/json",
        filename=f"extraction_{state.get('book_stem', 'libro')}.json",
    )


@app.get("/api/jobs/{job_id}/download/transcript")
async def download_transcript(job_id: str):
    """Download the scientific LaTeX transcription. Only available in scientific mode."""
    state = load_job(job_id)
    if not state or state.get("status") != "completed":
        raise HTTPException(status_code=404, detail="Transcripción no disponible aún")
    if not state.get("scientific_mode"):
        raise HTTPException(status_code=404, detail="Solo disponible en Modo Científico")
    book_stem       = state.get("book_stem", "libro")
    output_dir      = state.get("output_dir", "")
    transcript_path = os.path.join(output_dir, f"{book_stem}_transcript.md")
    if not os.path.exists(transcript_path):
        raise HTTPException(status_code=404, detail="Archivo de transcripción no encontrado")
    return FileResponse(
        transcript_path,
        media_type="text/markdown",
        filename=f"transcripcion_{book_stem}.md",
    )

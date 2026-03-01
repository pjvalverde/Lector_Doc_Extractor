"""
api/main.py — FastAPI backend for the Lector Doc Extractor Dashboard.

Endpoints:
  POST /api/jobs           — Upload file + select tasks → returns job_id
  GET  /api/jobs/{job_id}  — Poll job status + get results when done
  GET  /api/jobs/{job_id}/download/markdown — Download Markdown report
  GET  /api/jobs/{job_id}/download/json     — Download JSON knowledge base

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

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# ── Make sure the project root is on the Python path ──────────────────────────
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
app = FastAPI(title="Lector Doc Extractor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VALID_TASKS = {"main_ideas", "social_media", "teaching_material", "central_message", "knowledge_base"}


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


# ── Results loader ────────────────────────────────────────────────────────────

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
    task_names = ["main_ideas", "social_media", "teaching_material", "central_message", "knowledge_base"]
    results: dict[str, list] = {}
    for name in task_names:
        jsonl_path = os.path.join(output_dir, f"{book_stem}_{name}.jsonl")
        results[name] = _extract_entities(_load_jsonl(jsonl_path))
    return results


# ── Background extraction ─────────────────────────────────────────────────────

def run_extraction(job_id: str, file_path: str, tasks: list[str]) -> None:
    """Run the full extraction pipeline as a background task."""
    import langextract as lx
    from book_reader import read_book
    from extraction_tasks import TASKS
    from generate_report import export_qa_json, generate_report

    MODEL_ID         = "gemini-2.5-flash"
    MAX_WORKERS      = 10
    EXTRACTION_PASSES = 2
    DELAY_BETWEEN    = 5   # seconds between tasks
    MAX_RETRIES      = 3
    RETRY_BASE_DELAY = 30  # seconds

    try:
        book_stem  = Path(file_path).stem
        output_dir = str(RESULTS_DIR / job_id)
        os.makedirs(output_dir, exist_ok=True)

        save_job(job_id, {
            "status":    "processing",
            "progress":  "Leyendo documento...",
            "file":      Path(file_path).name,
            "book_stem": book_stem,
            "tasks":     tasks,
        })

        # 1. Read the book
        text = read_book(file_path)
        if len(text) < 100:
            save_job(job_id, {"status": "failed", "error": "El archivo tiene muy poco texto extraíble."})
            return

        # 2. Run each extraction task
        tasks_to_run = [t for t in TASKS if t.name in tasks] if tasks else TASKS

        for i, task in enumerate(tasks_to_run):
            save_job(job_id, {
                "status":    "processing",
                "progress":  f"Extrayendo: {task.description} ({i + 1}/{len(tasks_to_run)})",
                "file":      Path(file_path).name,
                "book_stem": book_stem,
                "tasks":     tasks,
                "step":      i + 1,
                "total":     len(tasks_to_run),
            })

            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    result = lx.extract(
                        text_or_documents=text,
                        prompt_description=task.prompt,
                        examples=task.examples,
                        model_id=MODEL_ID,
                        max_workers=MAX_WORKERS,
                        extraction_passes=EXTRACTION_PASSES,
                    )
                    lx.io.save_annotated_documents(
                        [result],
                        output_name=f"{book_stem}_{task.name}.jsonl",
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

            if i < len(tasks_to_run) - 1:
                time.sleep(DELAY_BETWEEN)

        # 3. Generate reports
        report_path = os.path.join(output_dir, f"{book_stem}_REPORTE.md")
        generate_report(book_stem, output_dir, report_path)

        qa_path = os.path.join(output_dir, f"{book_stem}_bot_qa.json")
        export_qa_json(book_stem, output_dir, qa_path)

        # 4. Load results and save final state
        results = load_extraction_results(book_stem, output_dir)
        save_job(job_id, {
            "status":      "completed",
            "file":        Path(file_path).name,
            "book_stem":   book_stem,
            "output_dir":  output_dir,
            "tasks":       tasks,
            "results":     results,
            "report_path": report_path,
            "qa_path":     qa_path,
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
    return {"status": "ok", "message": "Lector Doc Extractor API running 🚀"}


@app.post("/api/jobs")
async def create_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    tasks: str = "main_ideas,social_media,teaching_material,central_message,knowledge_base",
):
    """Upload a document and start extraction in the background."""
    # Validate file type
    allowed_exts = {".pdf", ".epub", ".txt"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Formato '{file_ext}' no soportado. Usa PDF, EPUB o TXT."
        )

    # Validate tasks
    task_list = [t.strip() for t in tasks.split(",") if t.strip()]
    invalid = [t for t in task_list if t not in VALID_TASKS]
    if invalid:
        raise HTTPException(status_code=400, detail=f"Tareas inválidas: {invalid}")
    if not task_list:
        task_list = list(VALID_TASKS)

    # Save uploaded file
    job_id = str(uuid.uuid4())
    upload_dir = UPLOADS_DIR / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    upload_path = upload_dir / file.filename

    content = await file.read()
    with open(upload_path, "wb") as f:
        f.write(content)

    # Save initial state
    save_job(job_id, {
        "status": "pending",
        "file":   file.filename,
        "tasks":  task_list,
    })

    # Kick off extraction
    background_tasks.add_task(run_extraction, job_id, str(upload_path), task_list)

    return {"job_id": job_id, "status": "pending", "file": file.filename}


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
    """Download the JSON knowledge base."""
    state = load_job(job_id)
    if not state or state.get("status") != "completed":
        raise HTTPException(status_code=404, detail="JSON no disponible aún")
    qa_path = state.get("qa_path", "")
    if not qa_path or not os.path.exists(qa_path):
        raise HTTPException(status_code=404, detail="Archivo JSON no encontrado")
    return FileResponse(
        qa_path,
        media_type="application/json",
        filename=f"knowledge_base_{state.get('book_stem', 'libro')}.json",
    )

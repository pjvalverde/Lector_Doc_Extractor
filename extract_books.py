"""
extract_books.py — Extract structured information from PDF/EPUB books
                   using LangExtract + Gemini.

Runs 5 extraction tasks per book:
  1. Main Ideas        2. Social Media Content    3. Teaching Material
  4. Central Message   5. Knowledge Base for Q&A Bot

Usage:
    python extract_books.py <file_or_folder> [--output_dir OUTPUT_DIR] [--tasks TASK1,TASK2]

Examples:
    python extract_books.py mybook.pdf
    python extract_books.py mybook.epub --output_dir results
    python extract_books.py ./books_folder
    python extract_books.py mybook.pdf --tasks main_ideas,social_media
"""

import argparse
import os
import sys
import time
from pathlib import Path

# Fix Windows cp1252 encoding for Unicode output
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import langextract as lx

from book_reader import list_books, read_book
from extraction_tasks import TASKS, get_task_by_name
from generate_report import export_qa_json, generate_report

MODEL_ID = "gemini-2.5-flash"
MAX_WORKERS = 10
EXTRACTION_PASSES = 2
DELAY_BETWEEN_TASKS = 5  # seconds between tasks
MAX_RETRIES = 3
RETRY_BASE_DELAY = 30  # seconds


def extract_task(text: str, task, output_dir: str, book_stem: str) -> bool:
    """Run a single extraction task on the book text with retry logic."""
    print(f"    ▸ [{task.name}] {task.description}")

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

            jsonl_name = f"{book_stem}_{task.name}.jsonl"
            lx.io.save_annotated_documents(
                [result], output_name=jsonl_name, output_dir=output_dir
            )

            n_extractions = len(result.extractions) if result.extractions else 0
            print(f"      ✔ {n_extractions} extractions → {jsonl_name}")
            return True

        except Exception as e:
            error_msg = str(e)
            if attempt < MAX_RETRIES and ("retry" in error_msg.lower() or "rate" in error_msg.lower() or "quota" in error_msg.lower() or "429" in error_msg or "resource" in error_msg.lower()):
                wait_time = RETRY_BASE_DELAY * attempt
                print(f"      ⏳ Rate limited (attempt {attempt}/{MAX_RETRIES}). Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"      ✘ Error: {e}")
                return False

    print(f"      ✘ Failed after {MAX_RETRIES} attempts")
    return False


def process_book(filepath: str, output_dir: str, task_names: list[str] | None = None):
    """Process a single book through all extraction tasks."""
    book_stem = Path(filepath).stem
    book_output_dir = os.path.join(output_dir, book_stem)
    os.makedirs(book_output_dir, exist_ok=True)

    print(f"\n{'═'*60}")
    print(f"  📚 {Path(filepath).name}")
    print(f"{'═'*60}")

    # 1. Read the book
    print(f"  [1/3] Leyendo archivo...")
    text = read_book(filepath)
    char_count = len(text)
    print(f"         {char_count:,} caracteres extraídos")

    if char_count < 100:
        print("  ⚠  Archivo con muy poco texto, saltando.")
        return

    # 2. Run extraction tasks
    tasks_to_run = TASKS
    if task_names:
        tasks_to_run = [t for t in TASKS if t.name in task_names]

    print(f"  [2/3] Ejecutando {len(tasks_to_run)} tareas de extracción...\n")
    success_count = 0
    for i, task in enumerate(tasks_to_run):
        ok = extract_task(text, task, book_output_dir, book_stem)
        if ok:
            success_count += 1
        # Delay between tasks to avoid rate limits
        if i < len(tasks_to_run) - 1:
            print(f"      ⏸ Pausa de {DELAY_BETWEEN_TASKS}s entre tareas (rate limit)...")
            time.sleep(DELAY_BETWEEN_TASKS)

    # 3. Generate reports
    print(f"\n  [3/3] Generando reportes...")

    # Markdown report
    report_path = os.path.join(book_output_dir, f"{book_stem}_REPORTE.md")
    generate_report(book_stem, book_output_dir, report_path)
    print(f"         📄 Reporte → {report_path}")

    # Q&A JSON for bot
    qa_path = os.path.join(book_output_dir, f"{book_stem}_bot_qa.json")
    export_qa_json(book_stem, book_output_dir, qa_path)
    print(f"         🤖 Bot Q&A → {qa_path}")

    # HTML visualizations
    for task in tasks_to_run:
        jsonl_path = os.path.join(book_output_dir, f"{book_stem}_{task.name}.jsonl")
        if os.path.exists(jsonl_path):
            try:
                html_content = lx.visualize(jsonl_path)
                html_path = os.path.join(
                    book_output_dir, f"{book_stem}_{task.name}_viz.html"
                )
                with open(html_path, "w", encoding="utf-8") as f:
                    if hasattr(html_content, "data"):
                        f.write(html_content.data)
                    else:
                        f.write(html_content)
            except Exception:
                pass  # Visualization is optional

    print(f"\n  ✔ Completado: {success_count}/{len(tasks_to_run)} tareas exitosas")
    print(f"  📂 Resultados en: {book_output_dir}/\n")


def main():
    parser = argparse.ArgumentParser(
        description="Extrae información estructurada de libros PDF/EPUB con LangExtract."
    )
    parser.add_argument(
        "input",
        help="Ruta a un libro (.pdf, .epub, .txt) o carpeta con libros.",
    )
    parser.add_argument(
        "--output_dir",
        default="results",
        help="Directorio de salida (default: ./results)",
    )
    parser.add_argument(
        "--tasks",
        default=None,
        help="Tareas a ejecutar, separadas por coma (default: todas). "
             "Opciones: main_ideas,social_media,teaching_material,central_message,knowledge_base",
    )
    args = parser.parse_args()

    # Parse tasks
    task_names = None
    if args.tasks:
        task_names = [t.strip() for t in args.tasks.split(",")]
        valid = {t.name for t in TASKS}
        invalid = [t for t in task_names if t not in valid]
        if invalid:
            print(f"Error: Tareas desconocidas: {invalid}")
            print(f"Tareas válidas: {sorted(valid)}")
            sys.exit(1)

    # Determine files
    input_path = args.input
    if os.path.isdir(input_path):
        files = list_books(input_path)
        if not files:
            print(f"No se encontraron archivos soportados en {input_path}")
            sys.exit(1)
        print(f"📚 {len(files)} libro(s) encontrado(s)")
    elif os.path.isfile(input_path):
        files = [input_path]
    else:
        print(f"Error: Ruta no encontrada: {input_path}")
        sys.exit(1)

    # Process each book
    for filepath in files:
        try:
            process_book(filepath, args.output_dir, task_names)
        except Exception as e:
            print(f"  ✘ Error procesando {Path(filepath).name}: {e}")
            continue

    print(f"\n{'═'*60}")
    print(f"  🎉 ¡Listo! Resultados en: {args.output_dir}/")
    print(f"{'═'*60}")


if __name__ == "__main__":
    main()

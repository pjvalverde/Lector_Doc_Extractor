"""
run_reports.py -- Regenerate the Markdown report and bot Q&A JSON
                  from existing JSONL extraction results.

No API key needed -- this only processes local data.

Usage:
    python run_reports.py
"""

import os
import sys
import json

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8')

from generate_report import generate_report, export_qa_json

BOOK_STEM = "Gustave Le Bon - The crowd_ a study of the popular mind-Dover Publications (2001)"
RESULTS_DIR = os.path.join("results", BOOK_STEM)


def main():
    if not os.path.isdir(RESULTS_DIR):
        print(f"Error: Results directory not found: {RESULTS_DIR}")
        return

    # List existing JSONL files
    jsonl_files = [f for f in os.listdir(RESULTS_DIR) if f.endswith(".jsonl")]
    print(f"[DIR] Found {len(jsonl_files)} JSONL files in {RESULTS_DIR}")
    for f in sorted(jsonl_files):
        size = os.path.getsize(os.path.join(RESULTS_DIR, f))
        print(f"   - {f}  ({size:,} bytes)")

    # 1. Generate Markdown report
    report_path = os.path.join(RESULTS_DIR, f"{BOOK_STEM}_REPORTE.md")
    print(f"\n[REPORT] Generating Markdown report...")
    generate_report(BOOK_STEM, RESULTS_DIR, report_path)
    report_size = os.path.getsize(report_path)
    print(f"   OK Report saved: {report_path}")
    print(f"   OK Size: {report_size:,} bytes")

    # 2. Export Q&A JSON for bot
    qa_path = os.path.join(RESULTS_DIR, f"{BOOK_STEM}_bot_qa.json")
    print(f"\n[BOT QA] Generating bot Q&A JSON...")
    export_qa_json(BOOK_STEM, RESULTS_DIR, qa_path)
    qa_size = os.path.getsize(qa_path)
    print(f"   OK Q&A JSON saved: {qa_path}")
    print(f"   OK Size: {qa_size:,} bytes")

    # 3. Quick validation
    with open(qa_path, "r", encoding="utf-8") as f:
        qa_data = json.load(f)
    print(f"\n[SUMMARY] Bot Q&A:")
    print(f"   Facts:    {len(qa_data.get('facts', []))}")
    print(f"   Concepts: {len(qa_data.get('concepts', []))}")
    print(f"   Q&A:      {len(qa_data.get('qa_pairs', []))}")

    # 4. Check report sections
    with open(report_path, "r", encoding="utf-8") as f:
        report_text = f.read()
    sections = ["Mensaje Central", "Ideas Principales", "Contenido para Redes", "Base de Conocimiento"]
    found = [s for s in sections if s in report_text]
    print(f"\n[SECTIONS] Report Sections: {len(found)}/{len(sections)}")
    for s in sections:
        status = "OK" if s in report_text else "MISSING"
        print(f"   [{status}] {s}")

    print(f"\n[DONE] Reports regenerated successfully!")


if __name__ == "__main__":
    main()

"""Quick integration test without sending email."""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from analyzers.report_builder import build_report_context, render_html_report
from config import DATABASE_PATH
from database import Database

def main():
    db = Database(DATABASE_PATH)
    models = db.get_today_models(date.today())
    ctx = build_report_context(models, date.today())
    html = render_html_report(ctx)

    out = Path("reports/test_report.html")
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")

    print("=== Report Test ===")
    print(f"Today models: {ctx['summary']['total_count']}")
    s = ctx["summary"]
    print(f"  文本大模型: {s['text_llm']}")
    print(f"  文生图:     {s['text_to_image']}")
    print(f"  图生图:     {s['image_to_image']}")
    print(f"  文生视频:   {s['text_to_video']}")
    print(f"  图生视频:   {s['image_to_video']}")
    print(f"HTML saved: {out} ({len(html)} bytes)")

    # per-platform breakdown
    platforms = {}
    for m in models:
        p = m.get("source_platform", "unknown")
        platforms[p] = platforms.get(p, 0) + 1
    print("By platform:", platforms)
    print("PASS")

if __name__ == "__main__":
    main()

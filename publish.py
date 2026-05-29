import logging
from datetime import date
from pathlib import Path

from config import DOCS_ARCHIVE_DIR, DOCS_DIR

logger = logging.getLogger(__name__)


def publish_html_report(html: str, report_date: date | None = None) -> Path:
    """将日报 HTML 发布到 docs/ 目录，供 GitHub Pages 展示。"""
    report_date = report_date or date.today()
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    index_path = DOCS_DIR / "index.html"
    archive_path = DOCS_ARCHIVE_DIR / f"{report_date.isoformat()}.html"

    index_path.write_text(html, encoding="utf-8")
    archive_path.write_text(html, encoding="utf-8")

    logger.info("Published report to %s and %s", index_path, archive_path)
    return index_path

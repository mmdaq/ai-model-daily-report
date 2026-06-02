import argparse
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

from analyzers.classifier import classify
from analyzers.gguf_analyzer import analyze_gguf
from analyzers.report_builder import build_report_context, render_html_report
from collectors import civitai_collector, github_collector, huggingface_collector, modelscope_collector
from collectors.base import ModelRecord
from config import DATABASE_PATH
from database import Database
from mail.mail_sender import send_html_email, send_html_email_if_configured
from publish import publish_html_report
from scheduler import start_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

COLLECTORS = {
    "huggingface": huggingface_collector.collect,
    "github": github_collector.collect,
    "civitai": civitai_collector.collect,
    "modelscope": modelscope_collector.collect,
}


def analyze_record(record: ModelRecord) -> ModelRecord:
    return classify(analyze_gguf(record))


def collect_all() -> list[ModelRecord]:
    records: list[ModelRecord] = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(fn): name for name, fn in COLLECTORS.items()
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                result = future.result()
                records.extend(result)
                logger.info("Collected %d items from %s", len(result), name)
            except Exception as e:
                logger.error("Collector %s failed: %s", name, e)

    return records


def save_records(db: Database, records: list[ModelRecord]) -> int:
    new_count = 0
    for record in records:
        analyzed = analyze_record(record)
        if db.insert_model(analyzed):
            new_count += 1
    return new_count


def run_daily_report(force: bool = False, publish_github: bool = False) -> None:
    db = Database(DATABASE_PATH)
    today = date.today()

    if not force and not publish_github and db.has_report_sent_today(today):
        logger.info("Report already sent today, skipping.")
        return

    logger.info("Starting collection...")
    records = collect_all()
    new_count = save_records(db, records)
    logger.info("Saved %d new models", new_count)

    report_models, report_mode = db.get_report_models(today)
    logger.info(
        "Report mode: %s, models: %d (new saved today: %d)",
        report_mode,
        len(report_models),
        new_count,
    )
    context = build_report_context(report_models, today, report_mode=report_mode)
    html = render_html_report(context)

    if publish_github:
        publish_html_report(html, today)

    subject = f"AI模型日报 - {today.isoformat()}"
    if publish_github:
        if not db.has_report_sent_today(today) or force:
            if send_html_email_if_configured(subject, html):
                db.mark_report_sent(today)
    else:
        send_html_email(subject, html)
        db.mark_report_sent(today)

    logger.info("Daily report completed.")


def main() -> None:
    parser = argparse.ArgumentParser(description="AI 模型日报邮件系统")
    parser.add_argument(
        "--once",
        action="store_true",
        help="立即执行一次采集并发送邮件",
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="启动定时任务，每天自动发送",
    )
    parser.add_argument(
        "--collect-only",
        action="store_true",
        help="仅采集数据，不发送邮件",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="强制发送（忽略今日已发送记录）",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="GitHub Actions 模式：采集、发布到 docs/、可选发邮件",
    )
    args = parser.parse_args()

    if args.collect_only:
        db = Database(DATABASE_PATH)
        records = collect_all()
        new_count = save_records(db, records)
        print(f"Collected {len(records)} items, {new_count} new.")
        for r in records[:10]:
            try:
                print(f"  [{r.source_platform}] {r.model_name}")
            except UnicodeEncodeError:
                print(f"  [{r.source_platform}] {r.model_name.encode('ascii', 'replace').decode()}")
        return

    if args.daemon:
        start_scheduler(lambda: run_daily_report(force=False))
        return

    if args.ci:
        run_daily_report(force=args.force, publish_github=True)
        return

    if args.once or len(sys.argv) == 1:
        run_daily_report(force=args.force)
        return

    parser.print_help()


if __name__ == "__main__":
    main()

"""CLI entrypoint for the STARGO Alibaba Inquiry AI Assistant.

Thin layer over :class:`stargo.app.AppContext` (the composition root). The CLI
parses arguments and delegates; all wiring lives in ``app.py``, all logic in
``control/``.

Commands:
    notify-test          send a test WeChat/WeCom message
    mail-check           poll the mailbox once and print parsed inquiries
    process <url>        run the full pipeline for one View Details URL
    debug-url <url>      open a View Details URL, dump DOM/screenshots + extraction
                         report, send nothing (for tuning Alibaba selectors)
    kb-search "<query>"  query the local knowledge index
    run                  long-running watch loop
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .app import AppContext
from .config import load_config
from .logging_setup import setup_logging

logger = logging.getLogger(__name__)


def cmd_notify_test(app: AppContext) -> int:
    if not app.notifier.configured:
        print(f"WeChat provider '{app.config.wechat.provider}' is not configured. "
              "Set the matching secret in .env.")
        return 1
    ok = app.notifier.notify_alert(
        "STARGO 测试通知",
        "如果你收到这条消息，说明微信通知已经配置成功 ✅",
    )
    print("Notification sent." if ok else "Notification failed (see logs).")
    return 0 if ok else 1


def cmd_mail_check(app: AppContext) -> int:
    inquiries = app.mail.fetch_new()
    if not inquiries:
        print("No new matching inquiry emails.")
        return 0
    print(f"Found {len(inquiries)} new inquiry email(s):\n")
    for inq in inquiries:
        print(f"- {inq.buyer_name or '(unknown)'} | {inq.country or '?'} | "
              f"{inq.product_title or '?'}")
        print(f"  preview: {inq.message_preview[:120]}")
        print(f"  url: {inq.view_details_url or '(no link found)'}\n")
    return 0


def cmd_kb_search(app: AppContext, query: str) -> int:
    results = app.knowledge.search(query, top_k=5)
    if not results:
        print("No matching knowledge docs (is knowledge.obsidian_path set?).")
        return 0
    for doc in results:
        print(f"[{doc.category}] {doc.title}  ({doc.source})")
        print(f"  {doc.text[:160].strip()}...\n")
    return 0


def cmd_process(app: AppContext, url: str) -> int:
    with app.browser() as browser:
        ctx = app.pipeline.process(browser, url)
    print(f"Done. status -> {'blocked' if not ctx.ok else 'processed'}; "
          f"screenshot: {ctx.screenshot_path or '(none)'}")
    return 0


def cmd_debug(app: AppContext, url: str) -> int:
    """Playwright debug mode: open the URL, dump DOM + screenshots, attempt
    extraction, print a report. Sends NOTHING."""
    with app.browser() as browser:
        report = browser.inspect(url)

    def _status() -> str:
        if report.get("error"):
            return f"ERROR: {report['error']}"
        if report.get("needs_login"):
            return "NEEDS LOGIN — log in to Alibaba in the opened Chrome, then retry"
        if report.get("needs_captcha"):
            return "CAPTCHA / verification — handle manually, do not bypass"
        if report.get("extraction_failed"):
            return "EXTRACTION FAILED — selectors likely need tuning (see DOM dump)"
        return "OK"

    lines = [
        "===== STARGO Alibaba Extraction Report =====",
        f"url:            {report.get('url', '')}",
        f"status:         {_status()}",
        f"buyer_name:     {report.get('buyer_name') or '(not found)'}",
        f"country:        {report.get('country') or '(not found)'}",
        f"product_title:  {report.get('product_title') or '(not found)'}",
        f"product_url:    {report.get('product_url') or '(not found)'}",
        f"latest_message: {(report.get('latest_message') or '(not found)')[:300]}",
        f"chat messages:  {report.get('chat_history_count', 0)}",
        f"dom dump:       {report.get('dom_text_path', '')} ({report.get('dom_chars', 0)} chars)",
        f"html dump:      {report.get('html_path', '')}",
        f"screenshots:    {', '.join(s for s in report.get('screenshots', []) if s)}",
    ]
    preview = report.get("chat_preview") or []
    if preview:
        lines.append("chat preview:")
        lines += [f"  - {m[:160]}" for m in preview]
    report_text = "\n".join(lines)
    print(report_text)

    # Persist the report next to the dumps.
    if report.get("dom_text_path"):
        report_path = Path(report["dom_text_path"]).with_name(
            Path(report["dom_text_path"]).stem.replace("-dom", "-report") + ".txt"
        )
        report_path.write_text(report_text, encoding="utf-8")
        print(f"\nReport saved: {report_path}")
    return 0


def cmd_run(app: AppContext) -> int:
    app.watch_service().run_forever()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="stargo", description=__doc__)
    parser.add_argument("--config", help="Path to config.yaml", default=None)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("notify-test", help="Send a test WeChat notification")
    sub.add_parser("mail-check", help="Poll the mailbox once")
    p_proc = sub.add_parser("process", help="Process a single View Details URL")
    p_proc.add_argument("url")
    p_kb = sub.add_parser("kb-search", help="Search the knowledge base")
    p_kb.add_argument("query")
    p_dbg = sub.add_parser("debug-url", help="Open an Alibaba View Details URL and dump an extraction report (sends nothing)")
    p_dbg.add_argument("url")
    sub.add_parser("run", help="Run the long-running watch loop")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_config(args.config)
    setup_logging(config.runtime.log_dir)
    app = AppContext(config)

    if args.command == "notify-test":
        return cmd_notify_test(app)
    if args.command == "mail-check":
        return cmd_mail_check(app)
    if args.command == "kb-search":
        return cmd_kb_search(app, args.query)
    if args.command == "process":
        return cmd_process(app, args.url)
    if args.command == "debug-url":
        return cmd_debug(app, args.url)
    if args.command == "run":
        return cmd_run(app)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

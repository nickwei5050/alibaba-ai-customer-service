# STARGO Alibaba Inquiry AI Assistant

A long-running local assistant that turns **Alibaba inquiry notification emails**
into **AI-drafted English replies**, sends low-risk replies automatically, and
pushes high-risk cases to WeChat for human approval.

> STARGO exports electric scooters, electric motorcycles, electric bicycles and
> electric tricycles. Alibaba does not expose a stable public customer-service
> message API for our use, so this system drives a **logged-in local Chrome**
> with Playwright instead of storing any Alibaba credentials.

## Pipeline

```
QQ Mail / Gmail  ──▶  Email watcher (IMAP)
                          │  extract "View Details" link
                          ▼
                     Task queue (SQLite)
                          │
                          ▼
                 Playwright + logged-in Chrome
                          │  read buyer message + product
                          ▼
              Knowledge engine (Obsidian + Notion)
                          │  retrieve models / prices / rules
                          ▼
                  AI reply generator (structured JSON)
                          │
                          ▼
                     Risk controller
                    /                \
            low risk                high risk
                |                        |
        auto-send reply           WeChat approval
                \                        /
                          ▼
                  CRM logger (SQLite / Sheet)
```

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium   # only needed for the browser worker

cp .env.example .env                     # fill in secrets
cp config/config.example.yaml config/config.yaml

# Step 1 — verify WeChat notifications work first (recommended)
python -m src.stargo.cli notify-test

# Run the full watch loop (email -> browser -> AI -> notify)
python -m src.stargo.cli run
```

See the build roadmap below — **do not enable auto-send until you have reviewed
50–100 real inquiries by hand.** `reply_rules.auto_send_low_risk` defaults to
`false`, and `safety.force_manual_only` defaults to `true` (a master switch that
blocks *all* sending regardless of AI output).

### Windows 本地部署（一键）

```powershell
# 1) 克隆到本地文件夹（例：E:\阿里AI客服智能体）
cd E:\
git clone https://github.com/nickwei5050/alibaba-ai-customer-service.git "阿里AI客服智能体"
cd "E:\阿里AI客服智能体"
git checkout claude/stargo-alibaba-ai-assistant-yvXH5

# 2) 一键安装（建虚拟环境 + 装依赖 + 下载浏览器 + 生成 config.yaml/.env）
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1

# 3) 编辑 .env 填密钥，然后激活环境并验证
notepad .env
.\.venv\Scripts\Activate.ps1
python -m src.stargo.cli notify-test
python -m src.stargo.cli kb-sync
python -m src.stargo.cli mail-check
python -m src.stargo.cli debug-url "真实 Alibaba View Details URL"
python -m src.stargo.cli run-once --dry-run
```

提示：
- `mail-check` 若找不到邮件，把 `config.yaml` 里 `email.subject_keyword` 改成你邮件标题真实出现的词，或留空 `""` 匹配全部。
- `debug-url` 第一次若跳登录页，在弹出的 Chrome 里手动登录阿里一次，再重跑（持久化 profile 会记住）。
- 没装 Chrome 浏览器内核时按提示运行 `python -m playwright install chromium`。

## CLI

| Command | What it does |
| --- | --- |
| `notify-test` | Send a test WeChat/WeCom message. |
| `mail-check` | Poll the mailbox once and print parsed inquiries. |
| `kb-sync` | Pull the Notion product catalog (all models' specs) into the local index. |
| `kb-search "..."` | Query the local knowledge index. |
| `debug-url URL` | Open a View Details URL, dump DOM/HTML/screenshot + extraction report. **Sends nothing.** |
| `process URL` | Run the browser + AI + notify pipeline for a single View Details URL. |
| `run-once [--dry-run]` | One full poll cycle (email→page→KB→reply→WeChat→CRM). `--dry-run` never sends. |
| `run` | Long-running watch loop. |

## Build roadmap (recommended order)

1. **WeChat notification** — get a test message on your phone (`notify-test`).
2. **Email watcher** — parse Alibaba inquiry emails (`mail-check`).
3. **Playwright + Chrome** — open the View Details link in a logged-in browser.
4. **Read buyer message** — DOM-first extraction, screenshot fallback.
5. **Knowledge base reply** — Obsidian/Notion retrieval + AI draft.
6. **Low-risk auto-send** — only after manual review proves it safe.

## Safety guarantees

- Never stores the Alibaba password — uses the existing Chrome login session.
- Never bypasses captcha / security verification — it stops and notifies you.
- Never invents prices, freight, certificates, or customs/clearance promises.
- All quotes split **bare vehicle price + battery price = total EXW price**.
- All secrets live in `.env`; every action is logged.

## Architecture — ECC (Entity · Control · Boundary)

The system is organised as three layers with **dependency inversion**: Control
depends only on Boundary *Protocols* (`boundary/interfaces.py`), never on
concrete adapters. The composition root (`app.py`) is the one place that wires
concrete implementations in. See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

```
src/stargo/
  config.py               load + validate config.yaml and .env (cross-cutting)
  logging_setup.py        console + rotating file logging (cross-cutting)
  app.py                  composition root: wire Boundary adapters into Control
  cli.py                  argparse entrypoint (delegates to app)

  entity/                 E — pure domain, no IO
    models.py             pydantic data models
    rules.py              hard rules + risk-topic detection (pure functions)

  boundary/               B — adapters to the outside world + their interfaces
    interfaces.py         Protocols: MailSource, BrowserDriver, KnowledgeBase,
                          ReplyDrafter, Notifier, CRMSink, DedupeStore
    mail_imap.py          IMAP watcher (Gmail/QQ)        -> MailSource
    mail_parser.py        Alibaba email -> EmailInquiry
    dedupe_sqlite.py      processed-email store          -> DedupeStore
    browser_playwright.py persistent-Chrome driver       -> BrowserDriver
    chat_extract.py       DOM-first chat extraction
    chat_send.py          type + send reply
    knowledge_obsidian.py Obsidian vault loader
    knowledge_notion.py   optional Notion sync
    knowledge_retriever.py keyword retriever             -> KnowledgeBase
    drafter_ai.py         OpenAI + offline drafter       -> ReplyDrafter
    notify_providers.py   WeCom / ServerChan / PushPlus (low-level)
    notifier_wechat.py    dispatcher + formatting        -> Notifier
    crm_sqlite.py         SQLite logger                  -> CRMSink
    crm_google_sheet.py   optional Google Sheet sink

  control/                C — orchestration, depends only on Entity + interfaces
    risk_controller.py    deterministic auto-send gate (final say)
    inquiry_pipeline.py   one inquiry, end to end
    watch_service.py      long-running poll loop

config/                   config.example.yaml + prompts
knowledge/                sample knowledge vault (replace with real content)
data/                     screenshots, logs, sqlite db (gitignored)
tests/                    unit tests incl. a fakes-only pipeline test
```

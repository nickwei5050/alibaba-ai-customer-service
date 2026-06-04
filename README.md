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
python -m src.stargo.main notify-test

# Run the full watch loop (email -> browser -> AI -> notify)
python -m src.stargo.main run
```

See the build roadmap below — **do not enable auto-send until you have reviewed
50–100 real inquiries by hand.** `reply_rules.auto_send_low_risk` defaults to
`false`.

## CLI

| Command | What it does |
| --- | --- |
| `notify-test` | Send a test WeChat/WeCom message. |
| `mail-check` | Poll the mailbox once and print parsed inquiries. |
| `process URL` | Run the browser + AI + notify pipeline for a single View Details URL. |
| `kb-search "..."` | Query the local knowledge index. |
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

## Project layout

```
src/stargo/
  config.py            load + validate config.yaml and .env
  models.py            pydantic data models
  main.py              CLI / orchestrator
  inbox/               IMAP watcher + Alibaba email parser + dedupe store
  browser/             Playwright driver, chat extraction, send reply
  knowledge/           Obsidian + Notion loaders, retriever, hard rules
  ai/                  reply generator + risk controller
  notify/              WeCom / ServerChan / PushPlus + dispatcher
  crm/                 SQLite logger + Google Sheet sync
config/                config.example.yaml + prompts
data/                  screenshots, logs, sqlite db (gitignored)
tests/                 unit tests for the pure logic
```

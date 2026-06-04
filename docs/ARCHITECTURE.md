# Architecture — ECC (Entity · Control · Boundary)

STARGO is built on a three-layer architecture with strict **dependency
inversion**. The goal: business logic that you can read, test, and change
without touching IMAP, Playwright, OpenAI, or any vendor SDK.

```
            ┌─────────────────────────────────────────────┐
            │                  Control (C)                 │
            │  inquiry_pipeline · risk_controller ·        │
            │  watch_service                               │
            │  depends on  ▼  (Protocols only)             │
            └───────────────┼─────────────────────────────┘
                            │
            ┌───────────────┼─────────────────────────────┐
            │             Boundary (B)                     │
            │  interfaces.py  ◀── Protocols (the contract) │
            │  mail_imap · browser_playwright ·            │
            │  knowledge_* · drafter_ai · notifier_wechat ·│
            │  crm_*  ── concrete adapters implement them  │
            └───────────────┬─────────────────────────────┘
                            │ both layers use ▼
            ┌───────────────┼─────────────────────────────┐
            │               Entity (E)                     │
            │  models.py (pydantic) · rules.py (pure)      │
            │  no IO, no vendor imports                     │
            └─────────────────────────────────────────────┘

        app.py = composition root (the ONLY place that knows
        both concrete adapters and Control — it wires them together)
```

## The three layers

### Entity (`entity/`)
Pure domain. `models.py` holds the pydantic data types that flow through the
system (`EmailInquiry`, `ChatContext`, `AIReply`, `InquiryRecord`). `rules.py`
holds STARGO's hard rules and risk-topic detection as **pure functions**. No
network, no disk, no third-party SDK. Everything else may depend on this; it
depends on nothing internal.

### Boundary (`boundary/`)
Every interaction with the outside world. `interfaces.py` declares the
**Protocols** (structural interfaces) that the Control layer programs against:
`MailSource`, `BrowserDriver`, `KnowledgeBase`, `ReplyDrafter`, `Notifier`,
`CRMSink`, `DedupeStore`. Each concrete adapter implements one Protocol by
matching its method signatures — no inheritance required.

Heavy/optional dependencies (`playwright`, `openai`, `notion-client`, `gspread`)
are **lazy-imported inside methods**, so importing the package — and running the
tests — needs none of them.

### Control (`control/`)
Business orchestration and decisions. `inquiry_pipeline.py` runs one inquiry end
to end; `risk_controller.py` is the deterministic final gate on auto-send;
`watch_service.py` is the poll loop. These import only `entity` and
`boundary.interfaces` — never a concrete adapter.

## Why dependency inversion here

- **Safety is testable.** `risk_controller` and `inquiry_pipeline` are verified
  with fakes (`tests/test_pipeline_di.py`) — no browser, network, or DB — so the
  "never auto-send a quote" guarantee is checked in milliseconds.
- **Swap vendors freely.** Replace IMAP with the Gmail API, ServerChan with
  WeCom, or SQLite with a Sheet by adding one Boundary class and changing one
  line in `app.py`. Control code does not move.
- **The blast radius is contained.** Alibaba changes its DOM? Only
  `chat_extract.py` / `chat_send.py` change. New notifier? Only `boundary/`.

## Adding a new adapter (example)

1. Pick the Protocol in `boundary/interfaces.py` (say `Notifier`).
2. Write `boundary/notifier_telegram.py` with matching methods.
3. Wire it in `app.py` (`self.notifier = TelegramNotifier(...)`).

Done — nothing in `control/` is touched.

## Relationship to gstack

[gstack](https://github.com/garrytan/gstack) (Garry Tan's Claude Code toolkit)
is a **development workflow** — a set of slash-command "skills" (`/office-hours`,
`/review`, `/qa`, `/ship`) that you install into your **local** Claude Code
(`~/.claude/commands/` or the project's `.claude/`). It governs *how you build*,
not *how the system is structured*. It is complementary to (and independent of)
this ECC architecture: you can use gstack to drive development of this codebase,
but it is not a runtime dependency and is not committed here.

"""Boundary layer (B in ECC): adapters to the outside world + their interfaces.

Every concrete adapter (IMAP, Playwright, Notion, WeChat, SQLite, ...) lives
here and implements a Protocol declared in :mod:`interfaces`. The Control layer
depends only on those Protocols, never on these concrete classes — that is the
dependency inversion that keeps business logic testable and swappable.
"""

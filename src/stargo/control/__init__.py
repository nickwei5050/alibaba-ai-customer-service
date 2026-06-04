"""Control layer (C in ECC): business orchestration and decisions.

Depends only on :mod:`stargo.entity` and the Protocols in
:mod:`stargo.boundary.interfaces` — never on concrete adapters. Wiring of
concrete implementations happens in :mod:`stargo.app`.
"""

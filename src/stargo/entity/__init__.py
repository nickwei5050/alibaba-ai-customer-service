"""Entity layer (E in ECC): pure domain models and rules.

This layer has no IO and no third-party side effects (only pydantic). Both the
Boundary and Control layers depend on it; it depends on nothing internal.
"""

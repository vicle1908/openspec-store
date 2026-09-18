"""Headless ArchiMate Open Exchange model operations."""

__all__ = ["ArchimateModel", "ModelError", "ValidationIssue", "deterministic_id"]

def __getattr__(name: str):
    if name in __all__:
        from . import engine
        return getattr(engine, name)
    raise AttributeError(name)

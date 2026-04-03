from .name_generator import GeneratorOptions, generate_candidates
from .providers import available_providers


__all__ = ["ScannerWorker", "available_providers", "GeneratorOptions", "generate_candidates"]


def __getattr__(name: str):
    if name == "ScannerWorker":
        from .scanner import ScannerWorker

        return ScannerWorker
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

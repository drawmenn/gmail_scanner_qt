__all__ = ["main"]
__version__ = "0.1.4"


def main() -> int:
    from .app import main as app_main

    return app_main()

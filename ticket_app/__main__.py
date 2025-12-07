import sys
from pathlib import Path

# Allow running `python __main__.py` directly (no parent package context)
if __package__ in (None, ""):
    base_path = Path(__file__).resolve().parent
    for p in (base_path, base_path.parent):
        p_str = str(p)
        if p_str not in sys.path:
            sys.path.insert(0, p_str)
    __package__ = "ticket_app"

from .main import main

if __name__ == "__main__":
    main()

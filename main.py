import sys
from pathlib import Path

# Allow running the app directly from the repository root (not as a package)
if __package__ in (None, ""):
    repo_path = Path(__file__).resolve().parent
    repo_str = str(repo_path)
    if repo_str not in sys.path:
        sys.path.insert(0, repo_str)

# Delegate to the real entrypoint so settings (theme, language, etc.) are applied consistently.
from ticket_app.main import main as run_app  # noqa: E402

if __name__ == "__main__":
    run_app()

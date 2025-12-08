# orgamate

Desktop Qt app (PySide6) to track tickets locally with a SQLite database. Runs offline, no server required.

## Features
- Create/edit/archive/restore tickets, detail pane with description, theme, urgency, deadline, created date.
- Instant search and quick filters (urgency, deadline: today/this week/overdue, theme).
- Color-coded themes managed in Settings; colors appear in the table.
- Notes and Post-it board with create/edit/delete and double-click edit.
- Startup alerts for overdue/due today/one-day-before (configurable).
- In-app DB import/export button (“BDD”).

## Requirements
- Python 3.11+ recommended
- PySide6 (pinned in `requirements.txt`)

## Setup
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m ticket_app
```

## Packaging (PyInstaller)
- Include assets:
  - Linux: `pyinstaller --noconsole --onefile --name orgamate --add-data "ticket_app/assets:ticket_app/assets" ticket_app/main.py`
  - Windows: `pyinstaller --noconsole --onefile --name orgamate --add-data "ticket_app/assets;ticket_app/assets" ticket_app\\main.py`
- Data/logs live in `~/.ticket_app` (Linux) or `%USERPROFILE%\.ticket_app` (Windows) when packaged.

## Notes
- Database: SQLite at `data/ticket_app.db` (dev) or user data dir when packaged.
- Settings and alerts: configurable in the “Paramètres” dialog.

## License
MIT License — see `LICENSE` for details.

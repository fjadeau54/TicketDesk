import json
import tempfile
import unittest
from pathlib import Path

from ticket_app import config
from ticket_app.db import database
from ticket_app.db.models import Ticket
from ticket_app.db.repositories import ticket_repository
from ticket_app.services.theme_service import ThemeService
from ticket_app.utils import settings_store


class SettingsStoreTests(unittest.TestCase):

    def setUp(self):
        self._orig_path = settings_store.SETTINGS_PATH
        self._tmpdir = tempfile.TemporaryDirectory()
        settings_store.SETTINGS_PATH = Path(self._tmpdir.name) / "settings.json"

    def tearDown(self):
        settings_store.SETTINGS_PATH = self._orig_path
        self._tmpdir.cleanup()

    def test_missing_file_returns_independent_copy(self):
        settings = settings_store.load_settings()
        # Mutating the returned dict must not change DEFAULT_SETTINGS
        settings["alerts"]["day_of"] = False
        self.assertTrue(settings_store.DEFAULT_SETTINGS["alerts"]["day_of"])

    def test_deep_merge_keeps_defaults_and_applies_overrides(self):
        override = {
            "alerts": {"overdue": False},
            "shortcuts": {"new": "Ctrl+Alt+N"},
            "appearance": {"mode": "dark"},
        }
        settings_store.SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(settings_store.SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(override, f)

        settings = settings_store.load_settings()

        # override applied
        self.assertFalse(settings["alerts"]["overdue"])
        self.assertEqual(settings["shortcuts"]["new"], "Ctrl+Alt+N")
        self.assertEqual(settings["appearance"]["mode"], "dark")
        # defaults preserved for missing nested keys
        self.assertTrue(settings["alerts"]["day_of"])
        self.assertEqual(settings["shortcuts"]["edit"], "Ctrl+E")
        self.assertEqual(settings["appearance"]["kanban_column"], "#f6f6f6")
        # DEFAULT_SETTINGS should remain intact
        self.assertTrue(settings_store.DEFAULT_SETTINGS["alerts"]["overdue"])


class ThemeRenameTests(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._db_path = Path(self._tmpdir.name) / "ticket_app.db"
        self._orig_db_path = database.DB_PATH
        self._orig_config_db_path = config.DB_PATH
        database.DB_PATH = self._db_path
        config.DB_PATH = self._db_path
        database.init_db()
        self.theme_service = ThemeService()

    def tearDown(self):
        database.DB_PATH = self._orig_db_path
        config.DB_PATH = self._orig_config_db_path
        from ticket_app.services.theme_service import theme_service as global_theme_service
        global_theme_service.refresh_cache()
        self._tmpdir.cleanup()

    def test_theme_rename_propagates_to_tickets(self):
        theme = self.theme_service.create("Old", "#111111")
        ticket_repository.add(
            Ticket(id=None, title="T1", description="", urgency="Basse", deadline=None, theme="Old")
        )

        theme.name = "New"
        self.theme_service.update(theme, old_name="Old")

        tickets = ticket_repository.get_all(include_archived=True)
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0].theme, "New")


if __name__ == "__main__":
    unittest.main()

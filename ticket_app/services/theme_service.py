from typing import Dict, List
from ..db.models import Theme
from ..db.repositories import theme_repository
import sqlite3


class ThemeService:

    def __init__(self):
        self._cache: Dict[str, Theme] = {}
        self.refresh_cache()

    def refresh_cache(self):
        try:
            self._cache = {t.name: t for t in theme_repository.get_all()}
        except sqlite3.OperationalError:
            # table peut ne pas exister avant init_db
            self._cache = {}

    def get_all(self) -> List[Theme]:
        return list(self._cache.values())

    def get_color_for(self, name: str) -> str | None:
        t = self._cache.get(name)
        return t.color if t else None

    def get_theme_colors(self) -> Dict[str, str]:
        return {name: theme.color for name, theme in self._cache.items()}

    def create(self, name: str, color: str, x=0, y=0, width=0, height=0) -> Theme:
        t = Theme(id=None, name=name, color=color, x=x, y=y, width=width, height=height)
        t.id = theme_repository.add(t)
        self.refresh_cache()
        return t

    def update(self, theme: Theme, old_name: str | None = None) -> None:
        theme_repository.update(theme)
        if old_name and old_name != theme.name:
            theme_repository.rename_in_tickets(old_name, theme.name)
        self.refresh_cache()

    def delete(self, theme_id: int) -> None:
        theme_repository.delete(theme_id)
        self.refresh_cache()

theme_service = ThemeService()

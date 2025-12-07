"""Tiny i18n helper with French/English strings."""

from __future__ import annotations

LANGUAGES = {
    "fr": "Français",
    "en": "English",
}

_current = "fr"

# Keys map to translated strings. French is the source of truth.
_T = {
    "app.title": {"fr": "Ticket Manager", "en": "Ticket Manager"},
    "menu.new_ticket": {"fr": "Nouveau ticket", "en": "New ticket"},
    "menu.edit": {"fr": "Modifier", "en": "Edit"},
    "menu.delete": {"fr": "Supprimer", "en": "Delete"},
    "menu.archive": {"fr": "Archiver", "en": "Archive"},
    "menu.restore": {"fr": "Restaurer", "en": "Restore"},
    "menu.refresh": {"fr": "Rafraîchir", "en": "Refresh"},
    "menu.settings": {"fr": "Paramètres", "en": "Settings"},
    "menu.db": {"fr": "BDD", "en": "DB"},
    "menu.show_archived": {"fr": "Afficher archivés", "en": "Show archived"},
    "filter.search": {"fr": "Rechercher (titre, thème, description)", "en": "Search (title, theme, description)"},
    "filter.urgency": {"fr": "Urgence", "en": "Urgency"},
    "filter.deadline": {"fr": "Échéance", "en": "Deadline"},
    "filter.theme": {"fr": "Thème", "en": "Theme"},
    "filter.all": {"fr": "Tous", "en": "All"},
    "filter.deadline.today": {"fr": "Aujourd'hui", "en": "Today"},
    "filter.deadline.week": {"fr": "Cette semaine", "en": "This week"},
    "filter.deadline.overdue": {"fr": "En retard", "en": "Overdue"},
    "urgency.low": {"fr": "Basse", "en": "Low"},
    "urgency.normal": {"fr": "Normale", "en": "Normal"},
    "urgency.high": {"fr": "Haute", "en": "High"},
    "urgency.critical": {"fr": "Critique", "en": "Critical"},
    "ticket.table.title": {"fr": "Titre", "en": "Title"},
    "ticket.table.urgency": {"fr": "Urgence", "en": "Urgency"},
    "ticket.table.deadline": {"fr": "Échéance", "en": "Deadline"},
    "ticket.table.theme": {"fr": "Thème", "en": "Theme"},
    "ticket.table.archived": {"fr": "Archivé", "en": "Archived"},
    "yes": {"fr": "Oui", "en": "Yes"},
    "no": {"fr": "Non", "en": "No"},
    "dlg.info.select_ticket": {"fr": "Sélectionne un ticket.", "en": "Select a ticket."},
    "dlg.confirm.delete_ticket": {"fr": "Supprimer le ticket #{id} ?", "en": "Delete ticket #{id}?"},
    "dlg.db.export.title": {"fr": "Exporter la base", "en": "Export database"},
    "dlg.db.export.success": {"fr": "Base exportée vers :\n{path}", "en": "Database exported to:\n{path}"},
    "dlg.db.export.error": {"fr": "Échec de l'export : {err}", "en": "Export failed: {err}"},
    "dlg.db.import.title": {"fr": "Importer une base", "en": "Import database"},
    "dlg.db.import.success": {"fr": "Base importée.\nRedémarre l'application pour prendre en compte.", "en": "Database imported.\nRestart the app to apply."},
    "dlg.db.import.error": {"fr": "Échec de l'import : {err}", "en": "Import failed: {err}"},
    "alerts.title": {"fr": "Alertes échéances", "en": "Deadline alerts"},
    "alerts.before": {"fr": "1 jour avant : {n} ticket(s)", "en": "1 day before: {n} ticket(s)"},
    "alerts.dayof": {"fr": "Aujourd'hui : {n} ticket(s)", "en": "Today: {n} ticket(s)"},
    "alerts.overdue": {"fr": "En retard : {n} ticket(s)", "en": "Overdue: {n} ticket(s)"},
    "notes.save": {"fr": "Enregistrer", "en": "Save"},
    "notes.title": {"fr": "Bloc-notes", "en": "Notebook"},
    "postit.title": {"fr": "Post-it", "en": "Post-it"},
    "postit.wall": {"fr": "Post-it (mur filtrable)", "en": "Sticky wall (filterable)"},
    "postit.filter.placeholder": {"fr": "Filtrer par texte ou #tag", "en": "Filter by text or #tag"},
    "postit.colors.all": {"fr": "Toutes les couleurs", "en": "All colors"},
    "postit.new": {"fr": "Nouveau", "en": "New"},
    "postit.edit": {"fr": "Modifier", "en": "Edit"},
    "postit.delete": {"fr": "Supprimer", "en": "Delete"},
    "postit.refresh": {"fr": "Rafraîchir", "en": "Refresh"},
    "postit.select": {"fr": "Sélectionne un post-it.", "en": "Select a post-it."},
    "postit.tags": {"fr": "Tags", "en": "Tags"},
    "postit.color": {"fr": "Couleur", "en": "Color"},
    "dlg.ok": {"fr": "OK", "en": "OK"},
    "dlg.cancel": {"fr": "Annuler", "en": "Cancel"},
    "ticket.form.title": {"fr": "Ticket", "en": "Ticket"},
    "ticket.form.field.title": {"fr": "Titre", "en": "Title"},
    "ticket.form.field.theme": {"fr": "Thème", "en": "Theme"},
    "ticket.form.field.urgency": {"fr": "Urgence", "en": "Urgency"},
    "ticket.form.field.deadline": {"fr": "Échéance", "en": "Deadline"},
    "ticket.form.field.description": {"fr": "Description", "en": "Description"},
    "detail.title": {"fr": "Détails du ticket", "en": "Ticket details"},
    "detail.theme": {"fr": "Thème", "en": "Theme"},
    "detail.urgency": {"fr": "Urgence", "en": "Urgency"},
    "detail.deadline": {"fr": "Échéance", "en": "Deadline"},
    "detail.created": {"fr": "Créé le", "en": "Created"},
    "detail.description": {"fr": "Description", "en": "Description"},
    "detail.resolve": {"fr": "Marquer comme résolu", "en": "Mark as resolved"},
    "detail.reopen": {"fr": "Réouvrir", "en": "Reopen"},
    "settings.title": {"fr": "Paramètres", "en": "Settings"},
    "settings.alerts": {"fr": "Alertes échéances", "en": "Deadline alerts"},
    "settings.alerts.before": {"fr": "1 jour avant", "en": "1 day before"},
    "settings.alerts.dayof": {"fr": "Jour J", "en": "Same day"},
    "settings.alerts.overdue": {"fr": "En retard", "en": "Overdue"},
    "settings.themes": {"fr": "Thèmes et couleurs", "en": "Themes and colors"},
    "settings.new": {"fr": "Nouveau", "en": "New"},
    "settings.edit": {"fr": "Modifier", "en": "Edit"},
    "settings.delete": {"fr": "Supprimer", "en": "Delete"},
    "settings.close": {"fr": "Fermer", "en": "Close"},
    "settings.language": {"fr": "Langue", "en": "Language"},
    "settings.reset.title": {"fr": "Réinitialiser les données", "en": "Reset data"},
    "settings.reset.button": {"fr": "Supprimer toutes les données", "en": "Delete all data"},
    "settings.reset.confirm": {"fr": "Supprimer toutes les données (tickets, thèmes, post-it, bloc-notes, paramètres) ? Cette action est irréversible.", "en": "Delete all data (tickets, themes, sticky notes, notebook, settings)? This cannot be undone."},
    "settings.reset.success": {"fr": "Données supprimées. Une base vide a été recréée.", "en": "Data deleted. A fresh database was recreated."},
    "settings.reset.error": {"fr": "Échec de la suppression : {err}", "en": "Failed to delete data: {err}"},
    "palette.title": {"fr": "Palette de commandes", "en": "Command palette"},
    "palette.search": {"fr": "Tape une commande...", "en": "Type a command..."},
    "palette.action.new": {"fr": "Nouveau ticket", "en": "New ticket"},
    "palette.action.edit": {"fr": "Modifier le ticket sélectionné", "en": "Edit selected ticket"},
    "palette.action.delete": {"fr": "Supprimer le ticket sélectionné", "en": "Delete selected ticket"},
    "palette.action.archive": {"fr": "Archiver/Restaurer le ticket sélectionné", "en": "Archive/Restore selected ticket"},
    "palette.action.focus_search": {"fr": "Mettre le focus sur la recherche", "en": "Focus search bar"},
    "palette.action.refresh": {"fr": "Rafraîchir les tickets", "en": "Refresh tickets"},
    "palette.action.open_settings": {"fr": "Ouvrir les paramètres", "en": "Open settings"},
    "shortcuts.title": {"fr": "Raccourcis clavier", "en": "Keyboard shortcuts"},
    "shortcuts.info": {"fr": "Utilise le format Qt (ex: Ctrl+K). Vide pour désactiver.", "en": "Use Qt format (e.g., Ctrl+K). Leave empty to disable."},
    "shortcuts.palette": {"fr": "Palette de commandes", "en": "Command palette"},
    "shortcuts.new": {"fr": "Nouveau ticket", "en": "New ticket"},
    "shortcuts.edit": {"fr": "Modifier", "en": "Edit"},
    "shortcuts.delete": {"fr": "Supprimer", "en": "Delete"},
    "shortcuts.archive": {"fr": "Archiver/Restaurer", "en": "Archive/Restore"},
    "shortcuts.refresh": {"fr": "Rafraîchir", "en": "Refresh"},
    "shortcuts.focus_search": {"fr": "Focus recherche", "en": "Focus search"},
    "shortcuts.settings": {"fr": "Paramètres", "en": "Settings"},
    "appearance.title": {"fr": "Apparence", "en": "Appearance"},
    "appearance.mode": {"fr": "Thème", "en": "Theme"},
    "appearance.mode.light": {"fr": "Clair", "en": "Light"},
    "appearance.mode.dark": {"fr": "Sombre", "en": "Dark"},
    "appearance.kanban_column": {"fr": "Fond des colonnes Kanban", "en": "Kanban column background"},
    "appearance.pick_color": {"fr": "Choisir", "en": "Pick"},
    "kanban.title": {"fr": "Vue Kanban", "en": "Kanban view"},
    "kanban.group_by": {"fr": "Grouper par", "en": "Group by"},
    "kanban.group.theme": {"fr": "Thème", "en": "Theme"},
    "kanban.group.urgency": {"fr": "Urgence", "en": "Urgency"},
    "kanban.no_tickets": {"fr": "Aucun ticket", "en": "No tickets"},
    "kanban.column.empty": {"fr": "Aucun ticket ici", "en": "No tickets here"},
    "palette.action.kanban": {"fr": "Ouvrir la vue Kanban", "en": "Open Kanban view"},
    "theme.dialog.title": {"fr": "Thème", "en": "Theme"},
    "theme.name": {"fr": "Nom", "en": "Name"},
    "theme.color": {"fr": "Couleur", "en": "Color"},
    "theme.posx": {"fr": "Pos X", "en": "Pos X"},
    "theme.posy": {"fr": "Pos Y", "en": "Pos Y"},
    "theme.width": {"fr": "Largeur", "en": "Width"},
    "theme.height": {"fr": "Hauteur", "en": "Height"},
    "theme.pick_color": {"fr": "Choisir couleur", "en": "Pick color"},
    "validation.name_required": {"fr": "Nom requis.", "en": "Name required."},
}


def set_language(lang: str):
    global _current
    _current = lang if lang in LANGUAGES else "fr"


def get_language() -> str:
    return _current


def tr(key: str, **kwargs) -> str:
    """Translate a key to the current language, formatting with kwargs."""
    value = _T.get(key, {}).get(_current) or _T.get(key, {}).get("fr") or key
    if kwargs:
        try:
            return value.format(**kwargs)
        except Exception:
            return value
    return value


def available_languages() -> dict[str, str]:
    return LANGUAGES.copy()

from ..db.repositories import note_repository

class NoteService:

    def get_current_content(self) -> str:
        note = note_repository.get_latest()
        return note.content if note else ""

    def save_content(self, content: str) -> None:
        # simple stratégie : chaque sauvegarde crée une nouvelle entrée
        note_repository.save_new(content)

note_service = NoteService()

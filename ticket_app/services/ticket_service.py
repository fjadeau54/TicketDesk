from typing import List
from ..db.models import Ticket
from ..db.repositories import ticket_repository

class TicketService:

    def get_all_tickets(self, include_archived: bool = False) -> List[Ticket]:
        return ticket_repository.get_all(include_archived=include_archived)

    def create_ticket(self, title, description, urgency, deadline, theme) -> Ticket:
        t = Ticket(
            id=None,
            title=title,
            description=description,
            urgency=urgency,
            deadline=deadline,
            theme=theme,
            archived=False,
        )
        t.id = ticket_repository.add(t)
        return t

    def update_ticket(self, ticket: Ticket) -> None:
        ticket_repository.update(ticket)

    def archive_ticket(self, ticket_id: int) -> None:
        ticket_repository.set_archived(ticket_id, True)

    def unarchive_ticket(self, ticket_id: int) -> None:
        ticket_repository.set_archived(ticket_id, False)

    def delete_ticket(self, ticket_id: int) -> None:
        ticket_repository.delete(ticket_id)

ticket_service = TicketService()

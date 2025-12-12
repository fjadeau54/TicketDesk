from typing import List, Optional
from .database import get_connection
from .models import Ticket, Note, PostIt, Theme

# -------- Tickets --------

class TicketRepository:

    def get_all(self, include_archived: bool = False) -> List[Ticket]:
        conn = get_connection()
        cur = conn.cursor()
        query = """
            SELECT id, title, description, urgency, deadline, theme, created_at, archived
            FROM tickets
        """
        if not include_archived:
            query += " WHERE archived = 0"
        query += " ORDER BY created_at DESC"
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()
        return [
            Ticket(
                id=row["id"],
                title=row["title"],
                description=row["description"],
                urgency=row["urgency"],
                deadline=row["deadline"],
                theme=row["theme"],
                created_at=row["created_at"],
                archived=bool(row["archived"]),
            )
            for row in rows
        ]

    def add(self, ticket: Ticket) -> int:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO tickets (title, description, urgency, deadline, theme, archived)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (ticket.title, ticket.description, ticket.urgency,
              ticket.deadline, ticket.theme, int(ticket.archived)))
        conn.commit()
        ticket_id = cur.lastrowid
        conn.close()
        return ticket_id

    def update(self, ticket: Ticket) -> None:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE tickets
            SET title = ?, description = ?, urgency = ?, deadline = ?, theme = ?, archived = ?
            WHERE id = ?
        """, (ticket.title, ticket.description, ticket.urgency,
              ticket.deadline, ticket.theme, int(ticket.archived), ticket.id))
        conn.commit()
        conn.close()

    def set_archived(self, ticket_id: int, archived: bool) -> None:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE tickets SET archived = ? WHERE id = ?
        """, (int(archived), ticket_id))
        conn.commit()
        conn.close()

    def delete(self, ticket_id: int) -> None:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
        conn.commit()
        conn.close()

ticket_repository = TicketRepository()

# -------- Notes (bloc-notes simple) --------

class NoteRepository:

    def get_latest(self) -> Optional[Note]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, content, created_at
            FROM notes
            ORDER BY created_at DESC
            LIMIT 1
        """)
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return Note(id=row["id"], content=row["content"], created_at=row["created_at"])

    def save_new(self, content: str) -> int:
        # Deprecated: kept for backward compatibility.
        return self.save_latest(content)

    def save_latest(self, content: str) -> int:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM notes WHERE id != 1")
        cur.execute("""
            INSERT INTO notes (id, content, created_at)
            VALUES (1, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE
            SET content = excluded.content,
                created_at = CURRENT_TIMESTAMP
        """, (content,))
        conn.commit()
        note_id = cur.lastrowid or 1
        conn.close()
        return note_id

note_repository = NoteRepository()

# -------- Post-it (squelette pour plus tard) --------

class PostItRepository:
    # pour l’instant on met juste un squelette minimal
    def get_all(self) -> List[PostIt]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, content, x, y, width, height, color, tags, order_index, created_at
            FROM postits
            ORDER BY order_index ASC, created_at ASC
        """)
        rows = cur.fetchall()
        conn.close()
        return [
            PostIt(
                id=row["id"],
                content=row["content"],
                x=row["x"], y=row["y"],
                width=row["width"], height=row["height"],
                color=row["color"],
                tags=row["tags"] if "tags" in row.keys() else "",
                order_index=row["order_index"] if "order_index" in row.keys() else 0,
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def add(self, postit: PostIt) -> int:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO postits (content, x, y, width, height, color, tags, order_index)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (postit.content, postit.x, postit.y, postit.width, postit.height,
              postit.color, postit.tags, postit.order_index))
        conn.commit()
        pid = cur.lastrowid
        conn.close()
        return pid

    def update(self, postit: PostIt) -> None:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE postits
            SET content = ?, x = ?, y = ?, width = ?, height = ?, color = ?, tags = ?, order_index = ?
            WHERE id = ?
        """, (postit.content, postit.x, postit.y, postit.width, postit.height,
              postit.color, postit.tags, postit.order_index, postit.id))
        conn.commit()
        conn.close()

    def delete(self, postit_id: int) -> None:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM postits WHERE id = ?", (postit_id,))
        conn.commit()
        conn.close()

    def get_max_order_index(self) -> int:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COALESCE(MAX(order_index), 0) AS max_order FROM postits")
        row = cur.fetchone()
        conn.close()
        return row["max_order"] if row else 0

    def update_order_indexes(self, ordering: List[int]) -> None:
        conn = get_connection()
        cur = conn.cursor()
        for idx, postit_id in enumerate(ordering):
            cur.execute(
                "UPDATE postits SET order_index = ? WHERE id = ?",
                (idx, postit_id)
            )
        conn.commit()
        conn.close()

postit_repository = PostItRepository()

# -------- Themes --------

class ThemeRepository:

    def get_all(self) -> List[Theme]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, color, x, y, width, height FROM themes")
        rows = cur.fetchall()
        conn.close()
        return [
            Theme(
                id=row["id"], name=row["name"], color=row["color"],
                x=row["x"], y=row["y"], width=row["width"], height=row["height"]
            )
            for row in rows
        ]

    def add(self, theme: Theme) -> int:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO themes (name, color, x, y, width, height)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (theme.name, theme.color, theme.x, theme.y, theme.width, theme.height))
        conn.commit()
        tid = cur.lastrowid
        conn.close()
        return tid

    def update(self, theme: Theme) -> None:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE themes
            SET name = ?, color = ?, x = ?, y = ?, width = ?, height = ?
            WHERE id = ?
        """, (theme.name, theme.color, theme.x, theme.y, theme.width, theme.height, theme.id))
        conn.commit()
        conn.close()

    def rename_in_tickets(self, old_name: str, new_name: str) -> None:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE tickets SET theme = ? WHERE theme = ?", (new_name, old_name))
        conn.commit()
        conn.close()

    def delete(self, theme_id: int) -> None:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM themes WHERE id = ?", (theme_id,))
        conn.commit()
        conn.close()

theme_repository = ThemeRepository()

from dataclasses import dataclass
from typing import Optional

@dataclass
class Ticket:
    id: Optional[int]
    title: str
    description: str
    urgency: str
    deadline: Optional[str]
    theme: str
    created_at: Optional[str] = None
    archived: bool = False

@dataclass
class Note:
    id: Optional[int]
    content: str
    created_at: Optional[str] = None

@dataclass
class PostIt:
    id: Optional[int]
    content: str
    x: int
    y: int
    width: int
    height: int
    color: str
    tags: str = ""
    order_index: int = 0
    created_at: Optional[str] = None

@dataclass
class Theme:
    id: Optional[int]
    name: str
    color: str
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0

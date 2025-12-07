from typing import List
from ..db.models import PostIt
from ..db.repositories import postit_repository

class PostItService:

    def get_all_postits(self) -> List[PostIt]:
        return postit_repository.get_all()

    def create_postit(
        self,
        content: str,
        tags: str = "",
        x: int = 20,
        y: int = 20,
        width: int = 150,
        height: int = 150,
        color: str = "yellow"
    ) -> PostIt:
        next_order = postit_repository.get_max_order_index() + 1
        p = PostIt(
            id=None,
            content=content,
            x=x,
            y=y,
            width=width,
            height=height,
            color=color,
            tags=tags,
            order_index=next_order
        )
        p.id = postit_repository.add(p)
        return p

    def update_postit(self, postit: PostIt) -> None:
        postit_repository.update(postit)

    def delete_postit(self, postit_id: int) -> None:
        postit_repository.delete(postit_id)

    def reorder_postits(self, ordering: List[int]) -> None:
        postit_repository.update_order_indexes(ordering)

postit_service = PostItService()

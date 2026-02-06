from sqlalchemy import func

from bot.database.models import Database
from bot.database.models.main import GoodsMedia


MAX_MEDIA_PER_ITEM = 10


def add_goods_media(item_name: str, file_id: str, media_type: str) -> int:
    """Add media to a product. Returns the new media id."""
    with Database().session() as s:
        max_pos = s.query(func.max(GoodsMedia.position)).filter(
            GoodsMedia.item_name == item_name
        ).scalar()
        position = (max_pos or 0) + 1

        media = GoodsMedia(
            item_name=item_name,
            file_id=file_id,
            media_type=media_type,
            position=position,
        )
        s.add(media)
        s.flush()
        media_id = media.id
    return media_id


def get_goods_media(item_name: str) -> list[dict]:
    """Get all media for a product, ordered by position."""
    with Database().session() as s:
        results = s.query(GoodsMedia).filter(
            GoodsMedia.item_name == item_name
        ).order_by(GoodsMedia.position).all()
        return [
            {
                'id': m.id,
                'item_name': m.item_name,
                'file_id': m.file_id,
                'media_type': m.media_type,
                'position': m.position,
            }
            for m in results
        ]


def get_goods_media_count(item_name: str) -> int:
    """Get count of media for a product."""
    with Database().session() as s:
        return s.query(GoodsMedia).filter(
            GoodsMedia.item_name == item_name
        ).count()


def delete_goods_media(media_id: int) -> bool:
    """Delete a media file by id. Returns True if deleted."""
    with Database().session() as s:
        count = s.query(GoodsMedia).filter(GoodsMedia.id == media_id).delete()
        return count > 0

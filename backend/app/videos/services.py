from app.videos.models import Video


def create_video(db, owner_id: int, caption: str = None) -> Video:
    new_video = Video(
        owner_id=owner_id,
        caption=caption,
        status="DRAFT",
        created_at="2024-01-01T00:00:00Z"  # Placeholder timestamp
    )
    db.add(new_video)
    db.commit()
    db.refresh(new_video)
    return new_video
from fastapi import APIRouter, Depends, HTTPException

from src.core.dependencies import get_current_user, get_db
from src.feed.schema import FeedSchema
from src.feed.services import get_feed_videos

router = APIRouter(prefix="/feed", tags=["feed"])

@router.get("/", response_model=FeedSchema)
def get_feed(
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):

    feed = get_feed_videos(db=db, current_user=current_user)
    return feed
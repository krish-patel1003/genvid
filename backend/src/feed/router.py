from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.db import get_session
from src.auth.utils import get_current_user
from src.feed.service import get_feed_videos
from src.feed.schema import FeedSchema

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("/", response_model=FeedSchema)
def get_feed(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    return get_feed_videos(session=session, current_user=current_user)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from src.db import get_session
from src.auth.utils import get_current_user
from src.user_interactions.schema import CommentSchema, PostCommentSchema
from src.user_interactions.service import (
    like_video,
    unlike_video,
    comment_on_video,
    get_comments_data,
    delete_user_comment,
)

router = APIRouter(prefix="/interactions", tags=["user_interactions"])

@router.post("/{video_id}/like", status_code=status.HTTP_201_CREATED)
def like(
    video_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    if not like_video(session=session, user_id=current_user.id, video_id=video_id):
        raise HTTPException(status_code=400, detail="Already liked")
    

@router.delete("/{video_id}/like", status_code=status.HTTP_204_NO_CONTENT)
def unlike(
    video_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    if not unlike_video(session=session, user_id=current_user.id, video_id=video_id):
        raise HTTPException(status_code=400, detail="Not liked")


@router.post("/{video_id}/comment", response_model=CommentSchema, status_code=201)
def post_comment(
    video_id: int,
    data: PostCommentSchema,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    return comment_on_video(
        session=session,
        user_id=current_user.id,
        video_id=video_id,
        content=data.comment_text,
        parent_comment_id=data.parent_comment_id,
    )


@router.get("/{video_id}/comments", response_model=list[CommentSchema])
def get_comments(
    video_id: int,
    session: Session = Depends(get_session),
):
    return get_comments_data(session=session, video_id=video_id)


@router.delete("/comment/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    if not delete_user_comment(
        session=session,
        comment_id=comment_id,
        user_id=current_user.id,
    ):
        raise HTTPException(status_code=404, detail="Comment not found or not yours")

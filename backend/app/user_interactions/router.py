from fastapi import APIRouter, Depends, HTTPException, status
from app.core.dependencies import get_current_user, get_db
from app.user_interactions.schema import CommentSchema, PostCommentSchema
from app.user_interactions.services import like, unlike, comment_on_video, get_comments_data, delete_user_comment

router = APIRouter(prefix="/interactions", tags=["user_interactions"])

@router.post("/{video_id}/like", status_code=201)
def like_video(
    video_id: int,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    like_obj = like(db=db, user_id=current_user.id, video_id=video_id)
    if not like_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has already liked this video.",
        )
    return like_obj


@router.delete("/{video_id}/like", status_code=204)
def unlike_video(
    video_id: int,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    unlike_obj = unlike(db=db, user_id=current_user.id, video_id=video_id)
    if not unlike_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has not liked this video yet.",
        )
    return unlike_obj


@router.post("/{video_id}/comment", response_model=CommentSchema, status_code=201)
def post_comment(
    video_id: int,
    comment_data: PostCommentSchema,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    comment = comment_on_video(
        db=db,
        user_id=current_user.id,
        video_id=video_id,
        content=comment_data.comment_text,
        parent_comment_id=comment_data.parent_comment_id,
    )
    return comment

@router.get("/{video_id}/comments", status_code=200, response_model=list[CommentSchema])
def get_comments(
    video_id: int,
    db=Depends(get_db),
):
    comments = get_comments_data(db=db, video_id=video_id)
    return comments

@router.delete("/comment/{comment_id}", status_code=204)
def delete_comment(
    comment_id: int,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    success = delete_user_comment(db=db, comment_id=comment_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you do not have permission to delete it.",
        )
    return success
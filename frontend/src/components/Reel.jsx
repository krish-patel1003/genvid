import React from 'react';
import Actions from './Actions.jsx';
import CommentsPanel from './CommentsPanel.jsx';

export default function Reel({
  video,
  isCommentsOpen,
  onLike,
  onComments,
  onFollow,
  isFollowing,
  commentDraft,
  replyTarget,
  onToggleReply,
  onDraftChange,
  onSubmitComment,
  isAuthed
}) {
  return (
    <section className="reel">
      {video.src ? (
        <video
          className="reel-video"
          data-video
          src={video.src}
          poster={video.poster || undefined}
          loop
          muted
          playsInline
        />
      ) : (
        <div className="reel-placeholder">Video unavailable</div>
      )}

      <div className="overlay">
        <div className="caption-block">
          <div className="caption-header">
            <div className="user-id">{video.userId}</div>
            <button
              type="button"
              className={`follow-btn ${isFollowing ? 'active' : ''}`}
              onClick={onFollow}
              disabled={!isAuthed}
            >
              {isFollowing ? 'Following' : 'Follow'}
            </button>
          </div>
          <p className="caption">{video.caption || 'No caption'}</p>
        </div>

        <Actions
          video={video}
          onLike={onLike}
          onComments={onComments}
          disabled={!isAuthed}
        />

        <CommentsPanel
          video={video}
          isOpen={isCommentsOpen}
          commentDraft={commentDraft}
          replyTarget={replyTarget}
          onToggleReply={onToggleReply}
          onDraftChange={onDraftChange}
          onSubmit={onSubmitComment}
        />
      </div>
    </section>
  );
}

import React from 'react';
import CommentItem from './CommentItem.jsx';

export default function CommentsPanel({
  video,
  isOpen,
  commentDraft,
  replyTarget,
  onToggleReply,
  onDraftChange,
  onSubmit
}) {
  const comments = video.comments || [];

  return (
    <div className={`comments-panel ${isOpen ? 'open' : ''}`}>
      <div className="comments-header">Comments</div>
      <div className="comment-input">
        <input
          type="text"
          placeholder={replyTarget ? 'Write a reply' : 'Add a comment'}
          value={commentDraft}
          onChange={(event) => onDraftChange(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter') onSubmit();
          }}
        />
        <button type="button" onClick={onSubmit}>
          Post
        </button>
      </div>
      {replyTarget && (
        <button
          type="button"
          className="reply-indicator"
          onClick={() => onToggleReply(null)}
        >
          Replying · Cancel
        </button>
      )}
      <ul className="comment-list">
        {comments.length === 0 && (
          <li className="comment-empty">No comments yet.</li>
        )}
        {comments.map((comment) => (
          <CommentItem
            key={comment.id}
            comment={comment}
            onReply={onToggleReply}
          />
        ))}
      </ul>
    </div>
  );
}

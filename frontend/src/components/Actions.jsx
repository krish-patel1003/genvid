import React from 'react';
import { countAllComments } from '../utils/comments.js';

export default function Actions({ video, onLike, onComments, disabled }) {
  const commentsCount =
    typeof video.comments_count === 'number'
      ? video.comments_count
      : countAllComments(video.comments || []);

  return (
    <div className="actions">
      <button
        type="button"
        className={`action-btn ${video.liked ? 'active' : ''}`}
        onClick={onLike}
        aria-pressed={video.liked ? 'true' : 'false'}
        disabled={disabled}
      >
        <span className="icon">♥</span>
        <span className="count">{(video.likes || 0).toLocaleString()}</span>
      </button>
      <button
        type="button"
        className="action-btn"
        onClick={onComments}
        disabled={disabled}
      >
        <span className="icon">💬</span>
        <span className="count">{commentsCount.toLocaleString()}</span>
      </button>
    </div>
  );
}

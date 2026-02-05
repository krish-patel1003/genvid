import React from 'react';

export default function CommentItem({ comment, onReply, depth = 0 }) {
  return (
    <li className={`comment-item depth-${depth}`}>
      <div className="comment-text">{comment.text}</div>
      <button
        type="button"
        className="comment-reply"
        onClick={() => onReply(comment.id)}
      >
        Reply
      </button>
      {comment.replies && comment.replies.length > 0 && (
        <ul className="comment-list nested">
          {comment.replies.map((child) => (
            <CommentItem
              key={child.id}
              comment={child}
              onReply={onReply}
              depth={Math.min(depth + 1, 3)}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

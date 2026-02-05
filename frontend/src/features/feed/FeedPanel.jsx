import React from "react";
import Card from "../../components/Card.jsx";
import SectionHeader from "../../components/SectionHeader.jsx";
import Button from "../../components/Button.jsx";
import Chip from "../../components/Chip.jsx";

export default function FeedPanel({
  feed,
  loading,
  isAuthed,
  onRefresh,
  onToggleLike,
  onLoadComments,
  commentDrafts,
  onCommentDraftChange,
  commentsByVideo,
  onSubmitComment,
  onDeleteComment
}) {
  return (
    <Card>
      <SectionHeader
        title="Feed"
        subtitle="Browse the latest videos."
        actions={(
          <Button variant="ghost" type="button" onClick={onRefresh} disabled={!isAuthed}>
            {loading ? "Refreshing..." : "Refresh feed"}
          </Button>
        )}
      />
      {!isAuthed && <p className="muted">Sign in to load the feed.</p>}
      <div className="feed">
        {feed.items?.map((item) => (
          <article key={item.video_id} className="feed-item">
            <div className="feed-head">
              <div>
                <h3>{item.owner_username}</h3>
                <p className="muted">{item.caption || "No caption"}</p>
              </div>
              <Chip>Video #{item.video_id}</Chip>
            </div>
            <div className="stats">
              <span>{item.likes_count} likes</span>
              <span>{item.comments_count} comments</span>
            </div>
            <div className="button-row">
              <Button
                variant={item.is_liked_by_user ? "solid" : "outline"}
                type="button"
                onClick={() => onToggleLike(item)}
                disabled={!isAuthed}
              >
                {item.is_liked_by_user ? "Unlike" : "Like"}
              </Button>
              <Button variant="ghost" type="button" onClick={() => onLoadComments(item.video_id)}>
                View comments
              </Button>
            </div>

            <div className="comment-box">
              <input
                type="text"
                placeholder="Write a comment"
                value={commentDrafts[item.video_id] || ""}
                onChange={(event) =>
                  onCommentDraftChange(item.video_id, event.target.value)
                }
                disabled={!isAuthed}
              />
              <Button
                type="button"
                onClick={() => onSubmitComment(item.video_id)}
                disabled={!isAuthed}
              >
                Post
              </Button>
            </div>

            {(commentsByVideo[item.video_id] || []).length > 0 && (
              <ul className="plain-list">
                {commentsByVideo[item.video_id].map((comment, idx) => (
                  <li key={`${comment.created_at || idx}`}>
                    <div className="comment">
                      <span>{comment.content}</span>
                      {comment.id && (
                        <Button
                          variant="ghost"
                          type="button"
                          onClick={() => onDeleteComment(comment.id, item.video_id)}
                          disabled={!isAuthed}
                        >
                          Delete
                        </Button>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </article>
        ))}
      </div>
    </Card>
  );
}

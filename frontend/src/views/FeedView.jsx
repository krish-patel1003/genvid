import React, { useEffect, useMemo } from 'react';
import Reel from '../components/Reel.jsx';

export default function FeedView({
  videos,
  openCommentsId,
  commentDrafts,
  replyTargets,
  onToggleLike,
  onToggleComments,
  onToggleReply,
  onDraftChange,
  onSubmitComment,
  onFollow,
  isAuthed
}) {
  const videoIds = useMemo(() => videos.map((video) => video.id), [videos]);

  useEffect(() => {
    const elements = Array.from(document.querySelectorAll('video[data-video]'));
    if (!elements.length) return undefined;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const video = entry.target;
          if (entry.isIntersecting) {
            video.play().catch(() => {});
          } else {
            video.pause();
          }
        });
      },
      { threshold: 0.65 }
    );

    elements.forEach((el) => observer.observe(el));

    return () => observer.disconnect();
  }, [videoIds]);

  if (!isAuthed) {
    return (
      <main className="feed">
        <div className="empty-state">
          Sign in to view your personalized feed.
        </div>
      </main>
    );
  }

  return (
    <main className="feed">
      {videos.length === 0 && (
        <div className="empty-state">No videos yet. Check back soon.</div>
      )}
      {videos.map((video) => (
        <Reel
          key={video.id}
          video={video}
          isCommentsOpen={openCommentsId === video.id}
          onLike={() => onToggleLike(video.id)}
          onComments={() => onToggleComments(video.id)}
          commentDraft={commentDrafts[video.id] || ''}
          replyTarget={replyTargets[video.id] || null}
          onToggleReply={(commentId) => onToggleReply(video.id, commentId)}
          onDraftChange={(value) => onDraftChange(video.id, value)}
          onSubmitComment={() => onSubmitComment(video.id)}
          onFollow={() => onFollow(video)}
          isFollowing={video.isFollowing}
          isAuthed={isAuthed}
        />
      ))}
    </main>
  );
}

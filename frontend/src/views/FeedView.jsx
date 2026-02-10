import React from 'react';

const formatDateTime = (value) => {
  if (!value) return '';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
};

export default function FeedView({
  generations,
  previews,
  isAuthed,
  isLoading,
  onReload,
  onRefresh,
  onPreview,
  onPublish
}) {
  if (!isAuthed) {
    return (
      <main className="library-view">
        <div className="empty-state">
          Sign in to view your generations.
        </div>
      </main>
    );
  }

  return (
    <main className="library-view">
      <header className="library-header">
        <div>
          <h2>Generation Library</h2>
          <p>Track queued, running, and published jobs.</p>
        </div>
        <button type="button" onClick={onReload} disabled={isLoading}>
          {isLoading ? 'Refreshing...' : 'Refresh'}
        </button>
      </header>

      {generations.length === 0 && (
        <div className="empty-state">
          No generations yet. Head to Create to start a new job.
        </div>
      )}

      <div className="generation-list">
        {generations.map((generation) => {
          const preview = previews[generation.id];
          const previewVideo = preview?.preview_video_url;
          const previewThumbnail = preview?.preview_thumbnail_url;
          const status = generation.status || '';
          const statusClass = status ? `status-${status.toLowerCase()}` : '';
          const canPublish = status === 'SUCCEEDED';

          return (
            <article key={generation.id} className="generation-card">
              <div className="generation-media">
                {previewVideo ? (
                  <video
                    src={previewVideo}
                    poster={previewThumbnail || undefined}
                    muted
                    loop
                    playsInline
                    preload="metadata"
                  />
                ) : previewThumbnail ? (
                  <img src={previewThumbnail} alt="Preview" />
                ) : (
                  <div className="preview-placeholder">No preview</div>
                )}
              </div>
              <div className="generation-body">
                <div className="generation-meta">
                  <span className={`status-pill ${statusClass}`}>{status || 'UNKNOWN'}</span>
                  <span>#{generation.id}</span>
                  {generation.created_at && (
                    <span>{formatDateTime(generation.created_at)}</span>
                  )}
                </div>
                <p className="generation-prompt">{generation.prompt}</p>
                {generation.error_message && (
                  <div className="generation-error">{generation.error_message}</div>
                )}
                <div className="generation-actions">
                  <button type="button" onClick={() => onRefresh(generation.id)}>
                    Refresh
                  </button>
                  <button
                    type="button"
                    onClick={() => onPreview(generation.id)}
                    disabled={!canPublish}
                  >
                    Get preview
                  </button>
                  <button
                    type="button"
                    onClick={() => onPublish(generation.id)}
                    disabled={!canPublish}
                  >
                    Publish
                  </button>
                </div>
              </div>
            </article>
          );
        })}
      </div>
    </main>
  );
}

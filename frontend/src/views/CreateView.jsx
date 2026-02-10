import React, { useMemo } from 'react';

const formatDateTime = (value) => {
  if (!value) return '';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
};

export default function CreateView({
  prompt,
  isAuthed,
  isSubmitting,
  latestGeneration,
  preview,
  onPromptChange,
  onGenerate,
  onRefresh,
  onFetchPreview,
  onPublish
}) {
  const canSubmit = useMemo(() => prompt.trim().length > 0, [prompt]);
  const status = latestGeneration?.status || '';
  const statusClass = status ? `status-${status.toLowerCase()}` : '';
  const canPublish = status === 'SUCCEEDED';
  const previewVideo = preview?.preview_video_url;
  const previewThumbnail = preview?.preview_thumbnail_url;
  const isDisabled = !isAuthed || isSubmitting;

  return (
    <main className="create-view">
      <div className="create-header">
        <h2>AI Video Studio</h2>
        <p>Generate short reels with a single prompt.</p>
      </div>

      <section className="generator-panel">
        <div className="generator-header">
          <div className="generator-title">
            <span className="status-pill">Generation</span>
            {status && (
              <span className={`status-pill ${statusClass}`}>
                {status}
              </span>
            )}
          </div>
          {latestGeneration && (
            <div className="generator-meta">
              <span>#{latestGeneration.id}</span>
              {latestGeneration.created_at && (
                <span>{formatDateTime(latestGeneration.created_at)}</span>
              )}
            </div>
          )}
        </div>

        <div className="prompt-field">
          <label htmlFor="prompt">Prompt</label>
          <textarea
            id="prompt"
            placeholder={
              !isAuthed
                ? 'Sign in to generate'
                : 'Describe the scene, motion, and style...'
            }
            value={prompt}
            onChange={(event) => onPromptChange(event.target.value)}
            disabled={!isAuthed}
          />
        </div>

        <div className="generator-actions">
          <button
            type="button"
            onClick={onGenerate}
            disabled={isDisabled || !canSubmit}
          >
            {isSubmitting ? 'Generating...' : 'Generate'}
          </button>
          {latestGeneration && (
            <>
              <button
                type="button"
                onClick={() => onRefresh(latestGeneration.id)}
                disabled={!isAuthed}
              >
                Refresh status
              </button>
              <button
                type="button"
                onClick={() => onFetchPreview(latestGeneration.id)}
                disabled={!isAuthed || !canPublish}
              >
                Get preview
              </button>
              <button
                type="button"
                onClick={() => onPublish(latestGeneration.id)}
                disabled={!isAuthed || !canPublish}
              >
                Publish
              </button>
            </>
          )}
        </div>

        {!isAuthed && (
          <div className="callout">
            Sign in to start a generation. Your access token is saved locally.
          </div>
        )}

        {latestGeneration?.error_message && (
          <div className="generation-error">{latestGeneration.error_message}</div>
        )}

        {latestGeneration && (
          <div className="generation-details">
            <div>
              <span className="label">Prompt</span>
              <span>{latestGeneration.prompt}</span>
            </div>
            <div>
              <span className="label">Status</span>
              <span>{latestGeneration.status}</span>
            </div>
          </div>
        )}
      </section>

      <section className="preview-panel">
        <div className="preview-header">
          <div>
            <h3>Preview</h3>
            <p>
              {latestGeneration
                ? `Generation #${latestGeneration.id}`
                : 'Create a generation to see previews'}
            </p>
          </div>
          {latestGeneration && (
            <div className="preview-actions">
              <button
                type="button"
                onClick={() => onFetchPreview(latestGeneration.id)}
                disabled={!isAuthed || !canPublish}
              >
                Refresh preview
              </button>
              <button
                type="button"
                onClick={() => onPublish(latestGeneration.id)}
                disabled={!isAuthed || !canPublish}
              >
                Publish
              </button>
            </div>
          )}
        </div>
        {previewVideo ? (
          <video
            className="preview-video"
            src={previewVideo}
            poster={previewThumbnail || undefined}
            controls
            muted
            loop
            playsInline
          />
        ) : previewThumbnail ? (
          <img
            className="preview-image"
            src={previewThumbnail}
            alt="Preview thumbnail"
          />
        ) : (
          <div className="preview-placeholder">
            {latestGeneration && latestGeneration.status === 'SUCCEEDED'
              ? 'Preview ready. Fetch the preview URLs to view it.'
              : 'Preview will appear here.'}
          </div>
        )}
      </section>
    </main>
  );
}

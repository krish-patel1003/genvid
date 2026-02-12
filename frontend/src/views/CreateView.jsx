import React, { useMemo } from 'react';

export default function CreateView({
  messages,
  prompt,
  pendingApproval,
  previewUrl,
  generationId,
  generationStatus,
  isLocked,
  isAuthed,
  draftGenerations = [],
  onSelectDraft,
  onPromptChange,
  onGenerate,
  onApprove
}) {
  const canSubmit = useMemo(() => prompt.trim().length > 0, [prompt]);
  const isDisabled = !isAuthed || isLocked;
  const formatTimestamp = (value) => {
    if (!value) return '';
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) return value;
    return parsed.toLocaleString();
  };

  return (
    <main className="create-view">
      <div className="create-header">
        <h2>AI Video Studio</h2>
        <p>Generate short reels with a single prompt.</p>
      </div>

      <div className="chat-panel">
        <div className="chat-actions">
          <div className="status-pill">Creative mode</div>
        </div>
        <div className="chat-messages">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`chat-bubble ${message.role}`}
            >
              {message.text}
            </div>
          ))}
        </div>
        <div className="chat-input">
          <input
            type="text"
            placeholder={
              !isAuthed
                ? 'Sign in to generate'
                : isLocked
                  ? 'Finish the current generation to continue'
                  : 'Describe your video...'
            }
            value={prompt}
            onChange={(event) => onPromptChange(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && !isDisabled && canSubmit) onGenerate();
            }}
            disabled={isDisabled}
          />
          <button type="button" onClick={onGenerate} disabled={isDisabled || !canSubmit}>
            Generate
          </button>
        </div>
      </div>

      {(generationId || previewUrl) && (
        <section className="preview-panel">
          <div className="preview-header">
            <div>
              <h3>Generated preview</h3>
              <p>
                {generationId ? `Generation #${generationId}` : 'Generation'}{' '}
                {generationStatus ? `· ${generationStatus}` : ''}
              </p>
            </div>
            {pendingApproval && (
              <div className="preview-actions">
                <button type="button" onClick={() => onApprove(true)}>
                  Publish now
                </button>
                <button type="button" onClick={() => onApprove(false)}>
                  Not now
                </button>
              </div>
            )}
          </div>
          {previewUrl ? (
            <video
              className="preview-video"
              src={previewUrl}
              controls
              muted
              loop
              playsInline
            />
          ) : (
            <div className="preview-placeholder">Preview will appear here.</div>
          )}
        </section>
      )}

      {draftGenerations.length > 0 && (
        <section className="drafts-panel">
          <div className="drafts-header">
            <h3>Unpublished drafts</h3>
            <p>Pick a generation to review or publish.</p>
          </div>
          <div className="drafts-grid">
            {draftGenerations.map((job) => (
              <button
                key={job.id}
                type="button"
                className="draft-card"
                onClick={() => onSelectDraft?.(job)}
              >
                <div className="draft-card-title">Generation #{job.id}</div>
                {job.prompt && <div className="draft-card-prompt">{job.prompt}</div>}
                <div className="draft-card-meta">
                  <span>{job.status}</span>
                  {job.updated_at && <span>{formatTimestamp(job.updated_at)}</span>}
                </div>
              </button>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}

import React, { useMemo } from 'react';

export default function CreateView({
  messages,
  prompt,
  pendingApproval,
  previewUrl,
  generationId,
  generationStatus,
  isAuthed,
  onPromptChange,
  onGenerate,
  onApprove
}) {
  const canSubmit = useMemo(() => prompt.trim().length > 0, [prompt]);

  return (
    <main className="create-view">
      <div className="create-header">
        <h2>AI Video Studio</h2>
        <p>Generate short reels with a single prompt.</p>
      </div>

      <div className="chat-panel">
        <div className="chat-actions">
          <div className="status-pill">Creative mode</div>
          {pendingApproval && (
            <div className="approval-actions">
              <button type="button" onClick={() => onApprove(true)}>
                Approve post
              </button>
              <button type="button" onClick={() => onApprove(false)}>
                Cancel
              </button>
            </div>
          )}
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
            placeholder={isAuthed ? 'Describe your video...' : 'Sign in to generate'}
            value={prompt}
            onChange={(event) => onPromptChange(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter') onGenerate();
            }}
            disabled={!isAuthed}
          />
          <button type="button" onClick={onGenerate} disabled={!isAuthed || !canSubmit}>
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
    </main>
  );
}

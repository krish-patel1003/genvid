import React, { useMemo } from 'react';

export default function CreateView({
  messages,
  prompt,
  pendingApproval,
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
    </main>
  );
}

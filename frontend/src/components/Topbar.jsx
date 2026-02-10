import React from 'react';

export default function Topbar({ isAuthed, onLogout }) {
  return (
    <header className="topbar">
      <div className="brand">
        <span className="brand-mark" />
        Genvid
      </div>
      <div className="topbar-right">
        <div className="brand-sub">AI video studio</div>
        {isAuthed && (
          <button type="button" className="logout-btn" onClick={onLogout} aria-label="Log out">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 4h6a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-6" />
              <path d="M8 12h8M8 12l3-3M8 12l3 3" />
            </svg>
          </button>
        )}
      </div>
    </header>
  );
}

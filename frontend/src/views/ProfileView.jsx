import React from 'react';

export default function ProfileView({
  isAuthed,
  authMode,
  onAuthModeChange,
  authForm,
  onAuthChange,
  onAuthSubmit,
  authError,
  googleUrl,
  accountInfo,
  maskedToken,
  onCopyToken,
  onLogout
}) {
  if (!isAuthed) {
    return (
      <main className="profile-view">
        <div className="auth-panel">
          <div className="auth-toggle">
            <button
              type="button"
              className={authMode === 'login' ? 'active' : ''}
              onClick={() => onAuthModeChange('login')}
            >
              Sign in
            </button>
            <button
              type="button"
              className={authMode === 'signup' ? 'active' : ''}
              onClick={() => onAuthModeChange('signup')}
            >
              Sign up
            </button>
          </div>

          <form className="auth-form" onSubmit={onAuthSubmit}>
            {authMode === 'signup' && (
              <input
                type="email"
                placeholder="Email"
                value={authForm.email}
                onChange={(event) => onAuthChange({ email: event.target.value })}
                required
              />
            )}
            <input
              type="text"
              placeholder="Username"
              value={authForm.username}
              onChange={(event) => onAuthChange({ username: event.target.value })}
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={authForm.password}
              onChange={(event) => onAuthChange({ password: event.target.value })}
              required
            />
            {authError && <div className="auth-error">{authError}</div>}
            <div className="auth-actions">
              <button type="submit">
                {authMode === 'signup' ? 'Create account' : 'Sign in'}
              </button>
              <a href={googleUrl}>Continue with Google</a>
            </div>
          </form>
        </div>
      </main>
    );
  }

  return (
    <main className="profile-view">
      <section className="account-card">
        <div className="account-header">
          <div>
            <h2>Account</h2>
            <p>Signed in and ready to generate.</p>
          </div>
          <span className="status-pill status-succeeded">Active</span>
        </div>
        <div className="account-row">
          <span>Username</span>
          <strong>{accountInfo.username || '—'}</strong>
        </div>
        {accountInfo.email && (
          <div className="account-row">
            <span>Email</span>
            <strong>{accountInfo.email}</strong>
          </div>
        )}
        <div className="account-row token-row">
          <span>Access token</span>
          <code>{maskedToken || 'Unavailable'}</code>
          <button type="button" onClick={onCopyToken}>
            Copy
          </button>
        </div>
        <button type="button" className="ghost-button" onClick={onLogout}>
          Sign out
        </button>
      </section>
    </main>
  );
}

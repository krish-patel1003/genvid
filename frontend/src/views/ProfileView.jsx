import React, { useState } from 'react';

export default function ProfileView({
  isAuthed,
  user,
  postedVideos,
  followers,
  following,
  creatorIndex = [],
  profileForm = { username: '', bio: '' },
  profilePicPreview = '',
  profileSaving = false,
  profileUploading = false,
  onFetchFollowers,
  onFetchFollowing,
  onProfileChange,
  onProfileSave,
  onProfileFileSelect,
  onProfileUpload,
  authMode,
  onAuthModeChange,
  authForm,
  onAuthChange,
  onAuthSubmit,
  googleUrl,
  authError
}) {
  const [openList, setOpenList] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCreator, setSelectedCreator] = useState(null);
  const [activeVideoSrc, setActiveVideoSrc] = useState('');
  const [editOpen, setEditOpen] = useState(false);

  const handleOpenList = (type) => {
    setOpenList(type);
    if (type === 'followers') {
      onFetchFollowers();
    } else if (type === 'following') {
      onFetchFollowing();
    }
  };

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

  const pfpSrc = profilePicPreview || user?.profile_pic || '';
  const username = user?.username ? `@${user.username}` : '@creator';
  const bio = user?.bio || 'No Bio';
  const normalizedSearch = searchTerm.trim().replace(/^@/, '').toLowerCase();
  const searchResults = normalizedSearch
    ? creatorIndex.filter((creator) =>
        creator.username.toLowerCase().includes(normalizedSearch)
      )
    : [];

  return (
    <main className="profile-view">
      <section className="profile-card">
        {pfpSrc ? (
          <img className="profile-pfp" src={pfpSrc} alt="Profile" />
        ) : (
          <div className="profile-pfp" />
        )}
        <div className="profile-meta">
          <h2>{username}</h2>
          <p>{bio}</p>
          <div className="profile-stats">
            <button type="button" onClick={() => handleOpenList('followers')}>
              <span className="stat-number">{followers.length}</span>
              <span className="stat-label">Followers</span>
            </button>
            <button type="button" onClick={() => handleOpenList('following')}>
              <span className="stat-number">{following.length}</span>
              <span className="stat-label">Following</span>
            </button>
          </div>
        </div>
        <button type="button" className="edit-toggle" onClick={() => setEditOpen((prev) => !prev)}>
          {editOpen ? 'Close edit' : 'Edit profile'}
        </button>
      </section>

      {editOpen && (
        <section className="profile-edit">
          <div className="grid-header">Edit profile</div>
          <div className="edit-grid">
            <label>
              Username
              <input
                type="text"
                value={profileForm.username}
                onChange={(event) => onProfileChange({ username: event.target.value })}
              />
            </label>
            <label>
              Bio
              <input
                type="text"
                value={profileForm.bio}
                onChange={(event) => onProfileChange({ bio: event.target.value })}
              />
            </label>
          </div>
          <div className="edit-actions">
            <button type="button" onClick={onProfileSave} disabled={profileSaving}>
              {profileSaving ? 'Saving...' : 'Save profile'}
            </button>
          </div>
          <div className="edit-upload">
            <input
              type="file"
              accept="image/*"
              onChange={(event) => onProfileFileSelect(event.target.files?.[0])}
            />
            <button type="button" onClick={onProfileUpload} disabled={profileUploading}>
              {profileUploading ? 'Uploading...' : 'Upload photo'}
            </button>
          </div>
        </section>
      )}

      <section className="profile-search">
        <div className="grid-header">Find creators</div>
        <div className="search-row">
          <input
            type="text"
            placeholder="Search by username"
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
          />
        </div>
        {searchResults.length > 0 && (
          <ul className="search-results">
            {searchResults.map((creator) => (
              <li key={creator.username}>
                <button type="button" onClick={() => setSelectedCreator(creator)}>
                  @{creator.username}
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="profile-grid">
        <div className="grid-header">Your Reels</div>
        <div className="grid-content">
          {postedVideos.length === 0 && (
            <div className="grid-placeholder">No videos yet</div>
          )}
          {postedVideos.map((video) => (
            video.src ? (
              <video
                key={video.id}
                className="grid-video"
                src={video.src}
                muted
                loop
                playsInline
                preload="metadata"
                onClick={() => setActiveVideoSrc(video.src)}
              />
            ) : (
              <div key={video.id} className="grid-placeholder">Video</div>
            )
          ))}
        </div>
      </section>

      {openList && (
        <div className="modal-backdrop" onClick={() => setOpenList(null)}>
          <div className="modal" onClick={(event) => event.stopPropagation()}>
            <div className="modal-header">
              <h3>{openList === 'followers' ? 'Followers' : 'Following'}</h3>
              <button type="button" onClick={() => setOpenList(null)}>
                Close
              </button>
            </div>
            <ul className="modal-list">
              {(openList === 'followers' ? followers : following).map((profile) => (
                <li key={profile.id || profile.email || profile.username}>
                  {profile.username || profile.email}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {selectedCreator && (
        <div className="modal-backdrop" onClick={() => setSelectedCreator(null)}>
          <div className="modal" onClick={(event) => event.stopPropagation()}>
            <div className="modal-header">
              <h3>@{selectedCreator.username}</h3>
              <button type="button" onClick={() => setSelectedCreator(null)}>
                Close
              </button>
            </div>
            <div className="grid-content">
              {selectedCreator.videos.length === 0 && (
                <div className="grid-placeholder">No videos found</div>
              )}
              {selectedCreator.videos.map((video) => (
                video.src ? (
                  <video
                    key={video.id}
                    className="grid-video"
                    src={video.src}
                    muted
                    loop
                    playsInline
                    preload="metadata"
                    onClick={() => setActiveVideoSrc(video.src)}
                  />
                ) : (
                  <div key={video.id} className="grid-placeholder">Video</div>
                )
              ))}
            </div>
          </div>
        </div>
      )}

      {activeVideoSrc && (
        <div className="modal-backdrop" onClick={() => setActiveVideoSrc('')}>
          <div className="video-modal" onClick={(event) => event.stopPropagation()}>
            <video src={activeVideoSrc} controls autoPlay playsInline />
          </div>
        </div>
      )}
    </main>
  );
}

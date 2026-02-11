import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import BottomNav from './components/BottomNav.jsx';
import Topbar from './components/Topbar.jsx';
import FeedView from './views/FeedView.jsx';
import CreateView from './views/CreateView.jsx';
import ProfileView from './views/ProfileView.jsx';
import { api, googleLoginUrl, uploadProfilePic } from './services/api.js';
import { addNestedComment, buildCommentTree } from './utils/comments.js';

const buildMessage = (role, text) => ({
  id: `${role}-${Date.now()}-${Math.random()}`,
  role,
  text
});

const API_BASE = import.meta.env.VITE_API_BASE;

const buildGeneratedVideoUrl = (filePath) => {
  if (!filePath) return '';
  const normalized = filePath.replace(/\\\\/g, '/');
  const fileName = normalized.split('/').pop();
  if (!fileName) return '';
  return `${API_BASE}/generated/${fileName}`;
};

export default function App() {
  const [activeTab, setActiveTab] = useState('feed');
  const [token, setToken] = useState(() => localStorage.getItem('genvid_token') || '');
  const [user, setUser] = useState(null);
  const [authMode, setAuthMode] = useState('login');
  const [authForm, setAuthForm] = useState({ email: '', username: '', password: '' });
  const [authError, setAuthError] = useState('');
  const [profileForm, setProfileForm] = useState({ username: '', bio: '' });
  const [profilePicFile, setProfilePicFile] = useState(null);
  const [profilePicPreview, setProfilePicPreview] = useState('');
  const [profileSaving, setProfileSaving] = useState(false);
  const [profileUploading, setProfileUploading] = useState(false);
  const profilePreviewRef = useRef(null);

  const [feedItems, setFeedItems] = useState([]);
  const [feedLoading, setFeedLoading] = useState(false);
  const [openCommentsId, setOpenCommentsId] = useState(null);
  const [commentDrafts, setCommentDrafts] = useState({});
  const [replyTargets, setReplyTargets] = useState({});
  const [commentsByVideo, setCommentsByVideo] = useState({});

  const [messages, setMessages] = useState([
    buildMessage('assistant', 'Describe the vibe, action, and duration. I will draft a short video.')
  ]);
  const [prompt, setPrompt] = useState('');
  const [pendingApproval, setPendingApproval] = useState(false);
  const [latestGeneration, setLatestGeneration] = useState(null);

  const [postedVideos, setPostedVideos] = useState([]);
  const [followers, setFollowers] = useState([]);
  const [following, setFollowing] = useState([]);
  const [followedUsers, setFollowedUsers] = useState({});
  const [ownerIdByVideo, setOwnerIdByVideo] = useState({});

  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');

  const isAuthed = useMemo(() => Boolean(token), [token]);
  const followedUsernames = useMemo(() => {
    const names = new Set();
    following.forEach((profile) => {
      if (profile?.username) names.add(profile.username);
    });
    return names;
  }, [following]);

  const feedVideos = useMemo(() =>
    feedItems.map((item) => {
      const ownerId = item.owner_id ?? ownerIdByVideo[item.video_id];
      const ownerUsername = item.owner_username || '';
      const isFollowing = ownerId
        ? Boolean(followedUsers[ownerId])
        : ownerUsername
          ? followedUsernames.has(ownerUsername)
          : false;

      return {
        id: item.video_id,
        ownerId,
        ownerUsername,
        userId: ownerUsername ? `@${ownerUsername}` : '@creator',
        caption: item.caption,
        src: item.video_url || '',
        poster: item.thumbnail_url || '',
        likes: item.likes_count ?? 0,
        liked: Boolean(item.is_liked_by_user),
        comments_count: item.comments_count ?? 0,
        comments: commentsByVideo[item.video_id] || [],
        isFollowing
      };
    }),
  [feedItems, commentsByVideo, ownerIdByVideo, followedUsers, followedUsernames]);

  const creatorIndex = useMemo(() => {
    const map = new Map();
    feedItems.forEach((item) => {
      if (!item.owner_username) return;
      const entry = map.get(item.owner_username) || {
        username: item.owner_username,
        videos: []
      };
      entry.videos.push({
        id: item.video_id,
        src: item.video_url || '',
        poster: item.thumbnail_url || ''
      });
      map.set(item.owner_username, entry);
    });
    return Array.from(map.values());
  }, [feedItems]);

  const previewUrl = useMemo(
    () => buildGeneratedVideoUrl(latestGeneration?.file_path),
    [latestGeneration]
  );

  const generationLocked = useMemo(() => {
    if (pendingApproval) return true;
    if (!latestGeneration) return false;
    const status = latestGeneration.status;
    if (!status) return true;
    return status !== 'READY' && status !== 'FAILED';
  }, [latestGeneration, pendingApproval]);

  useEffect(() => {
    if (token) {
      localStorage.setItem('genvid_token', token);
    } else {
      localStorage.removeItem('genvid_token');
    }
  }, [token]);

  useEffect(() => {
    if (!notice && !error) return undefined;
    const timer = setTimeout(() => {
      setNotice('');
      setError('');
    }, 3500);
    return () => clearTimeout(timer);
  }, [notice, error]);

  useEffect(() => {
    return () => {
      if (profilePreviewRef.current) {
        URL.revokeObjectURL(profilePreviewRef.current);
      }
    };
  }, []);

  useEffect(() => {
    const map = {};
    following.forEach((profile) => {
      if (profile?.id) map[profile.id] = true;
    });
    setFollowedUsers(map);
  }, [following]);

  useEffect(() => {
    let ws;
    let reconnectTimer;
    let heartbeatTimer;
    let closed = false;

    const wsUrl = API_BASE
      ? API_BASE.replace(/^http/, 'ws') + '/ws'
      : `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws`;

    const connect = () => {
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        heartbeatTimer = setInterval(() => {
          if (ws?.readyState === WebSocket.OPEN) {
            ws.send('ping');
          }
        }, 15000);
      };

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload?.type === 'video_generation') {
            const data = payload.data || {};
            setLatestGeneration((prev) => {
              if (!prev || prev?.id === data.id) {
                return { ...prev, ...data };
              }
              return prev;
            });

            if (data.status === 'READY') {
              setPendingApproval(true);
              setMessages((prev) => [
                buildMessage('assistant', `Draft ready (id ${data.id}). Preview below. Publish now?`),
                ...prev
              ]);
            } else if (data.status === 'FAILED') {
              setPendingApproval(false);
              setMessages((prev) => [
                buildMessage('assistant', `Generation failed for id ${data.id}. Try again.`),
                ...prev
              ]);
            }
          }
        } catch {
          // ignore non-json messages
        }
      };

      ws.onclose = () => {
        if (heartbeatTimer) {
          clearInterval(heartbeatTimer);
          heartbeatTimer = null;
        }
        if (!closed) {
          reconnectTimer = setTimeout(connect, 1200);
        }
      };

      ws.onerror = () => {
        try {
          ws.close();
        } catch {
          // ignore
        }
      };
    };

    connect();

    return () => {
      closed = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (heartbeatTimer) clearInterval(heartbeatTimer);
      if (ws && ws.readyState < WebSocket.CLOSING) {
        ws.close();
      }
    };
  }, []);

  useEffect(() => {
    if (!token) {
      setUser(null);
      setFeedItems([]);
      setPostedVideos([]);
      setFollowers([]);
      setFollowing([]);
      setFollowedUsers({});
      setOwnerIdByVideo({});
      return;
    }

    loadUser(token);
    loadFeed(token);
    loadMyVideos(token);
  }, [token]);

  useEffect(() => {
    const missing = feedItems
      .filter((item) => !(item.owner_id || ownerIdByVideo[item.video_id]))
      .map((item) => item.video_id);
    if (missing.length === 0) return;

    let cancelled = false;

    const resolveOwners = async () => {
      for (const videoId of missing) {
        try {
          const data = await api.getVideo(videoId);
          if (!cancelled && data?.owner_id) {
            setOwnerIdByVideo((prev) => ({ ...prev, [videoId]: data.owner_id }));
          }
        } catch (err) {
          if (!cancelled) setError(err.message);
        }
      }
    };

    resolveOwners();

    return () => {
      cancelled = true;
    };
  }, [feedItems, ownerIdByVideo]);

  useEffect(() => {
    if (!user?.id) return;

    const fetchFollows = async () => {
      try {
        const [followersData, followingData] = await Promise.all([
          api.getFollowers(user.id),
          api.getFollowing(user.id)
        ]);
        setFollowers(followersData || []);
        setFollowing(followingData || []);
      } catch (err) {
        setError(err.message);
      }
    };

    fetchFollows();
  }, [user?.id]);

  async function loadUser(authToken) {
    try {
      const data = await api.me(authToken);
      setUser(data);
      setProfileForm({
        username: data?.username || '',
        bio: data?.bio || ''
      });
      if (!profilePicFile) {
        setProfilePicPreview(data?.profile_pic || '');
      }
    } catch (err) {
      setError(err.message);
    }
  }

  async function loadFeed(authToken) {
    if (!authToken) return;
    setFeedLoading(true);
    try {
      const data = await api.getFeed(authToken);
      const normalized = (data?.items || []).map((item) => ({
        ...item,
        likes_count: item.likes_count ?? 0,
        comments_count: item.comments_count ?? 0,
        is_liked_by_user: Boolean(item.is_liked_by_user)
      }));
      setFeedItems(normalized);
    } catch (err) {
      setError(err.message);
    } finally {
      setFeedLoading(false);
    }
  }

  async function loadMyVideos(authToken) {
    if (!authToken) return;
    try {
      const data = await api.getMyVideos(authToken);
      const mapped = (data || []).map((video) => ({
        id: video.id,
        src: video.video_url || ''
      }));
      setPostedVideos(mapped);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleAuthSubmit(event) {
    event.preventDefault();
    setAuthError('');
    setError('');
    try {
      if (authMode === 'signup') {
        const data = await api.signup({
          email: authForm.email,
          username: authForm.username,
          password: authForm.password
        });
        setToken(data.access_token);
      } else {
        const data = await api.login({
          username: authForm.username,
          password: authForm.password,
          grant_type: 'password'
        });
        setToken(data.access_token);
      }
      setNotice('Signed in successfully.');
    } catch (err) {
      setAuthError(err.message);
    }
  }

  function handleLogout() {
    setToken('');
    setUser(null);
    setProfileForm({ username: '', bio: '' });
    setProfilePicFile(null);
    setProfilePicPreview('');
    setNotice('Logged out.');
  }

  function updateAuthForm(next) {
    setAuthForm((prev) => ({ ...prev, ...next }));
  }

  function updateProfileForm(next) {
    setProfileForm((prev) => ({ ...prev, ...next }));
  }

  function handleProfileFileSelect(file) {
    if (!file) return;
    if (profilePreviewRef.current) {
      URL.revokeObjectURL(profilePreviewRef.current);
    }
    const previewUrl = URL.createObjectURL(file);
    profilePreviewRef.current = previewUrl;
    setProfilePicPreview(previewUrl);
    setProfilePicFile(file);
  }

  async function handleProfileSave() {
    if (!token) return;
    setProfileSaving(true);
    try {
      const payload = {
        username: profileForm.username || null,
        bio: profileForm.bio || null
      };
      const data = await api.updateMe(token, payload);
      setUser(data);
      setProfileForm({
        username: data?.username || '',
        bio: data?.bio || ''
      });
      setNotice('Profile updated.');
    } catch (err) {
      setError(err.message);
    } finally {
      setProfileSaving(false);
    }
  }

  async function handleProfileUpload() {
    if (!token || !profilePicFile) return;
    setProfileUploading(true);
    try {
      const data = await uploadProfilePic(token, profilePicFile);
      setUser(data);
      setProfilePicFile(null);
      if (profilePreviewRef.current) {
        URL.revokeObjectURL(profilePreviewRef.current);
        profilePreviewRef.current = null;
      }
      setProfilePicPreview(data?.profile_pic || '');
      setNotice('Profile photo updated.');
    } catch (err) {
      setError(err.message);
    } finally {
      setProfileUploading(false);
    }
  }

  function updateDraft(videoId, value) {
    setCommentDrafts((prev) => ({ ...prev, [videoId]: value }));
  }

  function toggleReplyTarget(videoId, commentId) {
    setReplyTargets((prev) => ({ ...prev, [videoId]: commentId }));
  }

  async function toggleLike(videoId) {
    if (!token) {
      setError('Sign in to like videos.');
      return;
    }
    const item = feedItems.find((entry) => entry.video_id === videoId);
    if (!item) return;
    const liked = Boolean(item.is_liked_by_user);

    setFeedItems((prev) =>
      prev.map((entry) =>
        entry.video_id === videoId
          ? {
              ...entry,
              is_liked_by_user: !liked,
              likes_count: Math.max(0, (entry.likes_count ?? 0) + (liked ? -1 : 1))
            }
          : entry
      )
    );

    try {
      if (liked) {
        await api.unlikeVideo(token, videoId);
      } else {
        await api.likeVideo(token, videoId);
      }
    } catch (err) {
      setError(err.message);
      loadFeed(token);
    }
  }

  async function toggleComments(videoId) {
    setOpenCommentsId((prev) => (prev === videoId ? null : videoId));
    if (!commentsByVideo[videoId]) {
      await loadComments(videoId);
    }
  }

  function normalizeComment(comment, index) {
    return {
      id: comment.id || comment.comment_id || `${comment.created_at || 'comment'}-${index}`,
      text: comment.content || comment.comment_text || '',
      parentId: comment.parent_comment_id || null
    };
  }

  async function loadComments(videoId) {
    try {
      const data = await api.getComments(videoId);
      const normalized = (data || []).map(normalizeComment);
      const tree = buildCommentTree(normalized);
      setCommentsByVideo((prev) => ({ ...prev, [videoId]: tree }));
    } catch (err) {
      setError(err.message);
    }
  }

  async function submitComment(videoId) {
    if (!token) {
      setError('Sign in to comment.');
      return;
    }
    const text = (commentDrafts[videoId] || '').trim();
    if (!text) return;

    const parentId = replyTargets[videoId] || null;
    try {
      const response = await api.postComment(token, videoId, {
        video_id: videoId,
        comment_text: text,
        parent_comment_id: parentId
      });
      const normalized = normalizeComment(response || {}, Date.now());
      setCommentsByVideo((prev) => ({
        ...prev,
        [videoId]: addNestedComment(prev[videoId] || [], parentId, normalized)
      }));
      setCommentDrafts((prev) => ({ ...prev, [videoId]: '' }));
      setReplyTargets((prev) => ({ ...prev, [videoId]: null }));
      setFeedItems((prev) =>
        prev.map((entry) =>
          entry.video_id === videoId
            ? { ...entry, comments_count: (entry.comments_count || 0) + 1 }
            : entry
        )
      );
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleGenerate() {
    if (generationLocked) return;
    const trimmed = prompt.trim();
    if (!trimmed) return;

    setMessages((prev) => [buildMessage('user', trimmed), ...prev]);
    setPrompt('');

    if (!token) {
      setMessages((prev) => [
        buildMessage('assistant', 'Sign in to start a generation.'),
        ...prev
      ]);
      return;
    }

    try {
      const generation = await api.createVideo(token, { prompt: trimmed });
      setLatestGeneration(generation);
      setPendingApproval(false);
      setMessages((prev) => [
        buildMessage('assistant', `Draft queued (id ${generation.id}). I'll notify you when it is ready.`),
        ...prev
      ]);
    } catch (err) {
      setMessages((prev) => [
        buildMessage('assistant', `Error: ${err.message}`),
        ...prev
      ]);
    }
  }

  async function handleApprove(approved) {
    if (!pendingApproval) return;
    setPendingApproval(false);

    if (!approved) {
      setMessages((prev) => [
        buildMessage('assistant', 'No worries, saved as a draft.'),
        ...prev
      ]);
      return;
    }

    if (!token) {
      setMessages((prev) => [
        buildMessage('assistant', 'Sign in to publish videos.'),
        ...prev
      ]);
      return;
    }

    if (!latestGeneration?.id) {
      setMessages((prev) => [
        buildMessage('assistant', 'No generation available to publish.'),
        ...prev
      ]);
      return;
    }

    try {
      const video = await api.publishVideo(token, latestGeneration.id);
      setPostedVideos((prev) => [{ id: video.id, src: video.video_url || '' }, ...prev]);
      setMessages((prev) => [
        buildMessage('assistant', 'Posting now. Your reel is live.'),
        ...prev
      ]);
      setPendingApproval(false);
      loadFeed(token);
    } catch (err) {
      setMessages((prev) => [
        buildMessage('assistant', `Publish failed: ${err.message}`),
        ...prev
      ]);
    }
  }

  const loadFollowers = useCallback(async () => {
    if (!user?.id) return;
    try {
      const data = await api.getFollowers(user.id);
      setFollowers(data || []);
    } catch (err) {
      setError(err.message);
    }
  }, [user?.id]);

  const loadFollowing = useCallback(async () => {
    if (!user?.id) return;
    try {
      const data = await api.getFollowing(user.id);
      setFollowing(data || []);
    } catch (err) {
      setError(err.message);
    }
  }, [user?.id]);

  useEffect(() => {
    if (!isAuthed || activeTab !== 'profile') return;
    loadFollowers();
    loadFollowing();
  }, [activeTab, isAuthed, loadFollowers, loadFollowing]);

  const resolveOwnerId = useCallback(async (videoId, fallbackOwnerId) => {
    if (fallbackOwnerId) return fallbackOwnerId;
    if (ownerIdByVideo[videoId]) return ownerIdByVideo[videoId];
    try {
      const data = await api.getVideo(videoId);
      if (data?.owner_id) {
        setOwnerIdByVideo((prev) => ({ ...prev, [videoId]: data.owner_id }));
        return data.owner_id;
      }
    } catch (err) {
      setError(err.message);
    }
    return null;
  }, [ownerIdByVideo]);

  const handleFollowFromFeed = useCallback(async (video) => {
    if (!token) {
      setError('Sign in to follow creators.');
      return;
    }

    const ownerId = await resolveOwnerId(video.id, video.ownerId);
    if (!ownerId) {
      setError('Unable to resolve creator.');
      return;
    }

    if (user?.id && ownerId === user.id) {
      setNotice('You cannot follow yourself.');
      return;
    }

    const isFollowing = Boolean(followedUsers[ownerId]);
    try {
      if (isFollowing) {
        await api.unfollowUser(token, ownerId);
        setFollowing((prev) => prev.filter((profile) => profile.id !== ownerId));
      } else {
        await api.followUser(token, ownerId);
        const username = video.ownerUsername || video.userId?.replace('@', '') || `user-${ownerId}`;
        setFollowing((prev) =>
          prev.some((profile) => profile.id === ownerId)
            ? prev
            : [...prev, { id: ownerId, username }]
        );
      }
      setFollowedUsers((prev) => ({ ...prev, [ownerId]: !isFollowing }));
      setNotice(isFollowing ? 'Unfollowed.' : 'Following.');
    } catch (err) {
      setError(err.message);
    }
  }, [token, user?.id, followedUsers, resolveOwnerId]);

  return (
    <div className="app">
      <Topbar isAuthed={isAuthed} onLogout={handleLogout} />

      {activeTab === 'feed' && (
        <FeedView
          videos={feedVideos}
          openCommentsId={openCommentsId}
          commentDrafts={commentDrafts}
          replyTargets={replyTargets}
          onToggleLike={toggleLike}
          onToggleComments={toggleComments}
          onToggleReply={toggleReplyTarget}
          onDraftChange={updateDraft}
          onSubmitComment={submitComment}
          onFollow={handleFollowFromFeed}
          isAuthed={isAuthed}
        />
      )}

      {activeTab === 'create' && (
        <CreateView
          messages={messages}
          prompt={prompt}
          pendingApproval={pendingApproval}
          previewUrl={previewUrl}
          generationId={latestGeneration?.id}
          generationStatus={latestGeneration?.status}
          isLocked={generationLocked}
          isAuthed={isAuthed}
          onPromptChange={setPrompt}
          onGenerate={handleGenerate}
          onApprove={handleApprove}
        />
      )}

      {activeTab === 'profile' && (
        <ProfileView
          isAuthed={isAuthed}
          user={user}
          postedVideos={postedVideos}
          followers={followers}
          following={following}
          creatorIndex={creatorIndex}
          profileForm={profileForm}
          profilePicPreview={profilePicPreview}
          profileSaving={profileSaving}
          profileUploading={profileUploading}
          onFetchFollowers={loadFollowers}
          onFetchFollowing={loadFollowing}
          onProfileChange={updateProfileForm}
          onProfileSave={handleProfileSave}
          onProfileFileSelect={handleProfileFileSelect}
          onProfileUpload={handleProfileUpload}
          authMode={authMode}
          onAuthModeChange={setAuthMode}
          authForm={authForm}
          onAuthChange={updateAuthForm}
          onAuthSubmit={handleAuthSubmit}
          googleUrl={googleLoginUrl()}
          authError={authError}
        />
      )}

      <BottomNav activeTab={activeTab} onChange={setActiveTab} />

      {(error || notice || (feedLoading && isAuthed)) && (
        <div className={`status-toast ${error ? 'error' : ''}`}>
          {error || (feedLoading ? 'Refreshing feed...' : notice)}
        </div>
      )}
    </div>
  );
}

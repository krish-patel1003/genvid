import React, { useCallback, useEffect, useMemo, useState } from 'react';
import BottomNav from './components/BottomNav.jsx';
import Topbar from './components/Topbar.jsx';
import FeedView from './views/FeedView.jsx';
import CreateView from './views/CreateView.jsx';
import ProfileView from './views/ProfileView.jsx';
import { api, googleLoginUrl } from './services/api.js';
import { addNestedComment, buildCommentTree } from './utils/comments.js';

const buildMessage = (role, text) => ({
  id: `${role}-${Date.now()}-${Math.random()}`,
  role,
  text
});

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000';

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

  const feedVideos = useMemo(() =>
    feedItems.map((item) => ({
      id: item.video_id,
      ownerId: item.owner_id ?? ownerIdByVideo[item.video_id],
      userId: item.owner_username ? `@${item.owner_username}` : '@creator',
      caption: item.caption,
      src: item.video_url || '',
      poster: item.thumbnail_url || '',
      likes: item.likes_count ?? 0,
      liked: item.is_liked_by_user ?? false,
      comments_count: item.comments_count ?? 0,
      comments: commentsByVideo[item.video_id] || []
    })),
  [feedItems, commentsByVideo, ownerIdByVideo]);

  const previewUrl = useMemo(
    () => buildGeneratedVideoUrl(latestGeneration?.file_path),
    [latestGeneration]
  );

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
    const wsUrl = API_BASE
      ? API_BASE.replace(/^http/, 'ws') + '/ws'
      : `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws`;

    const ws = new WebSocket(wsUrl);

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

    ws.onerror = () => {
      ws.close();
    };

    return () => ws.close();
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

  async function loadUser(authToken) {
    try {
      const data = await api.me(authToken);
      setUser(data);
    } catch (err) {
      setError(err.message);
    }
  }

  async function loadFeed(authToken) {
    if (!authToken) return;
    setFeedLoading(true);
    try {
      const data = await api.getFeed(authToken);
      setFeedItems(data?.items || []);
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
    setNotice('Logged out.');
  }

  function updateAuthForm(next) {
    setAuthForm((prev) => ({ ...prev, ...next }));
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
    const liked = item.is_liked_by_user;

    setFeedItems((prev) =>
      prev.map((entry) =>
        entry.video_id === videoId
          ? {
              ...entry,
              is_liked_by_user: !liked,
              likes_count: Math.max(0, (entry.likes_count || 0) + (liked ? -1 : 1))
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
      } else {
        await api.followUser(token, ownerId);
      }
      setFollowedUsers((prev) => ({ ...prev, [ownerId]: !isFollowing }));
      setNotice(isFollowing ? 'Unfollowed.' : 'Following.');
    } catch (err) {
      setError(err.message);
    }
  }, [token, user?.id, followedUsers, resolveOwnerId]);

  return (
    <div className="app">
      <Topbar />

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
          followedUsers={followedUsers}
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
          onFetchFollowers={loadFollowers}
          onFetchFollowing={loadFollowing}
          onLogout={handleLogout}
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

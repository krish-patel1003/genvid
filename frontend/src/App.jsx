import React, { useCallback, useEffect, useMemo, useState } from 'react';
import BottomNav from './components/BottomNav.jsx';
import Topbar from './components/Topbar.jsx';
import FeedView from './views/FeedView.jsx';
import CreateView from './views/CreateView.jsx';
import ProfileView from './views/ProfileView.jsx';
import { api, googleLoginUrl } from './services/api.js';

const STATUS_POLL_MS = 5000;

const maskToken = (value) => {
  if (!value) return '';
  if (value.length <= 10) return value;
  return `${value.slice(0, 6)}...${value.slice(-4)}`;
};

export default function App() {
  const [activeTab, setActiveTab] = useState('library');
  const [token, setToken] = useState(() => localStorage.getItem('genvid_token') || '');
  const [accountInfo, setAccountInfo] = useState(() => {
    const raw = localStorage.getItem('genvid_account');
    if (!raw) return { username: '', email: '' };
    try {
      return JSON.parse(raw);
    } catch {
      return { username: '', email: '' };
    }
  });
  const [authMode, setAuthMode] = useState('login');
  const [authForm, setAuthForm] = useState({ email: '', username: '', password: '' });
  const [authError, setAuthError] = useState('');

  const [prompt, setPrompt] = useState('');
  const [generations, setGenerations] = useState([]);
  const [latestGenerationId, setLatestGenerationId] = useState(null);
  const [previewById, setPreviewById] = useState({});
  const [loadingGenerations, setLoadingGenerations] = useState(false);
  const [creating, setCreating] = useState(false);

  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');

  const isAuthed = useMemo(() => Boolean(token), [token]);
  const latestGeneration = useMemo(
    () => generations.find((item) => item.id === latestGenerationId) || null,
    [generations, latestGenerationId]
  );
  const latestPreview = useMemo(
    () => (latestGeneration ? previewById[latestGeneration.id] : null),
    [latestGeneration, previewById]
  );
  const maskedToken = useMemo(() => maskToken(token), [token]);

  const upsertGeneration = useCallback((generation) => {
    if (!generation?.id) return;
    setGenerations((prev) => {
      const index = prev.findIndex((item) => item.id === generation.id);
      if (index === -1) {
        return [generation, ...prev];
      }
      const next = [...prev];
      next[index] = { ...next[index], ...generation };
      return next;
    });
  }, []);

  const loadGenerations = useCallback(async (authToken) => {
    if (!authToken) return;
    setLoadingGenerations(true);
    try {
      const data = await api.listGenerations(authToken);
      const sorted = [...(data || [])].sort((a, b) => {
        const aTime = new Date(a.created_at || 0).getTime();
        const bTime = new Date(b.created_at || 0).getTime();
        return bTime - aTime;
      });
      setGenerations(sorted);
      setLatestGenerationId((prev) => {
        if (prev && sorted.some((item) => item.id === prev)) return prev;
        return sorted[0]?.id ?? null;
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingGenerations(false);
    }
  }, []);

  useEffect(() => {
    if (token) {
      localStorage.setItem('genvid_token', token);
    } else {
      localStorage.removeItem('genvid_token');
    }
  }, [token]);

  useEffect(() => {
    localStorage.setItem('genvid_account', JSON.stringify(accountInfo));
  }, [accountInfo]);

  useEffect(() => {
    if (!notice && !error) return undefined;
    const timer = setTimeout(() => {
      setNotice('');
      setError('');
    }, 3500);
    return () => clearTimeout(timer);
  }, [notice, error]);

  useEffect(() => {
    if (!token) {
      setGenerations([]);
      setLatestGenerationId(null);
      setPreviewById({});
      return;
    }
    loadGenerations(token);
  }, [token, loadGenerations]);

  useEffect(() => {
    if (!token || !latestGeneration) return undefined;
    const status = latestGeneration.status;
    if (status !== 'QUEUED' && status !== 'RUNNING') return undefined;

    let cancelled = false;
    const interval = setInterval(async () => {
      try {
        const data = await api.getGeneration(token, latestGeneration.id);
        if (!cancelled) {
          upsertGeneration(data);
        }
      } catch (err) {
        if (!cancelled) setError(err.message);
      }
    }, STATUS_POLL_MS);

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [token, latestGeneration, upsertGeneration]);

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
        setAccountInfo({ username: authForm.username, email: authForm.email });
      } else {
        const data = await api.login({
          username: authForm.username,
          password: authForm.password,
          grant_type: 'password'
        });
        setToken(data.access_token);
        setAccountInfo((prev) => ({ ...prev, username: authForm.username }));
      }
      setNotice('Signed in successfully.');
    } catch (err) {
      setAuthError(err.message);
    }
  }

  function handleLogout() {
    setToken('');
    setAccountInfo({ username: '', email: '' });
    setNotice('Logged out.');
  }

  function updateAuthForm(next) {
    setAuthForm((prev) => ({ ...prev, ...next }));
  }

  async function handleGenerate() {
    if (!token) {
      setError('Sign in to generate videos.');
      return;
    }

    const trimmed = prompt.trim();
    if (!trimmed) return;

    setCreating(true);
    try {
      const generation = await api.createGeneration(token, { prompt: trimmed });
      upsertGeneration(generation);
      setLatestGenerationId(generation.id);
      setPrompt('');
      setNotice(`Generation queued (#${generation.id}).`);
    } catch (err) {
      setError(err.message);
    } finally {
      setCreating(false);
    }
  }

  const handleRefreshGeneration = useCallback(async (jobId) => {
    if (!token) return;
    try {
      const data = await api.getGeneration(token, jobId);
      upsertGeneration(data);
    } catch (err) {
      setError(err.message);
    }
  }, [token, upsertGeneration]);

  const handleFetchPreview = useCallback(async (jobId) => {
    if (!token) return;
    try {
      const data = await api.getPreviewUrls(token, jobId);
      setPreviewById((prev) => ({ ...prev, [jobId]: data }));
    } catch (err) {
      setError(err.message);
    }
  }, [token]);

  useEffect(() => {
    if (!token || !latestGeneration) return;
    if (latestGeneration.status !== 'SUCCEEDED') return;
    if (previewById[latestGeneration.id]) return;
    handleFetchPreview(latestGeneration.id);
  }, [token, latestGeneration, previewById, handleFetchPreview]);

  const handlePublishGeneration = useCallback(async (jobId) => {
    if (!token) return;
    try {
      const data = await api.publishGeneration(token, jobId);
      const message = data?.video_id
        ? `Published video #${data.video_id}.`
        : 'Published generation.';
      setNotice(message);
      loadGenerations(token);
    } catch (err) {
      setError(err.message);
    }
  }, [token, loadGenerations]);

  const handleCopyToken = useCallback(async () => {
    if (!token) return;
    try {
      await navigator.clipboard.writeText(token);
      setNotice('Access token copied.');
    } catch {
      setError('Unable to copy token.');
    }
  }, [token]);

  return (
    <div className="app">
      <Topbar isAuthed={isAuthed} onLogout={handleLogout} />

      {activeTab === 'library' && (
        <FeedView
          generations={generations}
          previews={previewById}
          isAuthed={isAuthed}
          isLoading={loadingGenerations}
          onReload={() => loadGenerations(token)}
          onRefresh={handleRefreshGeneration}
          onPreview={handleFetchPreview}
          onPublish={handlePublishGeneration}
        />
      )}

      {activeTab === 'create' && (
        <CreateView
          prompt={prompt}
          isAuthed={isAuthed}
          isSubmitting={creating}
          latestGeneration={latestGeneration}
          preview={latestPreview}
          onPromptChange={setPrompt}
          onGenerate={handleGenerate}
          onRefresh={handleRefreshGeneration}
          onFetchPreview={handleFetchPreview}
          onPublish={handlePublishGeneration}
        />
      )}

      {activeTab === 'account' && (
        <ProfileView
          isAuthed={isAuthed}
          authMode={authMode}
          onAuthModeChange={setAuthMode}
          authForm={authForm}
          onAuthChange={updateAuthForm}
          onAuthSubmit={handleAuthSubmit}
          authError={authError}
          googleUrl={googleLoginUrl()}
          accountInfo={accountInfo}
          maskedToken={maskedToken}
          onCopyToken={handleCopyToken}
          onLogout={handleLogout}
        />
      )}

      <BottomNav activeTab={activeTab} onChange={setActiveTab} />

      {(error || notice || (loadingGenerations && isAuthed)) && (
        <div className={`status-toast ${error ? 'error' : ''}`}>
          {error || (loadingGenerations ? 'Refreshing generations...' : notice)}
        </div>
      )}
    </div>
  );
}

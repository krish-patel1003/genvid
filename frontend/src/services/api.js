const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export async function apiRequest(path, options = {}) {
  const {
    method = "GET",
    token,
    body,
    form
  } = options;

  const headers = {};
  let payload;

  if (form) {
    headers["Content-Type"] = "application/x-www-form-urlencoded";
    payload = new URLSearchParams(form).toString();
  } else if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: payload
  });

  if (response.status === 204) {
    return null;
  }

  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail = typeof data === "string" ? data : data?.detail;
    throw new Error(detail || `Request failed (${response.status})`);
  }

  return data;
}

export const api = {
  signup: (payload) => apiRequest("/auth/signup", { method: "POST", body: payload }),
  login: (payload) => apiRequest("/auth/token", { method: "POST", form: payload }),
  me: (token) => apiRequest("/users/me", { token }),
  updateMe: (token, payload) => apiRequest("/users/me", { method: "PATCH", token, body: payload }),
  createVideo: (token, payload) => apiRequest("/videos/create", { method: "POST", token, body: payload }),
  publishVideo: (token, generationId) => apiRequest(`/videos/generation/${generationId}/publish`, { method: "POST", token }),
  getVideo: (videoId) => apiRequest(`/videos/${videoId}`),
  deleteVideo: (token, videoId) => apiRequest(`/videos/${videoId}`, { method: "DELETE", token }),
  getMyVideos: (token) => apiRequest("/videos/user/videos", { token }),
  getFeed: (token) => apiRequest("/feed/", { token }),
  likeVideo: (token, videoId) => apiRequest(`/interactions/${videoId}/like`, { method: "POST", token }),
  unlikeVideo: (token, videoId) => apiRequest(`/interactions/${videoId}/like`, { method: "DELETE", token }),
  postComment: (token, videoId, payload) => apiRequest(`/interactions/${videoId}/comment`, { method: "POST", token, body: payload }),
  getComments: (videoId) => apiRequest(`/interactions/${videoId}/comments`),
  deleteComment: (token, commentId) => apiRequest(`/interactions/comment/${commentId}`, { method: "DELETE", token }),
  followUser: (token, userId) => apiRequest(`/users/${userId}/follow`, { method: "POST", token }),
  unfollowUser: (token, userId) => apiRequest(`/users/${userId}/follow`, { method: "DELETE", token }),
  getFollowers: (userId) => apiRequest(`/users/${userId}/followers`),
  getFollowing: (userId) => apiRequest(`/users/${userId}/following`)
};

export function googleLoginUrl() {
  return `${API_BASE}/auth/google/login`;
}

export async function uploadProfilePic(token, file) {
  const formData = new FormData();
  formData.append("file", file);

  const headers = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}/users/me/profile-pic`, {
    method: "POST",
    headers,
    body: formData
  });

  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail = typeof data === "string" ? data : data?.detail;
    throw new Error(detail || `Request failed (${response.status})`);
  }

  return data;
}

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
  listGenerations: (token) => apiRequest("/videos/", { token }),
  createGeneration: (token, payload) => apiRequest("/videos/", { method: "POST", token, body: payload }),
  getGeneration: (token, jobId) => apiRequest(`/videos/${jobId}`, { token }),
  publishGeneration: (token, jobId) => apiRequest(`/videos/${jobId}/publish`, { method: "POST", token }),
  getPreviewUrls: (token, jobId) => apiRequest(`/videos/${jobId}/preview-urls`, { token })
};

export function googleLoginUrl() {
  return `${API_BASE}/auth/google/login`;
}

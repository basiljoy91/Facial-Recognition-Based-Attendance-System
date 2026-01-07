const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Small helper to call the backend API with proper headers and error handling.
 */
export async function apiFetch(path, { method = "GET", token, body, headers } = {}) {
  const url = `${API_BASE}${path}`;
  const finalHeaders = new Headers(headers || {});

  // Don't set Content-Type for FormData - browser will set it with boundary
  const isFormData = body instanceof FormData;
  
  if (token) {
    finalHeaders.set("Authorization", `Bearer ${token}`);
  }

  // For FormData, only send Authorization header, let browser set Content-Type
  if (isFormData) {
    finalHeaders.delete("Content-Type");
  }

  const res = await fetch(url, {
    method,
    headers: finalHeaders,
    body,
  });

  let data;
  try {
    data = await res.json();
  } catch {
    data = null;
  }

  if (!res.ok) {
    const message =
      (data && (data.detail || data.message)) ||
      `Request failed with status ${res.status}`;
    throw new Error(message);
  }

  return data;
}

export { API_BASE };



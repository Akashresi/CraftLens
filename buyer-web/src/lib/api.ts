const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

interface RequestOptions extends RequestInit {
  token?: string | null;
}

export interface ApiEnvelope<T = unknown> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export async function apiRequest<T = any>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<ApiEnvelope<T>> {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = new Headers(options.headers || {});

  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const token =
    options.token ||
    (typeof window !== "undefined" ? localStorage.getItem("craftlens_token") : null);

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    const data = await response.json();
    if (!response.ok) {
      return {
        success: false,
        error: data.detail || data.message || "An error occurred with the request",
      };
    }

    return data as ApiEnvelope<T>;
  } catch (err: unknown) {
    return {
      success: false,
      error: err instanceof Error ? err.message : "Network connectivity failure",
    };
  }
}

async function requestUnwrapped<T = any>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const res = await apiRequest<T>(endpoint, options);
  if (!res.success) {
    throw new Error(res.error || "API request failed");
  }
  return (res.data as T) ?? ({} as T);
}

export const api = {
  get: <T = any>(endpoint: string, options: RequestOptions = {}) =>
    requestUnwrapped<T>(endpoint, { ...options, method: "GET" }),
  post: <T = any>(endpoint: string, body?: unknown, options: RequestOptions = {}) =>
    requestUnwrapped<T>(endpoint, {
      ...options,
      method: "POST",
      body: body instanceof FormData ? body : JSON.stringify(body ?? {}),
    }),
  put: <T = any>(endpoint: string, body?: unknown, options: RequestOptions = {}) =>
    requestUnwrapped<T>(endpoint, {
      ...options,
      method: "PUT",
      body: body instanceof FormData ? body : JSON.stringify(body ?? {}),
    }),
  delete: <T = any>(endpoint: string, options: RequestOptions = {}) =>
    requestUnwrapped<T>(endpoint, { ...options, method: "DELETE" }),
};

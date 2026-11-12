/**
 * Centralized API client for CraftLens mobile application.
 */

const envApiUrl = (
  globalThis as unknown as { process?: { env?: Record<string, string | undefined> } }
)?.process?.env?.EXPO_PUBLIC_API_URL;

export const API_BASE_URL = envApiUrl || "http://127.0.0.1:8000/api/v1";

export async function apiFetch<T = unknown>(
  path: string,
  options: RequestInit & { token?: string | null; idempotencyKey?: string } = {}
): Promise<{ ok: boolean; status: number; data: T | null; error?: string }> {
  const { token, idempotencyKey, headers = {}, ...rest } = options;
  const mergedHeaders: Record<string, string> = {
    ...(headers as Record<string, string>),
  };
  if (token) {
    mergedHeaders.Authorization = `Bearer ${token}`;
  }
  if (idempotencyKey) {
    mergedHeaders["X-Idempotency-Key"] = idempotencyKey;
  }

  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...rest,
    headers: mergedHeaders,
  });

  const payload = await res.json().catch(() => null);
  if (!res.ok) {
    const errMsg =
      (payload && (payload.detail || payload.message)) || `HTTP ${res.status}`;
    return { ok: false, status: res.status, data: null, error: String(errMsg) };
  }
  return {
    ok: true,
    status: res.status,
    data: payload && typeof payload === "object" && "data" in payload ? (payload.data as T) : (payload as T),
  };
}

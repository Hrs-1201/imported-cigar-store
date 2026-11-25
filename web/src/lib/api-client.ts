import { clearSession, getAccessToken, setSession } from "@/lib/auth";
import type { TokenResponse, UserPublic } from "@/types/api";

export class ApiRequestError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
  }
}

type RequestOptions = {
  method?: string;
  body?: unknown;
  auth?: boolean;
  retry?: boolean;
};

const REFRESH_EXEMPT = ["/auth/login", "/auth/register", "/auth/refresh", "/auth/logout"];

let refreshInFlight: Promise<boolean> | null = null;

export function apiBaseUrl(): string {
  const configured = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api/v1";
  return configured.replace(/\/$/, "");
}

function redirectToLogin(): void {
  if (typeof window === "undefined") return;
  const path = window.location.pathname;
  if (path.startsWith("/login") || path.startsWith("/register")) return;
  const next = `${path}${window.location.search}`;
  const target = safeRelative(next) ? `/login?next=${encodeURIComponent(next)}` : "/login";
  window.location.assign(target);
}

function safeRelative(value: string): boolean {
  return value.startsWith("/") && !value.startsWith("//") && !value.startsWith("/\\");
}

function firstDetail(data: unknown, fallback: string): string {
  if (!data || typeof data !== "object") return fallback;
  const detail = (data as { detail?: unknown }).detail;
  if (typeof detail === "string" && detail.trim()) return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0] as { msg?: unknown };
    if (first && typeof first.msg === "string" && first.msg.trim()) return first.msg;
  }
  return fallback;
}

async function readError(response: Response): Promise<string> {
  try {
    return firstDetail(await response.json(), response.statusText || "Request failed");
  } catch {
    return response.statusText || "Request failed";
  }
}

async function performRefresh(): Promise<boolean> {
  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl()}/auth/refresh`, {
      method: "POST",
      credentials: "include",
      cache: "no-store",
    });
  } catch {
    clearSession();
    return false;
  }
  if (!response.ok) {
    clearSession();
    return false;
  }
  const body = (await response.json()) as TokenResponse;
  setSession(body.access_token, body.user);
  return true;
}

export function refreshSession(): Promise<boolean> {
  if (!refreshInFlight) {
    refreshInFlight = performRefresh().finally(() => {
      refreshInFlight = null;
    });
  }
  return refreshInFlight;
}

function shouldRefresh(path: string, options: RequestOptions): boolean {
  if (options.auth === false || options.retry === false) return false;
  return !REFRESH_EXEMPT.some((prefix) => path.startsWith(prefix));
}

export async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers();
  if (options.body !== undefined) {
    headers.set("Content-Type", "application/json");
  }
  if (options.auth !== false) {
    const accessToken = getAccessToken();
    if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
  }

  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl()}${path}`, {
      method: options.method ?? "GET",
      headers,
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
      credentials: "include",
      cache: "no-store",
    });
  } catch {
    throw new ApiRequestError(0, "Could not reach the API. Is it running?");
  }

  if (response.status === 401 && shouldRefresh(path, options)) {
    const refreshed = await refreshSession();
    if (refreshed) {
      return apiFetch<T>(path, { ...options, retry: false });
    }
    clearSession();
    redirectToLogin();
    throw new ApiRequestError(401, "Session expired");
  }

  if (response.status === 401 && options.auth !== false && options.retry === false) {
    clearSession();
    redirectToLogin();
    throw new ApiRequestError(401, "Session expired");
  }

  if (response.status === 204) {
    return undefined as T;
  }

  if (!response.ok) {
    throw new ApiRequestError(response.status, await readError(response));
  }

  return (await response.json()) as T;
}

export async function logoutRequest(): Promise<void> {
  try {
    await fetch(`${apiBaseUrl()}/auth/logout`, {
      method: "POST",
      credentials: "include",
      cache: "no-store",
    });
  } catch {
    // The local session is cleared either way.
  } finally {
    clearSession();
  }
}

export type { UserPublic };

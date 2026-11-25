import type { UserPublic } from "@/types/api";

let accessToken: string | null = null;
let currentUser: UserPublic | null = null;
const listeners = new Set<() => void>();

function emit(): void {
  listeners.forEach((listener) => listener());
}

export function getAccessToken(): string | null {
  return accessToken;
}

export function getCurrentUser(): UserPublic | null {
  return currentUser;
}

export function setSession(token: string, user: UserPublic): void {
  accessToken = token;
  currentUser = user;
  emit();
}

export function clearSession(): void {
  accessToken = null;
  currentUser = null;
  emit();
}

export function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

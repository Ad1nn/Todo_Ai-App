/**
 * Authentication utilities for frontend.
 */

import type { User, AuthToken, UserCreate, UserLogin, UserUpdate, UserStats } from './types';
import { api } from './api';

const TOKEN_KEY = 'token';

/**
 * Store authentication token in localStorage.
 */
export function setToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(TOKEN_KEY, token);
  }
}

/**
 * Get authentication token from localStorage.
 */
export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Remove authentication token from localStorage.
 */
export function removeToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(TOKEN_KEY);
  }
}

/**
 * Check if user is authenticated (has token).
 */
export function isAuthenticated(): boolean {
  return getToken() !== null;
}

/**
 * Register a new user.
 */
export async function register(data: UserCreate): Promise<User> {
  return api.post<User>('/api/v1/auth/register', data, false);
}

/**
 * Login user and store token.
 */
export async function login(data: UserLogin): Promise<AuthToken> {
  const response = await api.post<AuthToken>('/api/v1/auth/login', data, false);
  setToken(response.access_token);
  return response;
}

/**
 * Logout user and remove token.
 */
export async function logout(): Promise<void> {
  try {
    await api.post('/api/v1/auth/logout');
  } finally {
    removeToken();
  }
}

/**
 * Get current user information.
 */
export async function getCurrentUser(): Promise<User> {
  return api.get<User>('/api/v1/auth/me');
}

/**
 * Update current user's profile.
 */
export async function updateProfile(data: UserUpdate): Promise<User> {
  return api.patch<User>('/api/v1/auth/me', data);
}

/**
 * Get current user's task statistics.
 */
export async function getUserStats(): Promise<UserStats> {
  return api.get<UserStats>('/api/v1/auth/me/stats');
}

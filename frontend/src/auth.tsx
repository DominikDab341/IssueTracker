import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { ApiError, request } from './api';
import type { User } from './types';

interface Auth {
  user: User | null; message: string;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  api: <T>(path: string, options?: RequestInit) => Promise<T>;
}
const Context = createContext<Auth | null>(null);
export function AuthProvider({ children }: { children: ReactNode }) {
  // Session credentials intentionally live only in memory.
  const [session, setSession] = useState<{ token: string; user: User; expires: number } | null>(null);
  const current = useRef(session);
  current.current = session;
  const [message, setMessage] = useState('');
  const expire = useCallback((message: string) => { current.current = null; setSession(null); setMessage(message); }, []);
  const logout = useCallback(() => expire('Wylogowano. Możesz zalogować się ponownie.'), [expire]);
  useEffect(() => {
    if (!session) return;
    const timer = setTimeout(() => expire('Sesja wygasła. Zaloguj się ponownie.'), Math.max(0, session.expires - Date.now()));
    return () => clearTimeout(timer);
  }, [session, expire]);
  const login = useCallback(async (email: string, password: string) => {
    const result = await request<{ access_token: string; expires_in: number }>('/auth/token', {
      method: 'POST', body: new URLSearchParams({ username: email, password }),
    });
    const user = await request<User>('/users/me', {}, result.access_token);
    setMessage('');
    setSession({ token: result.access_token, user, expires: Date.now() + result.expires_in * 1000 });
  }, []);
  const api = useCallback(async <T,>(path: string, options: RequestInit = {}) => {
    const snapshot = current.current;
    if (!snapshot) throw new ApiError(401, 'Zaloguj się ponownie.');
    try { return await request<T>(path, options, snapshot.token); }
    catch (error) {
      if (current.current?.token === snapshot.token && error instanceof ApiError && error.status === 401) expire('Sesja wygasła. Zaloguj się ponownie.');
      throw error;
    }
  }, [expire]);
  // Refresh permissions after focus/navigation and periodically, including role changes and deactivation.
  useEffect(() => {
    if (!session) return;
    const controller = new AbortController();
    const refresh = () => request<User>('/users/me', { signal: controller.signal }, session.token).then(user => {
      setSession(previous => previous?.token === session.token ? { ...previous, user } : previous);
    }).catch(error => {
      if (!controller.signal.aborted && error instanceof ApiError && [401, 403].includes(error.status)) expire(error.message);
    });
    const timer = setInterval(refresh, 30000);
    window.addEventListener('focus', refresh);
    return () => { controller.abort(); clearInterval(timer); window.removeEventListener('focus', refresh); };
  }, [session?.token, expire]);
  const value = useMemo(() => ({ user: session?.user ?? null, message, login, logout, api }), [session, message, login, logout, api]);
  return <Context.Provider value={value}>{children}</Context.Provider>;
}
export function useAuth() { return useContext(Context)!; }

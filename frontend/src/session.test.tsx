import { act, cleanup, renderHook } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { AuthProvider, useAuth } from './auth';

afterEach(() => { cleanup(); vi.useRealTimers(); vi.unstubAllGlobals(); });
it('keeps credentials in memory and expires the session', async () => {
  vi.useFakeTimers();
  const user = { id: 1, role: 'reporter', email: 'test@mail.com' };
  vi.stubGlobal('fetch', vi.fn().mockImplementation((url: string) => Promise.resolve(new Response(JSON.stringify(url.endsWith('/auth/token') ? { access_token: 'private-token', expires_in: 10 } : user)))));
  const storage = vi.spyOn(Storage.prototype, 'setItem');
  const { result, unmount } = renderHook(useAuth, { wrapper: AuthProvider });
  await act(() => result.current.login('test@mail.com', 'test-password'));
  expect(result.current.user?.id).toBe(1);
  expect(storage).not.toHaveBeenCalled();
  act(() => vi.advanceTimersByTime(10000));
  expect(result.current.user).toBe(null);
  expect(result.current.message).toContain('Sesja wygasła');
  unmount();
  const fresh = renderHook(useAuth, { wrapper: AuthProvider });
  expect(fresh.result.current.user).toBe(null);
});

import { act, cleanup, fireEvent, render, renderHook, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { afterEach, expect, it, vi } from 'vitest';
import App from './App';
import { AuthProvider, useAuth } from './auth';

afterEach(() => { cleanup(); vi.useRealTimers(); vi.unstubAllGlobals(); });
it('keeps credentials in memory and expires the session', async () => {
  vi.useFakeTimers();
  const user = { id: 1, role: 'reporter', email: 'test@mail.com', first_name: 'Anna', last_name: 'Nowak' };
  vi.stubGlobal('fetch', vi.fn().mockImplementation((url: string) => Promise.resolve(new Response(JSON.stringify(url.endsWith('/auth/token') ? { access_token: 'private-token', expires_in: 10 } : user)))));
  const storage = vi.spyOn(Storage.prototype, 'setItem');
  const { result, unmount } = renderHook(useAuth, { wrapper: AuthProvider });
  await act(() => result.current.login('test@mail.com', 'test-password'));
  expect(result.current.user?.id).toBe(1);
  expect(storage).not.toHaveBeenCalled();
  act(() => vi.advanceTimersByTime(10000));
  expect(result.current.user).toBe(null);
  expect(result.current.message).toContain('Your session expired');
  unmount();
  const fresh = renderHook(useAuth, { wrapper: AuthProvider });
  expect(fresh.result.current.user).toBe(null);
});

it.each([
  ['Łukasz', 'Żak', 'Łukasz Żak'],
  [null, null, 'User #1'],
])('opens tickets after sign-in and shows %s %s as %s', async (first_name, last_name, name) => {
  const account = { id: 1, role: 'reporter', email: 'legacy@mail.com', first_name, last_name };
  const fetch = vi.fn(async (url: string) => {
    if (url.endsWith('/auth/token')) return Response.json({ access_token: 'test-token', expires_in: 1800 });
    if (url.endsWith('/users/me')) return Response.json(account);
    return Response.json([]);
  });
  vi.stubGlobal('fetch', fetch);
  render(<MemoryRouter initialEntries={['/login']}><AuthProvider><App /></AuthProvider></MemoryRouter>);
  fireEvent.change(screen.getByLabelText('Email address'), { target: { value: account.email } });
  fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'test-password' } });
  fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

  await screen.findByRole('heading', { name: 'My tickets' });
  expect(screen.getByText(name)).toBeTruthy();
  expect(screen.queryByText(account.email)).toBeNull();
});

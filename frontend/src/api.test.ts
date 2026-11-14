import { afterEach, describe, expect, it, vi } from 'vitest';
import { errorMessage, request } from './api';
afterEach(() => vi.unstubAllGlobals());
describe('API client', () => {
  it('sends Bearer credentials and OAuth2 form correctly', async () => {
    const fetch = vi.fn().mockResolvedValue(new Response('{}', { status: 200 }));
    vi.stubGlobal('fetch', fetch);
    await request('/auth/token', { method: 'POST', body: new URLSearchParams({ username: 'test@mail.com', password: 'secret' }) });
    expect((fetch.mock.calls[0][1].headers as Headers).has('Content-Type')).toBe(false);
    await request('/tickets/1', {}, 'token');
    expect(fetch.mock.calls[1][1].headers.get('Authorization')).toBe('Bearer token');
  });
  it('translates validation and connection errors without echoing passwords', async () => {
    expect(errorMessage([{ loc: ['body', 'password'], type: 'string_too_short', input: 'secret' }], 422)).toContain('at least 12 characters');
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Network failure')));
    await expect(request('/tickets/')).rejects.toThrow('Cannot reach the API');
  });
  it('preserves API conflict messages', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: 'The ticket description changed.' }), { status: 409 })));
    await expect(request('/tickets/1')).rejects.toMatchObject({ status: 409, message: 'The ticket description changed.' });
  });
});

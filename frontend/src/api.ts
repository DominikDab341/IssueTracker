const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const fields: Record<string, string> = { email: 'E-mail', username: 'E-mail', password: 'Password', text: 'Description', work_blocked: 'Work blocked', resolution_note: 'Resolution notes', rejection_reason: 'Rejection reason', category: 'Category', priority: 'Priority', assignee_id: 'Assignee', expected_content_version: 'Description version', question: 'Question' };

export type RequestOptions = RequestInit & { timeoutMs?: number };

export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); }
}
export function errorMessage(detail: unknown, status: number): string {
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) return detail.map((e) => {
    const field = e.loc?.at(-1);
    // Translate structural validation errors that do not have a specific API message.
    const message = e.type === 'string_too_short' ? (field === 'password' ? 'Use at least 12 characters.' : 'The value is too short.')
      : e.type === 'string_too_long' ? 'The value exceeds the allowed length.'
      : e.type === 'missing' ? 'This field is required.'
      : e.type === 'extra_forbidden' ? 'This field is not allowed.'
      : e.type === 'value_error' && e.msg ? e.msg.replace(/^Value error, /, '') : 'Check this value.';
    return `${fields[field] || 'Form data'}: ${message}`;
  }).join(' ');
  return ({ 401: 'Your session expired. Sign in again.', 403: 'You do not have permission to do this.', 404: 'The page or ticket was not found.', 409: 'The data changed. Refresh and try again.', 422: 'Check the form data.' } as Record<number, string>)[status] || 'The API is unavailable. Try again shortly.';
}
export async function request<T>(path: string, { timeoutMs = 20000, ...options }: RequestOptions = {}, token?: string): Promise<T> {
  const headers = new Headers(options.headers);
  if (token) headers.set('Authorization', `Bearer ${token}`);
  if (options.body && !(options.body instanceof URLSearchParams)) headers.set('Content-Type', 'application/json');
  const controller = new AbortController();
  const abort = () => controller.abort();
  options.signal?.addEventListener('abort', abort, { once: true });
  if (options.signal?.aborted) controller.abort();
  const timeout = setTimeout(abort, timeoutMs);
  try {
    const response = await fetch(`${API_URL}${path}`, { ...options, headers, signal: controller.signal, cache: 'no-store' });
    const payload = await response.json().catch(() => null);
    if (!response.ok) throw new ApiError(response.status, errorMessage(payload?.detail, response.status));
    return payload as T;
  } catch (error) {
    if (error instanceof ApiError || options.signal?.aborted) throw error;
    throw new ApiError(0, 'Cannot reach the API. Check your connection and try again.');
  } finally {
    clearTimeout(timeout);
    options.signal?.removeEventListener('abort', abort);
  }
}

const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const fields: Record<string, string> = { email: 'E-mail', username: 'E-mail', password: 'Hasło', text: 'Opis', work_blocked: 'Blokada pracy', resolution_note: 'Opis rozwiązania', rejection_reason: 'Powód odrzucenia', category: 'Kategoria', priority: 'Priorytet', assignee_id: 'Osoba obsługująca', expected_content_version: 'Wersja opisu' };

export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); }
}
export function errorMessage(detail: unknown, status: number): string {
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) return detail.map((e) => {
    const field = e.loc?.at(-1);
    // The API provides Polish business messages; translate structural validation errors here.
    const message = e.type === 'string_too_short' ? 'Wartość jest za krótka (hasło: co najmniej 12 znaków).'
      : e.type === 'string_too_long' ? 'Przekroczono dozwoloną długość.'
      : e.type === 'missing' ? 'To pole jest wymagane.'
      : e.type === 'extra_forbidden' ? 'To pole nie jest dozwolone.'
      : e.type === 'value_error' && e.msg ? e.msg.replace(/^Value error, /, '') : 'Sprawdź podaną wartość.';
    return `${fields[field] || 'Dane formularza'}: ${message}`;
  }).join(' ');
  return ({ 401: 'Sesja wygasła. Zaloguj się ponownie.', 403: 'Brak uprawnień do tej operacji.', 404: 'Nie znaleziono strony lub zgłoszenia.', 409: 'Dane zmieniły się. Odśwież widok i spróbuj ponownie.', 422: 'Sprawdź dane formularza.' } as Record<number, string>)[status] || 'API jest niedostępne. Spróbuj ponownie za chwilę.';
}
export async function request<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const headers = new Headers(options.headers);
  if (token) headers.set('Authorization', `Bearer ${token}`);
  if (options.body && !(options.body instanceof URLSearchParams)) headers.set('Content-Type', 'application/json');
  const controller = new AbortController();
  const abort = () => controller.abort();
  options.signal?.addEventListener('abort', abort, { once: true });
  if (options.signal?.aborted) controller.abort();
  const timeout = setTimeout(abort, 20000);
  try {
    const response = await fetch(`${API_URL}${path}`, { ...options, headers, signal: controller.signal, cache: 'no-store' });
    const payload = await response.json().catch(() => null);
    if (!response.ok) throw new ApiError(response.status, errorMessage(payload?.detail, response.status));
    return payload as T;
  } catch (error) {
    if (error instanceof ApiError || options.signal?.aborted) throw error;
    throw new ApiError(0, 'Nie można połączyć się z API. Sprawdź połączenie i spróbuj ponownie.');
  } finally {
    clearTimeout(timeout);
    options.signal?.removeEventListener('abort', abort);
  }
}

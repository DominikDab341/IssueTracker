import { useEffect, useRef, useState, type FormEvent, type ReactNode } from 'react';
import { useAuth } from './auth';
import { categories, priorities, statuses, taskStates } from './labels';
import type { Ticket } from './types';

export function ErrorBox({ error }: { error: unknown }) {
  return error ? <div className="notice error" role="alert">{error instanceof Error ? error.message : String(error)}</div> : null;
}
export function Loading() { return <p className="muted" role="status">Ładowanie danych…</p>; }
export function Badge({ children, tone = '' }: { children: ReactNode; tone?: string }) {
  return <span className={`badge ${tone}`}>{children}</span>;
}
export function TicketBadges({ ticket }: { ticket: Ticket }) {
  return <div className="badges"><Badge tone={ticket.status}>{statuses[ticket.status]}</Badge>
    <Badge tone={ticket.priority}>{priorities[ticket.priority] ?? 'Nieustalony'}</Badge>
    <Badge tone={ticket.needs_review ? 'review' : ''}>{categories[ticket.category] ?? ticket.category}</Badge></div>;
}
export function TaskLabel({ ticket }: { ticket: Ticket }) {
  return <span>{ticket.current_task_state ? taskStates[ticket.current_task_state] : 'Brak zadania'}{!ticket.classification_current && ticket.current_task_state === 'succeeded' ? ' · wynik nieaktualny' : ''}</span>;
}
export function Options({ values, all }: { values: Record<string, string>; all?: string }) {
  return <>{all && <option value="">{all}</option>}{Object.entries(values).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</>;
}
// One in-flight fetch; changing dependencies aborts and discards the old response.
export function useResource<T>(path: string, revision = 0) {
  const { api } = useAuth();
  const [state, setState] = useState<{ data: T | null; error: unknown; loading: boolean }>({ data: null, error: null, loading: true });
  useEffect(() => {
    const controller = new AbortController();
    setState({ data: null, error: null, loading: true });
    api<T>(path, { signal: controller.signal }).then(data => {
      if (!controller.signal.aborted) setState({ data, error: null, loading: false });
    }).catch(error => { if (!controller.signal.aborted) setState({ data: null, error, loading: false }); });
    return () => controller.abort();
  }, [api, path, revision]);
  return state;
}
export function ActionForm({ title, action, children, submit = 'Zapisz', onSuccess, onFailure }: {
  title: string; action: (form: FormData) => Promise<unknown>; children: ReactNode;
  submit?: string; onSuccess: () => void; onFailure?: (error: unknown) => void;
}) {
  const [busy, setBusy] = useState(false);
  const inFlight = useRef(false);
  const [error, setError] = useState<unknown>(null);
  const [success, setSuccess] = useState(false);
  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (inFlight.current) return;
    inFlight.current = true; setBusy(true); setError(null); setSuccess(false);
    try { await action(new FormData(event.currentTarget)); setSuccess(true); onSuccess(); }
    catch (error) { setError(error); onFailure?.(error); }
    finally { setBusy(false); inFlight.current = false; }
  }
  return <form className="action-form" onSubmit={save}><h3>{title}</h3><ErrorBox error={error} />
    {success && <p role="status" className="success">Zapisano zmianę.</p>}
    <fieldset disabled={busy}>{children}<button type="submit">{busy ? 'Zapisywanie…' : submit}</button></fieldset></form>;
}

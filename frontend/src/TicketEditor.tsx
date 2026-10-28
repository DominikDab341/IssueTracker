import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router';
import { useAuth } from './auth';
import { ApiError } from './api';
import { ErrorBox } from './components';
import type { Ticket } from './types';

export default function TicketEditor({ ticket, onSaved, onConflict }: { ticket?: Ticket; onSaved?: () => void; onConflict?: (error: unknown) => void }) {
  const { api } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);
  const [blocked, setBlocked] = useState(ticket?.work_blocked ?? false);
  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setBusy(true); setError(null);
    try {
      const result = await api<{ ticket: Ticket }>(ticket ? `/tickets/${ticket.id}` : '/tickets/', {
        method: ticket ? 'PATCH' : 'POST', body: JSON.stringify({ text: String(form.get('text')), work_blocked: blocked }),
      });
      if (onSaved) onSaved(); else navigate(`/tickets/${result.ticket.id}`);
    } catch (error) {
      setError(error);
      if (error instanceof ApiError && [403, 409].includes(error.status)) onConflict?.(error);
    } finally { setBusy(false); }
  }
  return <form onSubmit={save} className="ticket-editor"><ErrorBox error={error} /><fieldset disabled={busy}>
    <label>Opis problemu<textarea name="text" defaultValue={ticket?.text || ''} rows={7} maxLength={10000} required placeholder="Opisz, co się dzieje, od kiedy występuje problem i jakie kroki zostały już wykonane." /></label>
    <p className="hint">Limit wynosi 256 tokenów, sprawdzanych przez serwer. Nie wpisuj haseł ani innych sekretów.</p>
    <label className="check blocked-check"><input type="checkbox" checked={blocked} onChange={e => setBlocked(e.target.checked)} /><span><strong>Nie mogę kontynuować pracy</strong><small>Problem uniemożliwia wykonywanie obowiązków.</small></span></label>
    {ticket?.priority_source === 'administrator' ? <p className="notice">Priorytet ustalił administrator. Zmiana blokady pracy zachowa jego decyzję.</p> : blocked && <p className="notice">Blokada pracy nada zgłoszeniu priorytet krytyczny.</p>}
    <div className="button-row"><button type="submit">{busy ? 'Zapisywanie…' : ticket ? 'Zapisz zmiany' : 'Wyślij zgłoszenie →'}</button>{!ticket && <Link to="/tickets" className="button secondary">Wróć do listy</Link>}</div>
  </fieldset></form>;
}

import { useState } from 'react';
import { Link, useParams } from 'react-router';
import { useAuth } from './auth';
import { ActionForm, Badge, ErrorBox, Loading, Options, TicketBadges, useResource } from './components';
import { categories, date, permissions, person, priorities, sources, taskStates } from './labels';
import type { User } from './types';
import { useTicket } from './useTicket';
import TicketEditor from './TicketEditor';

function Assignment({ id, reload, onFailure }: { id: number; reload: () => void; onFailure: (error: unknown) => void }) {
  const { api } = useAuth();
  const [offset, setOffset] = useState(0);
  const { data, error, loading } = useResource<Pick<User, 'id' | 'email'>[]>(`/admin/assignees?limit=100&offset=${offset}`);
  return <ActionForm title="Przypisz osobę obsługującą" action={form => api(`/tickets/${id}/assignee`, { method: 'PATCH', body: JSON.stringify({ assignee_id: Number(form.get('assignee')) }) })} onSuccess={reload} onFailure={onFailure}>
    <ErrorBox error={error} />{loading && <Loading />}<label>Wykonawca<select name="assignee" required key={offset}><option value="">Wybierz osobę</option>{data?.map(user => <option key={user.id} value={user.id}>{user.email} (#{user.id})</option>)}</select></label>
    {data?.length === 0 && <p className="hint">Brak aktywnych, zaakceptowanych kont obsługi na tej stronie.</p>}
    <div className="button-row"><button type="button" className="secondary" disabled={offset === 0 || loading} onClick={() => setOffset(o => o - 100)}>Poprzednie osoby</button><button type="button" className="secondary" disabled={loading || !data || data.length < 100} onClick={() => setOffset(o => o + 100)}>Kolejne osoby</button></div>
  </ActionForm>;
}

export default function TicketDetail() {
  const { id = '' } = useParams();
  const { user, api } = useAuth();
  const { ticket, task, duplicates, error, extraError, loading, reload } = useTicket(id);
  const [actionError, setActionError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);
  const [editing, setEditing] = useState(false);
  if (loading && !ticket) return <Loading />;
  if (!ticket || !user) return <><ErrorBox error={error} /><button onClick={reload}>Spróbuj ponownie</button><p><Link to="/tickets">← Wróć do listy</Link></p></>;
  const can = permissions(user, ticket, task);
  const ticketId = ticket.id;
  const onFailure = (error: unknown) => { setActionError(error); reload(); };
  const mutate = (suffix: string, body: unknown) => api(`/tickets/${ticket.id}/${suffix}`, { method: 'PATCH', body: JSON.stringify(body) });
  async function change(status: string) {
    setBusy(true); setActionError(null);
    try { await mutate('status', { status }); }
    catch (error) { setActionError(error); }
    finally { setBusy(false); reload(); }
  }
  async function retry() {
    setBusy(true); setActionError(null);
    try { await api(`/tickets/${ticketId}/classification/retry`, { method: 'POST' }); }
    catch (error) { setActionError(error); }
    finally { setBusy(false); reload(); }
  }
  return <><Link className="back-link" to="/tickets">← Wszystkie zgłoszenia</Link><div className="page-heading"><div><span className="eyebrow">ZGŁOSZENIE #{ticket.id}</span><h1>Szczegóły zgłoszenia</h1><p className="muted">Utworzono {date(ticket.created_at)}</p></div><button className="secondary" onClick={reload}>Odśwież dane</button></div>
    <ErrorBox error={error} /><ErrorBox error={extraError} /><ErrorBox error={actionError} />
    <div className="detail-grid"><div className="detail-main"><section className="panel"><TicketBadges ticket={ticket} /><h2>Opis problemu</h2><p className="ticket-text">{ticket.text}</p>
      {ticket.work_blocked && <p className="notice">Autor nie może kontynuować pracy.</p>}
      {can.edit ? <button className="secondary" onClick={() => setEditing(e => !e)}>{editing ? 'Zamknij edycję' : 'Edytuj zgłoszenie'}</button> : <p className="hint">Opis problemu i blokada pracy są tylko do odczytu.</p>}
      {editing && can.edit && <TicketEditor key={ticket.content_version} ticket={ticket} onSaved={() => { setEditing(false); reload(); }} onConflict={onFailure} />}
    </section>
    <section className="panel"><div className="section-heading"><h2>Klasyfikacja</h2><Badge tone={task?.state === 'failed' ? 'review' : ''}>{task ? taskStates[task.state] : ticket.current_task_state ? taskStates[ticket.current_task_state] : 'Brak zadania'}</Badge></div>
      <p className="muted">Stan zadania jest niezależny od statusu zgłoszenia.</p>
      {task?.state === 'failed' && <div className="notice error" role="alert">{task.error_code === 'interrupted' ? 'Przetwarzanie zostało przerwane. ' : ''}{task.error || 'Nie udało się zakończyć klasyfikacji.'}</div>}
      {ticket.needs_review && <p className="notice">Do weryfikacji: kategoria wymaga oceny osoby obsługującej.</p>}
      {!ticket.classification_current && <p className="hint">Brak aktualnego wyniku modelu dla bieżącej wersji opisu.</p>}
      <dl className="facts"><dt>Przewidywanie modelu</dt><dd>{ticket.predicted_category ? categories[ticket.predicted_category] || ticket.predicted_category : 'Brak wyniku'}{ticket.predicted_category_version !== null && ` · wersja ${ticket.predicted_category_version}`}</dd>
        <dt>Kategoria operacyjna</dt><dd>{categories[ticket.category] || ticket.category}</dd>
        <dt>Korekta ręczna</dt><dd>{ticket.manual_category ? `${categories[ticket.manual_category]} · ${ticket.manual_category_current ? 'aktualna' : 'nieaktualna'} · ${person(ticket.manual_category_by_id)} · ${date(ticket.manual_category_at)}` : 'Brak korekty'}</dd></dl>
      {can.retry && <button disabled={busy} onClick={retry}>{busy ? 'Ponawianie…' : 'Ponów klasyfikację'}</button>}
      {can.category && <ActionForm title="Skoryguj kategorię" key={`category-${ticket.content_version}`} action={form => mutate('category', { category: form.get('category'), expected_content_version: ticket.content_version })} onSuccess={reload} onFailure={onFailure}>
        <label>Kategoria<select name="category" defaultValue={ticket.category === 'unknown' ? '' : ticket.category} required><option value="">Wybierz kategorię</option><Options values={Object.fromEntries(Object.entries(categories).filter(([key]) => key !== 'unknown'))} /></select></label>
      </ActionForm>}
    </section>
    {(ticket.resolution_note || ticket.rejection_reason) && <section className="panel"><h2>{ticket.resolution_note ? 'Opis rozwiązania' : 'Powód odrzucenia'}</h2><p className="ticket-text">{ticket.resolution_note || ticket.rejection_reason}</p><p className="hint">{person(ticket.resolution_note ? ticket.resolved_by_id : ticket.rejected_by_id)} · {date(ticket.resolution_note ? ticket.resolved_at : ticket.rejected_at)}</p></section>}
    <section className="panel"><h2>Możliwe duplikaty</h2><p className="hint">Sugestie podobnych aktywnych spraw dostępnych dla Twojego konta. Podobieństwo tekstu nie potwierdza duplikatu.</p>
      {duplicates.length ? <ul className="duplicates">{duplicates.map(item => <li key={item.id}><Link to={`/tickets/${item.id}`}>#{item.id} · {item.text}</Link><span className="hint">Podobieństwo tekstu: {Math.round(item.similarity * 100)}%</span></li>)}</ul> : <p className="muted">Brak sugestii dla aktualnego wyniku klasyfikacji.</p>}
    </section></div>
    <aside className="detail-aside"><section className="panel"><h2>Informacje o sprawie</h2><dl className="facts vertical"><dt>Autor</dt><dd>{ticket.author_id ? person(ticket.author_id) : 'Autor historyczny nieznany'}</dd><dt>Osoba obsługująca</dt><dd>{person(ticket.assignee_id)}</dd><dt>Priorytet</dt><dd>{priorities[ticket.priority]}<small>{sources[ticket.priority_source] || ticket.priority_source}</small></dd><dt>Priorytet bazowy modelu</dt><dd>{ticket.base_priority ? priorities[ticket.base_priority] : 'Brak wyniku'}</dd>
      {ticket.manual_priority_by_id && <><dt>Decyzja o priorytecie</dt><dd>{person(ticket.manual_priority_by_id)}<small>{date(ticket.manual_priority_at)}</small></dd></>}
      <dt>Ostatnia aktualizacja</dt><dd>{date(ticket.updated_at)}</dd></dl></section>
      <section className="panel"><h2>Działania</h2><div className="stack">
        {can.accept && <button disabled={busy} onClick={() => change('accepted')}>Przyjmij zgłoszenie</button>}
        {can.start && <button disabled={busy} onClick={() => change('in_progress')}>Rozpocznij realizację</button>}
        {can.cancel && <button className="danger secondary" disabled={busy} onClick={() => change('cancelled')}>Anuluj zgłoszenie</button>}
        {!(can.accept || can.start || can.cancel || can.assign || can.resolve || can.reject || can.priority) && <p className="muted">Brak dostępnych działań na tym etapie.</p>}
      </div>
      {can.resolve && <ActionForm title="Zakończ realizację" submit="Rozwiąż zgłoszenie" action={form => mutate('status', { status: 'resolved', resolution_note: form.get('note') })} onSuccess={reload} onFailure={onFailure}><label>Opis rozwiązania<textarea name="note" required maxLength={2000} rows={4} /></label></ActionForm>}
      {can.reject && <ActionForm title="Odrzuć zgłoszenie" submit="Odrzuć zgłoszenie" action={form => mutate('status', { status: 'rejected', rejection_reason: form.get('note') })} onSuccess={reload} onFailure={onFailure}><label>Powód odrzucenia<textarea name="note" required maxLength={2000} rows={3} /></label></ActionForm>}
      {can.assign && <Assignment id={ticket.id} reload={reload} onFailure={onFailure} />}
      {can.priority && <ActionForm title="Ustal priorytet ręcznie" action={form => mutate('priority', { priority: form.get('priority') })} onSuccess={reload} onFailure={onFailure}><label>Priorytet<select name="priority" defaultValue={ticket.priority}><Options values={Object.fromEntries(Object.entries(priorities).filter(([key]) => key !== 'unknown'))} /></select></label></ActionForm>}
      </section>
    </aside></div></>;
}

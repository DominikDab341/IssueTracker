import { useState } from 'react';
import { Link, useSearchParams } from 'react-router';
import { useAuth } from './auth';
import { ErrorBox, Loading, Options, TaskLabel, TicketBadges, useResource } from './components';
import { categories, date, priorities, statuses } from './labels';
import type { Ticket } from './types';

export default function TicketList() {
  const { user } = useAuth();
  const [params, setParams] = useSearchParams();
  const [revision, setRevision] = useState(0);
  const offset = Math.max(0, Number(params.get('offset')) || 0);
  const query = new URLSearchParams({ limit: '20', offset: String(offset) });
  for (const key of ['status', 'category', 'priority']) if (params.get(key)) query.set(key, params.get(key)!);
  if (user?.role !== 'reporter' && params.get('needs_review') === 'true') query.set('needs_review', 'true');
  const { data, error, loading } = useResource<Ticket[]>(`/tickets/?${query}`, revision);
  function filter(key: string, value: string) {
    const next = new URLSearchParams(params); next.delete('offset');
    if (value) next.set(key, value); else next.delete(key);
    setParams(next);
  }
  function page(nextOffset: number) { const next = new URLSearchParams(params); next.set('offset', String(nextOffset)); setParams(next); }
  return <><div className="page-heading"><div><span className="eyebrow">TICKET DESK</span><h1>{user?.role === 'reporter' ? 'My tickets' : 'All tickets'}</h1><p className="muted">{user?.role === 'reporter' ? 'View your tickets and track their progress.' : 'Review and coordinate tickets.'}</p></div><Link className="button" to="/tickets/new">＋ New ticket</Link></div>
    <section className="panel list-panel"><div className="toolbar"><label>Status<select value={params.get('status') || ''} onChange={e => filter('status', e.target.value)}><Options values={statuses} all="All statuses" /></select></label>
      <label>Category<select value={params.get('category') || ''} onChange={e => filter('category', e.target.value)}><Options values={categories} all="All categories" /></select></label>
      <label>Priority<select value={params.get('priority') || ''} onChange={e => filter('priority', e.target.value)}><Options values={priorities} all="All priorities" /></select></label>
      {user?.role !== 'reporter' && <label className="check"><input type="checkbox" checked={params.get('needs_review') === 'true'} onChange={e => filter('needs_review', e.target.checked ? 'true' : '')} />Needs review</label>}
      <button className="secondary" onClick={() => setRevision(r => r + 1)}>Refresh</button></div>
      <ErrorBox error={error} />{loading && <Loading />}
      {data && (data.length ? <div className="ticket-list">{data.map(ticket => <Link className="ticket-row" to={`/tickets/${ticket.id}`} key={ticket.id}>
        <div className="ticket-number">#{ticket.id}</div><div className="ticket-description"><h2>{ticket.text}</h2><TicketBadges ticket={ticket} /><p className="hint">{date(ticket.created_at)} · Task: <TaskLabel ticket={ticket} /></p></div><span className="row-arrow" aria-hidden="true">↗</span>
      </Link>)}</div> : <div className="empty"><span className="empty-icon">✓</span><h2>No tickets</h2><p className="muted">No tickets match the selected filters.</p><Link to="/tickets/new">Create a ticket →</Link></div>)}
      <div className="pagination"><span className="hint">Page {Math.floor(offset / 20) + 1}</span><button className="secondary" disabled={loading || offset === 0} onClick={() => page(Math.max(0, offset - 20))}>← Previous</button><button className="secondary" disabled={loading || !data || data.length < 20} onClick={() => page(offset + 20)}>Next →</button></div>
    </section></>;
}

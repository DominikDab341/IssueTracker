import { useState } from 'react';
import { Link, useParams } from 'react-router';
import { useAuth } from './auth';
import { ActionForm, Badge, ErrorBox, Loading, Options, TicketBadges, useResource } from './components';
import { categories, date, permissions, person, priorities, reviewReasons, sources, taskStates } from './labels';
import type { User } from './types';
import { useTicket } from './useTicket';
import TicketEditor from './TicketEditor';

function Assignment({ id, reload, onFailure }: { id: number; reload: () => void; onFailure: (error: unknown) => void }) {
  const { api } = useAuth();
  const [offset, setOffset] = useState(0);
  const { data, error, loading } = useResource<Pick<User, 'id' | 'email'>[]>(`/admin/assignees?limit=100&offset=${offset}`);
  return <ActionForm title="Assign to staff" action={form => api(`/tickets/${id}/assignee`, { method: 'PATCH', body: JSON.stringify({ assignee_id: Number(form.get('assignee')) }) })} onSuccess={reload} onFailure={onFailure}>
    <ErrorBox error={error} />{loading && <Loading />}<label>Assignee<select name="assignee" required key={offset}><option value="">Select an assignee</option>{data?.map(user => <option key={user.id} value={user.id}>{user.email} (#{user.id})</option>)}</select></label>
    {data?.length === 0 && <p className="hint">No active, approved staff accounts on this page.</p>}
    <div className="button-row"><button type="button" className="secondary" disabled={offset === 0 || loading} onClick={() => setOffset(o => o - 100)}>Previous staff</button><button type="button" className="secondary" disabled={loading || !data || data.length < 100} onClick={() => setOffset(o => o + 100)}>Next staff</button></div>
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
  if (!ticket || !user) return <><ErrorBox error={error} /><button onClick={reload}>Try again</button><p><Link to="/tickets">← Back to tickets</Link></p></>;
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
  return <><Link className="back-link" to="/tickets">← All tickets</Link><div className="page-heading"><div><span className="eyebrow">TICKET #{ticket.id}</span><h1>Ticket details</h1><p className="muted">Created {date(ticket.created_at)}</p></div><button className="secondary" onClick={reload}>Refresh</button></div>
    <ErrorBox error={error} /><ErrorBox error={extraError} /><ErrorBox error={actionError} />
    <div className="detail-grid"><div className="detail-main"><section className="panel"><TicketBadges ticket={ticket} /><h2>Problem description</h2><p className="ticket-text">{ticket.text}</p>
      {ticket.work_blocked && <p className="notice">The reporter cannot continue working.</p>}
      {can.edit ? <button className="secondary" onClick={() => setEditing(e => !e)}>{editing ? 'Close editor' : 'Edit ticket'}</button> : <p className="hint">The description and work-blocked setting are read-only.</p>}
      {editing && can.edit && <TicketEditor key={ticket.content_version} ticket={ticket} onSaved={() => { setEditing(false); reload(); }} onConflict={onFailure} />}
    </section>
    <section className="panel"><div className="section-heading"><h2>Classification</h2><Badge tone={task?.state === 'failed' ? 'review' : ''}>{task ? taskStates[task.state] : ticket.current_task_state ? taskStates[ticket.current_task_state] : 'No task'}</Badge></div>
      <p className="muted">Task status tracks classification progress.</p>
      {task?.state === 'failed' && <div className="notice error" role="alert">{task.error_code === 'interrupted' ? 'Processing was interrupted. ' : ''}{task.error || 'Classification failed.'}</div>}
      {ticket.category === 'unknown' && <p className="notice">A staff member needs to review the category. {ticket.review_version === ticket.content_version && reviewReasons[ticket.category_review_reason || '']}</p>}
      {ticket.priority_needs_review && <p className="notice">The base priority needs review. {reviewReasons[ticket.priority_review_reason || '']} The suggested base priority is shown separately from the effective priority.</p>}
      {!ticket.classification_current && <p className="hint">The current description has no classification result.</p>}
      <dl className="facts"><dt>Predicted category</dt><dd>{ticket.predicted_category ? categories[ticket.predicted_category] || 'Legacy result' : 'No result'}{ticket.predicted_category_version !== null && ` · version ${ticket.predicted_category_version}`}</dd>
        <dt>Current category</dt><dd>{categories[ticket.category] || ticket.category}</dd>
        <dt>Manual correction</dt><dd>{ticket.manual_category ? `${categories[ticket.manual_category] || 'Legacy category'} · ${ticket.manual_category_current ? 'Current' : 'Out of date'} · ${person(ticket.manual_category_by_id)} · ${date(ticket.manual_category_at)}` : 'No correction'}</dd></dl>
      {can.retry && <button disabled={busy} onClick={retry}>{busy ? 'Retrying…' : 'Retry classification'}</button>}
      {can.category && <ActionForm title="Correct category" key={`category-${ticket.content_version}`} action={form => mutate('category', { category: form.get('category'), expected_content_version: ticket.content_version })} onSuccess={reload} onFailure={onFailure}>
        <label>Category<select name="category" defaultValue={ticket.category === 'unknown' ? '' : ticket.category} required><option value="">Select a category</option><Options values={Object.fromEntries(Object.entries(categories).filter(([key]) => key !== 'unknown'))} /></select></label>
      </ActionForm>}
    </section>
    {(ticket.resolution_note || ticket.rejection_reason) && <section className="panel"><h2>{ticket.resolution_note ? 'Resolution notes' : 'Rejection reason'}</h2><p className="ticket-text">{ticket.resolution_note || ticket.rejection_reason}</p><p className="hint">{person(ticket.resolution_note ? ticket.resolved_by_id : ticket.rejected_by_id)} · {date(ticket.resolution_note ? ticket.resolved_at : ticket.rejected_at)}</p></section>}
    <section className="panel"><h2>Possible duplicates</h2><p className="hint">Review similar active tickets to check for duplicates.</p>
      {duplicates.length ? <ul className="duplicates">{duplicates.map(item => <li key={item.id}><Link to={`/tickets/${item.id}`}>#{item.id} · {item.text}</Link><span className="hint">Text similarity: {Math.round(item.similarity * 100)}%</span></li>)}</ul> : <p className="muted">No possible duplicates for the current classification.</p>}
    </section></div>
    <aside className="detail-aside"><section className="panel"><h2>Ticket information</h2><dl className="facts vertical"><dt>Reporter</dt><dd>{ticket.author_id ? person(ticket.author_id) : 'Unknown legacy reporter'}</dd><dt>Assignee</dt><dd>{person(ticket.assignee_id)}</dd><dt>Priority</dt><dd>{priorities[ticket.priority]}<small>{sources[ticket.priority_source] || ticket.priority_source}</small></dd><dt>Predicted base priority</dt><dd>{ticket.base_priority ? priorities[ticket.base_priority] : 'No result'}</dd>
      {ticket.predicted_base_priority && ticket.priority_needs_review && <><dt>Suggestion to review</dt><dd>{priorities[ticket.predicted_base_priority]}</dd></>}
      {ticket.escalation_reason && <><dt>Escalation</dt><dd>{ticket.escalation_reason}<small>{date(ticket.escalated_at || null)}</small></dd></>}
      {ticket.manual_priority_by_id && <><dt>Priority decision</dt><dd>{person(ticket.manual_priority_by_id)}<small>{date(ticket.manual_priority_at)}</small></dd></>}
      <dt>Last updated</dt><dd>{date(ticket.updated_at)}</dd></dl></section>
      <section className="panel"><h2>Actions</h2><div className="stack">
        {can.accept && <button disabled={busy} onClick={() => change('accepted')}>Accept ticket</button>}
        {can.start && <button disabled={busy} onClick={() => change('in_progress')}>Start work</button>}
        {can.cancel && <button className="danger secondary" disabled={busy} onClick={() => change('cancelled')}>Cancel ticket</button>}
        {!(can.accept || can.start || can.cancel || can.assign || can.resolve || can.reject || can.priority) && <p className="muted">No actions are available at this stage.</p>}
      </div>
      {can.resolve && <ActionForm title="Finish work" submit="Resolve ticket" action={form => mutate('status', { status: 'resolved', resolution_note: form.get('note') })} onSuccess={reload} onFailure={onFailure}><label>Resolution notes<textarea name="note" required maxLength={2000} rows={4} /></label></ActionForm>}
      {can.reject && <ActionForm title="Reject ticket" submit="Reject ticket" action={form => mutate('status', { status: 'rejected', rejection_reason: form.get('note') })} onSuccess={reload} onFailure={onFailure}><label>Rejection reason<textarea name="note" required maxLength={2000} rows={3} /></label></ActionForm>}
      {can.assign && <Assignment id={ticket.id} reload={reload} onFailure={onFailure} />}
      {can.priority && <ActionForm title="Set priority manually" action={form => mutate('priority', { priority: form.get('priority') })} onSuccess={reload} onFailure={onFailure}><label>Priority<select name="priority" defaultValue={ticket.priority}><Options values={Object.fromEntries(Object.entries(priorities).filter(([key]) => key !== 'unknown'))} /></select></label></ActionForm>}
      </section>
    </aside></div></>;
}

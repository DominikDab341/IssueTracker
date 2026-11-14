import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router';
import { useAuth } from './auth';
import { ActionForm, Badge, ErrorBox, Loading, Options, TicketBadges } from './components';
import { categories, date, permissions, person, priorities, reviewReasons, sources, taskStates } from './labels';
import type { User } from './types';
import { useTicket } from './useTicket';
import TicketEditor from './TicketEditor';

function Assignment({ id, reload, onFailure }: { id: number; reload: () => void; onFailure: (error: unknown) => void }) {
  const { api } = useAuth();
  const [assignees, setAssignees] = useState<Pick<User, 'id' | 'email'>[] | null>(null);
  const [error, setError] = useState<unknown>(null);
  useEffect(() => {
    const controller = new AbortController();
    const limit = 100;
    async function load() {
      const staff = new Map<number, Pick<User, 'id' | 'email'>>();
      try {
        for (let offset = 0; !controller.signal.aborted; offset += limit) {
          const page = await api<Pick<User, 'id' | 'email'>[]>(`/admin/assignees?limit=${limit}&offset=${offset}`, { signal: controller.signal });
          for (const user of page) staff.set(user.id, user);
          if (page.length < limit) break;
        }
        if (!controller.signal.aborted) setAssignees([...staff.values()]);
      } catch (error) {
        if (!controller.signal.aborted) setError(error);
      }
    }
    void load();
    return () => controller.abort();
  }, [api]);
  if (error || !assignees?.length) return <section className="action-form">
    <h3>Assign to staff</h3>
    <ErrorBox error={error} />
    {!error && (assignees ? <p className="hint">No active, approved staff accounts.</p> : <Loading />)}
  </section>;
  return <ActionForm title="Assign to staff" action={form => api(`/tickets/${id}/assignee`, { method: 'PATCH', body: JSON.stringify({ assignee_id: Number(form.get('assignee')) }) })} onSuccess={reload} onFailure={onFailure}>
    <label>Assignee<select name="assignee" required><option value="">Select an assignee</option>{assignees.map(user => <option key={user.id} value={user.id}>{user.email} (#{user.id})</option>)}</select></label>
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
  const hasOtherActions = can.accept || can.start || can.cancel || can.assign || can.reject;
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
  return <div className="ticket-detail"><Link className="back-link" to="/tickets">← All tickets</Link><div className="page-heading"><div><h1>Ticket #{ticket.id}</h1><p className="muted">Created {date(ticket.created_at)}</p></div><button className="secondary" onClick={reload}>Refresh</button></div>
    <ErrorBox error={error} /><ErrorBox error={extraError} /><ErrorBox error={actionError} />
    <div className="detail-grid"><div className="detail-main"><section className="panel ticket-problem"><TicketBadges ticket={ticket} /><h2>Problem description</h2><p className="ticket-text">{ticket.text}</p>
      {ticket.work_blocked && <p className="notice">The reporter cannot continue working.</p>}
      {can.edit && <button className="secondary" onClick={() => setEditing(e => !e)}>{editing ? 'Close editor' : 'Edit ticket'}</button>}
      {editing && can.edit && <TicketEditor key={ticket.content_version} ticket={ticket} onSaved={() => { setEditing(false); reload(); }} onConflict={onFailure} />}
    </section>
    {can.resolve && <section className="panel ticket-resolution">
      <ActionForm title="Finish work" submit="Resolve ticket" action={form => mutate('status', { status: 'resolved', resolution_note: form.get('note') })} onSuccess={reload} onFailure={onFailure}>
        <div id="resolution-note-guide" className="resolution-guide">
          <p>Describe the change that fixed the issue and how you verified it. Name the device, app, or setting you changed.</p>
          <p><strong>Example</strong> “Updated the VPN client and confirmed it stayed connected after waking the laptop from sleep.”</p>
        </div>
        <label>Resolution notes<textarea name="note" aria-describedby="resolution-note-guide" required maxLength={2000} rows={4} /></label>
      </ActionForm>
    </section>}
    {(ticket.resolution_note || ticket.rejection_reason) && <section className="panel"><h2>{ticket.resolution_note ? 'Resolution notes' : 'Rejection reason'}</h2><p className="ticket-text">{ticket.resolution_note || ticket.rejection_reason}</p><p className="hint">{person(ticket.resolution_note ? ticket.resolved_by_id : ticket.rejected_by_id)} · {date(ticket.resolution_note ? ticket.resolved_at : ticket.rejected_at)}</p></section>}
    <section className="panel"><div className="section-heading"><h2>Classification</h2><Badge tone={task?.state === 'failed' ? 'review' : ''}>{task ? taskStates[task.state] : ticket.current_task_state ? taskStates[ticket.current_task_state] : 'No task'}</Badge></div>
      {task?.state === 'failed' && <div className="notice error" role="alert">{task.error_code === 'interrupted' ? 'Processing was interrupted. ' : ''}{task.error || 'Classification failed.'}</div>}
      {ticket.category === 'unknown' && <p className="notice">A staff member needs to review the category. {ticket.review_version === ticket.content_version && reviewReasons[ticket.category_review_reason || '']}</p>}
      {ticket.priority_needs_review && <p className="notice">The base priority needs review. {reviewReasons[ticket.priority_review_reason || '']} The suggested base priority is shown separately from the effective priority.</p>}
      {!ticket.classification_current && <p className="hint">The current description has no classification result.</p>}
      <dl className="facts"><dt>Current category</dt><dd>{categories[ticket.category] || ticket.category}</dd>
        <dt>Predicted category</dt><dd>{ticket.predicted_category ? categories[ticket.predicted_category] || 'Legacy result' : 'No result'}{ticket.predicted_category_version != null && <small>Version {ticket.predicted_category_version}</small>}</dd>
        <dt>Manual correction</dt><dd>{ticket.manual_category ? <>{categories[ticket.manual_category] || 'Legacy category'}<small>{ticket.manual_category_current ? 'Current' : 'Out of date'} · {person(ticket.manual_category_by_id)} · {date(ticket.manual_category_at)}</small></> : 'No correction'}</dd></dl>
      {can.retry && <button disabled={busy} onClick={retry}>{busy ? 'Retrying…' : 'Retry classification'}</button>}
      {(can.category || can.priority) && <div className="classification-actions">
        {can.category && <ActionForm title="Correct category" submit="Save category" key={`category-${ticket.content_version}`} action={form => mutate('category', { category: form.get('category'), expected_content_version: ticket.content_version })} onSuccess={reload} onFailure={onFailure}>
          <label>Category<select name="category" defaultValue={ticket.category === 'unknown' ? '' : ticket.category} required><option value="">Select a category</option><Options values={Object.fromEntries(Object.entries(categories).filter(([key]) => key !== 'unknown'))} /></select></label>
        </ActionForm>}
        {can.priority && <ActionForm title="Change priority" submit="Save priority" action={form => mutate('priority', { priority: form.get('priority') })} onSuccess={reload} onFailure={onFailure}>
          <label>New priority<select name="priority" defaultValue={ticket.priority === 'unknown' ? '' : ticket.priority} required>
            <option value="" disabled>Select a priority</option>
            <Options values={Object.fromEntries(Object.entries(priorities).filter(([key]) => key !== 'unknown'))} />
          </select></label>
        </ActionForm>}
      </div>}
    </section>
    <section className="panel"><h2>Possible duplicates</h2>
      {duplicates.length ? <ul className="duplicates">{duplicates.map(item => <li key={item.id}><Link to={`/tickets/${item.id}`}>#{item.id} · {item.text}</Link><span className="hint">Text similarity: {Math.round(item.similarity * 100)}%</span></li>)}</ul> : <p className="muted">No possible duplicates for the current classification.</p>}
    </section></div>
    <aside className="detail-aside"><section className="panel"><h2>Ticket information</h2><dl className="facts vertical"><dt>Reporter</dt><dd>{ticket.author_id ? person(ticket.author_id) : 'Unknown legacy reporter'}</dd><dt>Assignee</dt><dd>{person(ticket.assignee_id)}</dd><dt>Priority</dt><dd>{priorities[ticket.priority]}<small>{sources[ticket.priority_source] || ticket.priority_source}</small>{user.role === 'staff' && <small>Only administrators can change the priority.</small>}</dd><dt>Predicted base priority</dt><dd>{ticket.base_priority ? priorities[ticket.base_priority] : 'No result'}</dd>
      {ticket.predicted_base_priority && ticket.priority_needs_review && <><dt>Suggestion to review</dt><dd>{priorities[ticket.predicted_base_priority]}</dd></>}
      {ticket.escalation_reason && <><dt>Escalation</dt><dd>{ticket.escalation_reason}<small>{date(ticket.escalated_at || null)}</small></dd></>}
      {ticket.manual_priority_by_id && <><dt>Priority decision</dt><dd>{person(ticket.manual_priority_by_id)}<small>{date(ticket.manual_priority_at)}</small></dd></>}
      <dt>Last updated</dt><dd>{date(ticket.updated_at)}</dd></dl>
    </section>
      {hasOtherActions && <section className="panel ticket-actions"><h2>Actions</h2>
      {(can.accept || can.start || can.cancel) && <div className="stack">
        {can.accept && <button disabled={busy} onClick={() => change('accepted')}>Accept ticket</button>}
        {can.start && <button disabled={busy} onClick={() => change('in_progress')}>Start work</button>}
        {can.cancel && <button className="danger secondary" disabled={busy} onClick={() => change('cancelled')}>Cancel ticket</button>}
      </div>}
      {can.reject && <ActionForm title="Reject ticket" submit="Reject ticket" action={form => mutate('status', { status: 'rejected', rejection_reason: form.get('note') })} onSuccess={reload} onFailure={onFailure}><label>Rejection reason<textarea name="note" required maxLength={2000} rows={3} /></label></ActionForm>}
      {can.assign && <Assignment id={ticket.id} reload={reload} onFailure={onFailure} />}
      </section>}
    </aside></div></div>;
}

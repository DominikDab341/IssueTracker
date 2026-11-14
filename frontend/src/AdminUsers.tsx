import { useState } from 'react';
import { useAuth } from './auth';
import { ActionForm, Badge, ErrorBox, Loading, NameFields, Options, readName, useResource } from './components';
import { fullName, roles } from './labels';
import type { User } from './types';

export default function AdminUsers() {
  const { api } = useAuth();
  const [offset, setOffset] = useState(0);
  const [pending, setPending] = useState(true);
  const [revision, setRevision] = useState(0);
  const reload = () => setRevision(r => r + 1);
  const { data, error, loading } = useResource<User[]>(`/admin/users?limit=20&offset=${offset}${pending ? '&pending=true' : ''}`, revision);
  const afterDelete = () => {
    if (data?.length === 1) setOffset(current => current === offset ? Math.max(0, current - 20) : current);
    reload();
  };
  return <><div className="page-heading"><div><span className="eyebrow">ADMINISTRATION</span><h1>User accounts</h1><p className="muted">Approve accounts and assign roles.</p></div></div><section className="panel"><div className="toolbar"><label className="check"><input type="checkbox" checked={pending} onChange={e => { setPending(e.target.checked); setOffset(0); }} />Pending only</label><button className="secondary" onClick={reload}>Refresh</button></div>
    <ErrorBox error={error} />{loading && <Loading />}{data?.length === 0 && <p className="empty">No accounts to display.</p>}
    {data?.map(user => <article className="user-row" key={user.id}><div><h2>{fullName(user) || `User #${user.id}`}</h2><div className="badges"><Badge>{user.is_approved ? 'Approved' : 'Pending approval'}</Badge><Badge>{user.is_active ? 'Active' : 'Inactive'}</Badge>{user.role && <Badge>{roles[user.role]}</Badge>}</div>
      <details className="user-name-editor"><summary>{fullName(user) ? 'Edit name' : 'Add name'}</summary>
        <ActionForm title="Account name" submit="Save name" action={form => api(`/admin/users/${user.id}/name`, { method: 'PATCH', body: JSON.stringify(readName(form)) })} onSuccess={reload}>
          <NameFields person={user} />
        </ActionForm>
      </details></div>
      <ActionForm title={user.is_approved ? 'Change role' : 'Account approval'} submit={user.is_approved ? 'Change role' : 'Approve account'} action={form => api(`/admin/users/${user.id}/${user.is_approved ? 'role' : 'approve'}`, { method: user.is_approved ? 'PATCH' : 'POST', body: JSON.stringify({ role: form.get('role') }) })} onSuccess={reload}>
        <label>Role<select name="role" defaultValue={user.role || ''} required><option value="">Select a role</option><Options values={roles} /></select></label></ActionForm>
      {user.is_approved ? <ActionForm title="Account status" submit={user.is_active ? 'Deactivate' : 'Activate'} action={() => api(`/admin/users/${user.id}/active`, { method: 'PATCH', body: JSON.stringify({ is_active: !user.is_active }) })} onSuccess={reload}><p className="hint">Changes apply to active sessions.</p></ActionForm>
        : <ActionForm title="Reject registration" submit="Delete pending account" action={() => api(`/admin/users/${user.id}`, { method: 'DELETE' })} onSuccess={afterDelete}>
          <p className="hint">Permanently deletes this pending registration.</p>
        </ActionForm>}
    </article>)}<div className="pagination"><button className="secondary" disabled={loading || offset === 0} onClick={() => setOffset(o => o - 20)}>← Previous</button><button className="secondary" disabled={loading || !data || data.length < 20} onClick={() => setOffset(o => o + 20)}>Next →</button></div>
  </section></>;
}

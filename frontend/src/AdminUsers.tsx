import { useState } from 'react';
import { useAuth } from './auth';
import { ActionForm, Badge, ErrorBox, Loading, Options, useResource } from './components';
import { roles } from './labels';
import type { User } from './types';

export default function AdminUsers() {
  const { api } = useAuth();
  const [offset, setOffset] = useState(0);
  const [pending, setPending] = useState(true);
  const [revision, setRevision] = useState(0);
  const reload = () => setRevision(r => r + 1);
  const { data, error, loading } = useResource<User[]>(`/admin/users?limit=20&offset=${offset}${pending ? '&pending=true' : ''}`, revision);
  return <><div className="page-heading"><div><span className="eyebrow">ADMINISTRATION</span><h1>User accounts</h1><p className="muted">Approve accounts and assign roles.</p></div></div><section className="panel"><div className="toolbar"><label className="check"><input type="checkbox" checked={pending} onChange={e => { setPending(e.target.checked); setOffset(0); }} />Pending only</label><button className="secondary" onClick={reload}>Refresh</button></div>
    <ErrorBox error={error} />{loading && <Loading />}{data?.length === 0 && <p className="empty">No accounts to display.</p>}
    {data?.map(user => <article className="user-row" key={user.id}><div><h2>{user.email}</h2><div className="badges"><Badge>{user.is_approved ? 'Approved' : 'Pending approval'}</Badge><Badge>{user.is_active ? 'Active' : 'Inactive'}</Badge>{user.role && <Badge>{roles[user.role]}</Badge>}</div></div>
      <ActionForm title={user.is_approved ? 'Change role' : 'Account approval'} submit={user.is_approved ? 'Change role' : 'Approve account'} action={form => api(`/admin/users/${user.id}/${user.is_approved ? 'role' : 'approve'}`, { method: user.is_approved ? 'PATCH' : 'POST', body: JSON.stringify({ role: form.get('role') }) })} onSuccess={reload}>
        <label>Role<select name="role" defaultValue={user.role || ''} required><option value="">Select a role</option><Options values={roles} /></select></label></ActionForm>
      <ActionForm title="Account status" submit={user.is_active ? 'Deactivate' : 'Activate'} action={() => api(`/admin/users/${user.id}/active`, { method: 'PATCH', body: JSON.stringify({ is_active: !user.is_active }) })} onSuccess={reload}><p className="hint">Changes apply to active sessions.</p></ActionForm>
    </article>)}<div className="pagination"><button className="secondary" disabled={loading || offset === 0} onClick={() => setOffset(o => o - 20)}>← Previous</button><button className="secondary" disabled={loading || !data || data.length < 20} onClick={() => setOffset(o => o + 20)}>Next →</button></div>
  </section></>;
}

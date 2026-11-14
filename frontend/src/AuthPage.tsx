import { useEffect, useState, type FormEvent } from 'react';
import { Link, Navigate, useNavigate } from 'react-router';
import { useAuth } from './auth';
import { request } from './api';
import { ErrorBox } from './components';

export default function AuthPage({ register = false }: { register?: boolean }) {
  const { user, login, message } = useAuth();
  const navigate = useNavigate();
  const [domain, setDomain] = useState('');
  const [configError, setConfigError] = useState<unknown>(null);
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);
  const [registered, setRegistered] = useState(false);
  useEffect(() => {
    const controller = new AbortController();
    if (register) request<{ allowed_email_domain: string }>('/auth/config', { signal: controller.signal })
      .then(data => setDomain(data.allowed_email_domain))
      .catch(error => { if (!controller.signal.aborted) setConfigError(error); });
    return () => controller.abort();
  }, [register]);
  if (user) return <Navigate to="/tickets" replace />;
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setBusy(true); setError(null);
    try {
      const email = String(form.get('email')).trim();
      const password = String(form.get('password'));
      if (register) {
        if (password !== form.get('repeat')) throw new Error('The passwords must match.');
        await request('/auth/register', { method: 'POST', body: JSON.stringify({ email, password }) });
        setRegistered(true);
      } else { await login(email, password); navigate('/tickets'); }
    } catch (error) { setError(error); }
    finally { setBusy(false); }
  }
  return <div className="auth-layout"><section className="auth-intro">
    <h1>IT help desk</h1><p>Report an IT issue and track it through resolution.</p>
    <div className="intro-note"><span className="intro-symbol">↗</span><div><strong>Ticket history</strong><br /><span>See updates as your ticket progresses.</span></div></div></section>
    <section className="panel auth-panel"><span className="eyebrow">ISSUETRACKER</span><h2>{register ? 'Create an account' : 'Sign in'}</h2>
      <p className="muted">{register ? 'An administrator must approve your account after registration.' : 'Sign in to view your tickets.'}</p>
      {!register && message && <div className="notice" role="status">{message}</div>}
      <ErrorBox error={configError} /><ErrorBox error={error} />
      {registered ? <div className="notice success" role="status">Your account was created. You can sign in once an administrator approves it.<p><Link to="/login">Go to sign in →</Link></p></div>
        : <form onSubmit={submit}><fieldset disabled={busy}>
          <label>Email address<input name="email" type="email" autoComplete="username" maxLength={254} required placeholder={domain ? `name@${domain}` : 'name@example.com'} /></label>
          {register && <p className="hint">{domain ? `Required domain: @${domain}` : 'Loading the required domain…'}</p>}
          <label>Password<input name="password" type="password" autoComplete={register ? 'new-password' : 'current-password'} minLength={register ? 12 : undefined} maxLength={128} required /></label>
          {register && <><p className="hint">12 to 128 characters.</p><label>Confirm password<input name="repeat" type="password" autoComplete="new-password" minLength={12} maxLength={128} required /></label></>}
          <button className="wide" type="submit" disabled={register && !domain}>{busy ? 'Please wait…' : register ? 'Register' : 'Sign in →'}</button>
        </fieldset></form>}
      <p className="auth-switch">{register ? 'Already have an account? ' : 'New here? '}<Link to={register ? '/login' : '/register'}>{register ? 'Sign in' : 'Create an account'}</Link></p>
      <p className="hint">Refreshing the page requires you to sign in again.</p>
    </section></div>;
}

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
        if (password !== form.get('repeat')) throw new Error('Podane hasła muszą być takie same.');
        await request('/auth/register', { method: 'POST', body: JSON.stringify({ email, password }) });
        setRegistered(true);
      } else { await login(email, password); navigate('/tickets'); }
    } catch (error) { setError(error); }
    finally { setBusy(false); }
  }
  return <div className="auth-layout"><section className="auth-intro"><span className="eyebrow">POMOC TECHNICZNA · IT</span>
    <h1>Problemy IT<br />pod kontrolą.</h1><p>Zgłoś problem, śledź postępy i wróć do pracy. Wszystkie informacje o sprawie w jednym miejscu.</p>
    <div className="intro-note"><span className="intro-symbol">↗</span><div><strong>Od zgłoszenia do rozwiązania</strong><br /><span>Przejrzysta historia na każdym etapie.</span></div></div></section>
    <section className="panel auth-panel"><span className="eyebrow">ISSUETRACKER</span><h2>{register ? 'Utwórz konto' : 'Dobrze Cię widzieć'}</h2>
      <p className="muted">{register ? 'Po rejestracji administrator zaakceptuje Twoje konto.' : 'Zaloguj się, aby przejść do zgłoszeń.'}</p>
      {!register && message && <div className="notice" role="status">{message}</div>}
      <ErrorBox error={configError} /><ErrorBox error={error} />
      {registered ? <div className="notice success" role="status">Konto zostało utworzone. Oczekuje na akceptację administratora. Po akceptacji możesz się zalogować.<p><Link to="/login">Przejdź do logowania →</Link></p></div>
        : <form onSubmit={submit}><fieldset disabled={busy}>
          <label>Adres e-mail<input name="email" type="email" autoComplete="username" maxLength={254} required placeholder={domain ? `imie@${domain}` : 'imie@firma.pl'} /></label>
          {register && <p className="hint">{domain ? `Wymagana domena: @${domain}` : 'Pobieranie wymaganej domeny…'}</p>}
          <label>Hasło<input name="password" type="password" autoComplete={register ? 'new-password' : 'current-password'} minLength={register ? 12 : undefined} maxLength={128} required /></label>
          {register && <><p className="hint">Od 12 do 128 znaków.</p><label>Powtórz hasło<input name="repeat" type="password" autoComplete="new-password" minLength={12} maxLength={128} required /></label></>}
          <button className="wide" type="submit" disabled={register && !domain}>{busy ? 'Proszę czekać…' : register ? 'Zarejestruj się' : 'Zaloguj się →'}</button>
        </fieldset></form>}
      <p className="auth-switch">{register ? 'Masz już konto? ' : 'Pierwsza wizyta? '}<Link to={register ? '/login' : '/register'}>{register ? 'Zaloguj się' : 'Utwórz konto'}</Link></p>
      <p className="hint">Sesja trwa do wygaśnięcia tokenu. Odświeżenie strony wymaga ponownego logowania.</p>
    </section></div>;
}

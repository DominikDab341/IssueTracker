import { Link, Navigate, NavLink, Outlet, Route, Routes, useLocation, useParams } from 'react-router';
import { useAuth } from './auth';
import AuthPage from './AuthPage';
import TicketList from './TicketList';
import TicketEditor from './TicketEditor';
import TicketDetail from './TicketDetail';
import AdminUsers from './AdminUsers';
import { roles } from './labels';

function Shell() {
  const { user, logout } = useAuth();
  const location = useLocation();
  if (!user) return <Navigate to="/login" replace />;
  return <div className="app-shell"><aside className="sidebar"><Link className="brand" to="/tickets"><span className="brand-icon">it</span>IssueTracker<span className="brand-dot">.</span></Link><span className="sidebar-caption">PRZESTRZEŃ ROBOCZA</span><nav><NavLink to="/tickets" end>▤ <span>Zgłoszenia</span></NavLink><NavLink to="/tickets/new">＋ <span>Nowe zgłoszenie</span></NavLink>{user.role === 'admin' && <NavLink to="/admin/users">♙ <span>Użytkownicy</span></NavLink>}</nav><div className="sidebar-bottom"><span className="live-dot" /> Pomoc techniczna IT<br /><small>Jeden problem. Wspólne rozwiązanie.</small></div></aside>
    <div className="workspace"><header className="topbar"><span className="topbar-label">Panel zgłoszeń <span className="muted">/ {location.pathname.includes('/new') ? 'Nowe zgłoszenie' : location.pathname.includes('/admin') ? 'Użytkownicy' : 'Przegląd'}</span></span><div className="account"><span className="avatar">{user.email[0].toUpperCase()}</span><span><strong>{user.email}</strong><small>{user.role && roles[user.role]}</small></span><button className="text-button" onClick={logout}>Wyloguj</button></div></header>
      <main><Outlet /></main><footer>IssueTracker <span>Wsparcie IT, krok po kroku.</span></footer></div></div>;
}
function AdminRoute() {
  const { user } = useAuth();
  return user?.role === 'admin' ? <AdminUsers /> : <div className="panel"><h1>Brak dostępu</h1><p>Ta strona jest dostępna dla administratora.</p><Link to="/tickets">Wróć do zgłoszeń</Link></div>;
}
function DetailRoute() {
  const { id } = useParams();
  return <TicketDetail key={id} />;
}
export default function App() {
  return <Routes><Route path="/login" element={<AuthPage key="login" />} /><Route path="/register" element={<AuthPage key="register" register />} />
    <Route element={<Shell />}><Route index element={<Navigate to="/tickets" replace />} /><Route path="tickets" element={<TicketList />} /><Route path="tickets/new" element={<><div className="page-heading"><div><span className="eyebrow">POMOC ZACZYNA SIĘ TUTAJ</span><h1>Nowe zgłoszenie</h1><p className="muted">Opisz problem. Zajmiemy się resztą.</p></div></div><section className="panel editor-panel"><TicketEditor /></section></>} /><Route path="tickets/:id" element={<DetailRoute />} /><Route path="admin/users" element={<AdminRoute />} /><Route path="*" element={<div className="panel"><h1>Nie znaleziono strony</h1><Link to="/tickets">Wróć do zgłoszeń →</Link></div>} /></Route>
  </Routes>;
}

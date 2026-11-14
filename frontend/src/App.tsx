import { Link, Navigate, NavLink, Outlet, Route, Routes, useLocation, useParams } from 'react-router';
import { useAuth } from './auth';
import AuthPage from './AuthPage';
import TicketList from './TicketList';
import TicketEditor from './TicketEditor';
import TicketDetail from './TicketDetail';
import Assistant from './Assistant';
import AdminUsers from './AdminUsers';
import { fullName, roles } from './labels';

function Shell() {
  const { user, logout } = useAuth();
  const location = useLocation();
  if (!user) return <Navigate to="/login" replace />;
  const name = fullName(user) || `User #${user.id}`;
  const initials = `${Array.from(user.first_name ?? '')[0] ?? ''}${Array.from(user.last_name ?? '')[0] ?? ''}`.toUpperCase();
  return <div className="app-shell"><aside className="sidebar"><Link className="brand" to="/tickets" aria-label="IT Help Desk"><span className="brand-icon" aria-hidden="true">IT</span>Help Desk</Link><span className="sidebar-caption">WORKSPACE</span><nav><NavLink to="/tickets" end>▤ <span>Tickets</span></NavLink><NavLink to="/tickets/new">＋ <span>New ticket</span></NavLink>{(user.role === 'admin' || user.role === 'staff') && <NavLink to="/assistant">◇ <span>AI Assistant</span></NavLink>}{user.role === 'admin' && <NavLink to="/admin/users">♙ <span>Users</span></NavLink>}</nav><div className="sidebar-bottom"><span className="live-dot" /> IT Help Desk</div></aside>
    <div className="workspace"><header className="topbar"><span className="topbar-label">Ticket desk <span className="muted">/ {location.pathname.includes('/new') ? 'New ticket' : location.pathname.includes('/admin') ? 'Users' : location.pathname === '/assistant' ? 'AI Assistant' : 'Overview'}</span></span><div className="account"><span className="avatar" aria-hidden="true">{initials}</span><span><strong>{name}</strong><small>{user.role && roles[user.role]}</small></span><button className="text-button" onClick={logout}>Sign out</button></div></header>
      <main><Outlet /></main><footer>IT Help Desk</footer></div></div>;
}
function AdminRoute() {
  const { user } = useAuth();
  return user?.role === 'admin' ? <AdminUsers /> : <div className="panel"><h1>Access denied</h1><p>This page is available to administrators.</p><Link to="/tickets">Back to tickets</Link></div>;
}
function AssistantRoute() {
  const { user } = useAuth();
  return user?.role === 'staff' || user?.role === 'admin'
    ? <Assistant key={user.id} />
    : <div className="panel"><h1>Access denied</h1><p>The assistant is available to staff and administrators.</p><Link to="/tickets">Back to tickets</Link></div>;
}
function DetailRoute() {
  const { id } = useParams();
  return <TicketDetail key={id} />;
}
function NewTicketPage() {
  return <div className="new-ticket-page">
    <div className="page-heading"><h1>New ticket</h1></div>
    <section className="panel editor-panel"><TicketEditor /></section>
  </div>;
}
export default function App() {
  return <Routes><Route path="/login" element={<AuthPage key="login" />} /><Route path="/register" element={<AuthPage key="register" register />} />
    <Route element={<Shell />}><Route index element={<Navigate to="/tickets" replace />} /><Route path="tickets" element={<TicketList />} /><Route path="tickets/new" element={<NewTicketPage />} /><Route path="tickets/:id" element={<DetailRoute />} /><Route path="assistant" element={<AssistantRoute />} /><Route path="admin/users" element={<AdminRoute />} /><Route path="*" element={<div className="panel"><h1>Page not found</h1><Link to="/tickets">Back to tickets →</Link></div>} /></Route>
  </Routes>;
}

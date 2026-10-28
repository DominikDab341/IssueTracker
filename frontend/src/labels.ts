import type { Ticket, User, Task } from './types';

export const statuses = { reported: 'Zgłoszony', accepted: 'Przyjęty', in_progress: 'W trakcie', resolved: 'Rozwiązany', rejected: 'Odrzucony', cancelled: 'Anulowany' };
export const categories: Record<string, string> = { bug: 'Błąd', performance: 'Wydajność', feature: 'Nowa funkcja', unknown: 'Do weryfikacji' };
export const priorities: Record<string, string> = { low: 'Niski', medium: 'Średni', high: 'Wysoki', critical: 'Krytyczny', unknown: 'Nieustalony' };
export const roles = { reporter: 'Zgłaszający', staff: 'Obsługa', admin: 'Administrator' };
export const taskStates = { pending: 'Oczekuje', running: 'W toku', succeeded: 'Zakończone', failed: 'Błąd' };
export const sources: Record<string, string> = { administrator: 'Decyzja administratora', work_blocked: 'Blokada pracy', automatic: 'Klasyfikacja automatyczna', fallback: 'Tymczasowy', legacy: 'Dane historyczne' };
export function date(value: string | null) {
  return value ? new Intl.DateTimeFormat('pl-PL', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value)) : '—';
}
export const person = (id: number | null) => id ? `Użytkownik #${id}` : 'Nie przypisano';
export const active = (ticket: Ticket) => ['reported', 'accepted', 'in_progress'].includes(ticket.status);
export function permissions(user: User, ticket: Ticket, task?: Task | null) {
  const admin = user.role === 'admin';
  const staff = user.role === 'staff';
  const assigned = staff && user.id === ticket.assignee_id;
  const own = user.id === ticket.author_id;
  return {
    edit: own && ticket.status === 'reported',
    cancel: own && ticket.status === 'reported' && ticket.assignee_id === null,
    accept: staff && ticket.status === 'reported' && ticket.assignee_id === null,
    assign: admin && active(ticket),
    start: (admin || assigned) && ticket.status === 'accepted',
    resolve: (admin || assigned) && ticket.status === 'in_progress',
    reject: (admin && active(ticket)) || (staff && ticket.status === 'reported'),
    priority: admin,
    category: admin || assigned,
    retry: active(ticket) && task?.current === true && task.state === 'failed'
      && ['processing_failed', 'interrupted'].includes(task.error_code ?? '')
      && (admin || (own && ticket.status === 'reported' && ticket.assignee_id === null)
        || (assigned && ['accepted', 'in_progress'].includes(ticket.status))),
  };
}

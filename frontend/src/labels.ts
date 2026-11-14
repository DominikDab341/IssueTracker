import type { Ticket, User, Task } from './types';

export const statuses = { reported: 'Reported', accepted: 'Accepted', in_progress: 'In progress', resolved: 'Resolved', rejected: 'Rejected', cancelled: 'Cancelled' };
export const categories: Record<string, string> = { accounts_access: 'Accounts and access', hardware: 'Hardware', network: 'Network and connectivity', software: 'Software', unknown: 'Needs review' };
export const priorities: Record<string, string> = { low: 'Low', medium: 'Medium', high: 'High', critical: 'Critical', unknown: 'Undetermined' };
export const roles = { reporter: 'Reporter', staff: 'Staff', admin: 'Administrator' };
export const taskStates = { pending: 'Pending', running: 'Running', succeeded: 'Completed', failed: 'Failed' };
export const sources: Record<string, string> = { administrator: 'Administrator decision', work_blocked: 'Work blocked', automatic: 'Automatic classification', fallback: 'Provisional', legacy: 'Legacy data', escalation: 'Similar-ticket escalation' };
export const reviewReasons: Record<string, string> = {
  no_references: 'No reference examples are available.',
  low_category_similarity: 'The description is a weak match for the category examples.',
  split_category_vote: 'Similar examples point to different categories.',
  no_known_priority_terms: 'The priority classifier did not recognize any terms in the description.',
  low_priority_score: 'The priority classifier score is too low for an automatic decision.',
  sparse_priority_information: 'Add how the issue affects work and whether a workaround is available.',
};
export function date(value: string | null) {
  return value ? new Intl.DateTimeFormat('en-GB', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value)) : '—';
}
export const person = (id: number | null) => id ? `User #${id}` : 'Unassigned';
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

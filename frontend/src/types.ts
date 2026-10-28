export type Role = 'reporter' | 'staff' | 'admin';
export type Status = 'reported' | 'accepted' | 'in_progress' | 'resolved' | 'rejected' | 'cancelled';
export type TaskState = 'pending' | 'running' | 'succeeded' | 'failed';
export interface User {
  id: number; email: string; role: Role | null; is_active: boolean; is_approved: boolean;
}
export interface Ticket {
  id: number; text: string; author_id: number | null; assignee_id: number | null;
  status: Status; category: string; priority: string; priority_source: string;
  work_blocked: boolean; content_version: number; classification_current: boolean;
  current_task_id: string | null; current_task_state: TaskState | null; needs_review: boolean;
  predicted_category: string | null; predicted_category_version: number | null;
  manual_category: string | null; manual_category_current: boolean;
  manual_category_by_id: number | null; manual_category_at: string | null;
  manual_priority_by_id: number | null; manual_priority_at: string | null;
  base_priority: string | null; created_at: string; updated_at: string;
  resolution_note: string | null; resolved_by_id: number | null; resolved_at: string | null;
  rejection_reason: string | null; rejected_by_id: number | null; rejected_at: string | null;
}
export interface Task {
  task_id: string; state: TaskState; current: boolean; content_version: number;
  error_code: string | null; error: string | null;
}
export interface Duplicate { id: number; text: string; similarity: number }

import { describe, expect, it } from 'vitest';
import { permissions } from './labels';
import type { Ticket, User, Task, Status } from './types';

const user = (role: User['role'], id = 1) => ({ id, role, email: 'test@mail.com', is_active: true, is_approved: true });
const ticket = (status: Status, assignee_id: number | null = null) => ({ author_id: 1, assignee_id, status }) as Ticket;
const failed = { current: true, state: 'failed', error_code: 'interrupted' } as Task;
describe('role and workflow actions', () => {
  it('locks author editing/cancellation and retry after acceptance', () => {
    expect(permissions(user('reporter'), ticket('reported'), failed)).toMatchObject({ edit: true, cancel: true, retry: true, accept: false });
    expect(permissions(user('reporter'), ticket('accepted', 2), failed)).toMatchObject({ edit: false, cancel: false, retry: false });
    expect(permissions(user('reporter', 3), ticket('reported'), failed)).toMatchObject({ edit: false, cancel: false, retry: false });
  });
  it('only current assignee can handle a ticket and steps cannot be skipped', () => {
    expect(permissions(user('staff'), ticket('reported'), failed)).toMatchObject({ accept: true, start: false, resolve: false });
    expect(permissions(user('staff'), ticket('accepted', 1), failed)).toMatchObject({ start: true, resolve: false, category: true, retry: true });
    expect(permissions(user('staff', 2), ticket('in_progress', 1), failed)).toMatchObject({ start: false, resolve: false, category: false, retry: false, reject: false });
    expect(permissions(user('staff'), ticket('in_progress', 1), failed)).toMatchObject({ resolve: true, start: false });
  });
  it('administrator assigns instead of accepting and respects final statuses', () => {
    expect(permissions(user('admin'), ticket('reported'), failed)).toMatchObject({ accept: false, assign: true, start: false, resolve: false, priority: true });
    for (const status of ['resolved', 'rejected', 'cancelled'] as Status[]) {
      expect(permissions(user('admin'), ticket(status), failed)).toMatchObject({ retry: false, assign: false, start: false, resolve: false, reject: false });
    }
  });
  it('never retries a successful, obsolete or superseded task', () => {
    for (const task of [null, { ...failed, current: false }, { ...failed, state: 'succeeded' }, { ...failed, error_code: 'superseded' }]) {
      expect(permissions(user('admin'), ticket('reported'), task as Task | null).retry).toBe(false);
    }
  });
});

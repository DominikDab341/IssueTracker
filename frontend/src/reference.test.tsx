import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import TicketDetail from './TicketDetail';

const { api, state, reload } = vi.hoisted(() => ({
  api: vi.fn(), reload: vi.fn(),
  state: { role: 'staff', id: 2 },
}));
vi.mock('./auth', () => ({ useAuth: () => ({ api, user: { ...state, is_active: true, is_approved: true } }) }));
vi.mock('./useTicket', () => ({ useTicket: () => ({
  ticket: { id: 1, text: 'Printer motor replaced', status: 'resolved', assignee_id: 2, author_id: 3,
    category: 'hardware', priority: 'critical', base_priority: 'high', priority_source: 'work_blocked',
    content_version: 4, current_task_state: 'succeeded', classification_current: true, needs_review: false,
    predicted_category_version: 4, created_at: '2026-11-07T10:00:00Z', updated_at: '2026-11-07T10:00:00Z' },
  task: null, duplicates: [], error: null, extraError: null, loading: false, reload,
}) }));

beforeEach(() => { api.mockReset(); reload.mockReset(); state.role = 'staff'; state.id = 2; api.mockResolvedValue(null); });
afterEach(cleanup);

it('requires an explicit reference category and base priority instead of copying final critical', async () => {
  render(<MemoryRouter><TicketDetail /></MemoryRouter>);
  const category = await screen.findByLabelText('Kategoria referencyjna') as HTMLSelectElement;
  const priority = screen.getByLabelText('Priorytet bazowy referencji') as HTMLSelectElement;
  expect(category.value).toBe('');
  expect(priority.value).toBe('');
  fireEvent.change(category, { target: { value: 'hardware' } });
  fireEvent.change(priority, { target: { value: 'low' } });
  fireEvent.submit(priority.closest('form')!);
  await waitFor(() => expect(api).toHaveBeenCalledWith('/tickets/1/reference', {
    method: 'POST', body: JSON.stringify({ category: 'hardware', base_priority: 'low', expected_content_version: 4 }),
  }));
  expect(reload).toHaveBeenCalled();
});

it('does not show approval controls to another assignee or a reporter', async () => {
  state.id = 9;
  const view = render(<MemoryRouter><TicketDetail /></MemoryRouter>);
  await screen.findByText(/Może to zrobić aktualny wykonawca/);
  expect(screen.queryByRole('button', { name: 'Dodaj do referencji' })).toBeNull();
  view.unmount(); api.mockClear(); state.role = 'reporter'; state.id = 3;
  render(<MemoryRouter><TicketDetail /></MemoryRouter>);
  expect(screen.queryByRole('heading', { name: 'Przykład referencyjny' })).toBeNull();
  expect(api).not.toHaveBeenCalled();
});

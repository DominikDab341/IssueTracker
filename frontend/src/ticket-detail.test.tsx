import { cleanup, fireEvent, render, screen, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { afterEach, expect, it, vi } from 'vitest';
import TicketDetail from './TicketDetail';

const { api } = vi.hoisted(() => ({ api: vi.fn() }));
vi.mock('./auth', () => ({ useAuth: () => ({ api, user: { id: 1, role: 'admin' } }) }));
vi.mock('./useTicket', () => ({ useTicket: () => ({
  ticket: {
    id: 10, text: 'The printer jams.', status: 'reported', author_id: 3,
    category: 'hardware', priority: 'medium', classification_current: true, content_version: 1,
  },
  duplicates: [], reload: vi.fn(),
}) }));

afterEach(() => { cleanup(); api.mockReset(); });

it('allows assigning staff from beyond the first page without pagination buttons', async () => {
  const firstPage = Array.from({ length: 100 }, (_, index) => ({ id: index + 100, email: `staff${index}@example.test` }));
  api.mockImplementation(async (path: string) => {
    if (path === '/admin/assignees?limit=100&offset=0') return firstPage;
    if (path === '/admin/assignees?limit=100&offset=100') return [{ id: 200, email: 'last@example.test' }];
    if (path === '/tickets/10/assignee') return {};
    throw new Error(`Unexpected request to ${path}`);
  });

  render(<MemoryRouter><TicketDetail /></MemoryRouter>);
  const lastOption = await screen.findByRole('option', { name: 'last@example.test (#200)' });
  const form = lastOption.closest('form')!;
  expect(within(form).queryByRole('button', { name: /previous staff|next staff/i })).toBeNull();
  fireEvent.change(within(form).getByRole('combobox', { name: 'Assignee' }), { target: { value: '200' } });
  fireEvent.click(within(form).getByRole('button', { name: 'Save' }));
  expect(api).toHaveBeenCalledWith('/tickets/10/assignee', { method: 'PATCH', body: '{"assignee_id":200}' });
  await within(form).findByText('Changes saved.');
});

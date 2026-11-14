import { cleanup, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { afterEach, expect, it, vi } from 'vitest';
import TicketDetail from './TicketDetail';

const { api } = vi.hoisted(() => ({ api: vi.fn() }));
vi.mock('./auth', () => ({ useAuth: () => ({ api, user: { id: 2, role: 'staff' } }) }));
vi.mock('./useTicket', () => ({ useTicket: () => ({
  ticket: {
    id: 1, text: 'Printer would not feed paper.', status: 'resolved', assignee_id: 2, author_id: 3,
    category: 'hardware', priority: 'low', base_priority: 'low', priority_source: 'automatic',
    content_version: 1, resolution_note: 'Replaced the feed roller.', classification_current: true,
    predicted_category_version: 1, created_at: '2026-11-07T10:00:00Z', updated_at: '2026-11-07T10:00:00Z',
  },
  task: null, duplicates: [], error: null, extraError: null, loading: false, reload: vi.fn(),
}) }));

afterEach(cleanup);

it('shows the resolution without loading or rendering a manual reference form', () => {
  render(<MemoryRouter><TicketDetail /></MemoryRouter>);
  expect(screen.getByText('Replaced the feed roller.')).toBeTruthy();
  expect(screen.queryByRole('heading', { name: 'Reference example' })).toBeNull();
  expect(screen.queryByRole('button', { name: 'Add as a reference' })).toBeNull();
  expect(api).not.toHaveBeenCalled();
});

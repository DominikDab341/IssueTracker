// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { afterEach, expect, it, vi } from 'vitest';
import Assistant from './Assistant';

const { api } = vi.hoisted(() => ({ api: vi.fn() }));
vi.mock('./auth', () => ({ useAuth: () => ({ api }) }));
afterEach(() => { cleanup(); api.mockReset(); });

it('links cited tickets and keeps follow-up context in the current view', async () => {
  api.mockResolvedValue({
    parts: [{ text: 'Updated the VPN client.', ticket_id: 42 }], message: null,
  });
  const view = render(<MemoryRouter><Assistant /></MemoryRouter>);
  fireEvent.change(screen.getByLabelText('Question'), { target: { value: 'How did we fix VPN disconnects?' } });
  fireEvent.click(screen.getByRole('button', { name: 'Send question' }));
  const source = await screen.findByRole('link', { name: 'Ticket #42' });
  expect(source.getAttribute('href')).toBe('/tickets/42');
  fireEvent.change(screen.getByLabelText('Question'), { target: { value: 'What exactly was updated?' } });
  fireEvent.click(screen.getByRole('button', { name: 'Send question' }));
  expect(JSON.parse(api.mock.calls[1][1].body).previous_questions).toEqual(['How did we fix VPN disconnects?']);
  await waitFor(() => expect(screen.getAllByRole('link', { name: 'Ticket #42' })).toHaveLength(2));
  view.unmount();
  render(<MemoryRouter><Assistant /></MemoryRouter>);
  expect(screen.queryByRole('link', { name: 'Ticket #42' })).toBeNull();
});

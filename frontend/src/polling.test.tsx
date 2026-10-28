import { act, cleanup, renderHook } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { useTicket } from './useTicket';

const { api } = vi.hoisted(() => ({ api: vi.fn() }));
vi.mock('./auth', () => ({ useAuth: () => ({ api }) }));
beforeEach(() => { vi.useFakeTimers(); api.mockReset(); });
afterEach(() => { cleanup(); vi.useRealTimers(); });
it('polls sequentially and stops after task completion', async () => {
  let state = 'pending';
  api.mockImplementation((path: string) => Promise.resolve(path.endsWith('/duplicates') ? [] : path.includes('/task/') ? { state } : { id: 1, current_task_id: 'task-1', current_task_state: state }));
  const { result } = renderHook(() => useTicket('1'));
  await act(async () => { await Promise.resolve(); });
  expect(api).toHaveBeenCalledTimes(3);
  await act(async () => { await vi.advanceTimersByTimeAsync(2999); });
  expect(api).toHaveBeenCalledTimes(3);
  state = 'succeeded';
  await act(async () => { await vi.advanceTimersByTimeAsync(1); });
  expect(result.current.task?.state).toBe('succeeded');
  expect(api).toHaveBeenCalledTimes(6);
  await act(async () => { await vi.advanceTimersByTimeAsync(30000); });
  expect(api).toHaveBeenCalledTimes(6);
});
it('aborts requests and clears timers on leaving the detail view', async () => {
  api.mockResolvedValue({ current_task_id: null, current_task_state: 'pending' });
  const { unmount } = renderHook(() => useTicket('1'));
  await act(async () => { await Promise.resolve(); });
  const signal = api.mock.calls[0][1].signal as AbortSignal;
  const count = api.mock.calls.length;
  unmount();
  expect(signal.aborted).toBe(true);
  await act(async () => { await vi.advanceTimersByTimeAsync(30000); });
  expect(api).toHaveBeenCalledTimes(count);
});
it('stops on an API failure and offers explicit reload', async () => {
  api.mockRejectedValue(new Error('API niedostępne'));
  const { result } = renderHook(() => useTicket('1'));
  await act(async () => { await Promise.resolve(); });
  expect(result.current.loading).toBe(false);
  expect(result.current.error).toBeInstanceOf(Error);
  await act(async () => { await vi.advanceTimersByTimeAsync(30000); });
  expect(api).toHaveBeenCalledTimes(1);
  await act(async () => result.current.reload());
  expect(api).toHaveBeenCalledTimes(2);
});

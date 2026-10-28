import { useCallback, useEffect, useState } from 'react';
import { useAuth } from './auth';
import type { Duplicate, Task, Ticket } from './types';

export function useTicket(id: string) {
  const { api } = useAuth();
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [task, setTask] = useState<Task | null>(null);
  const [duplicates, setDuplicates] = useState<Duplicate[]>([]);
  const [error, setError] = useState<unknown>(null);
  const [extraError, setExtraError] = useState<unknown>(null);
  const [loading, setLoading] = useState(true);
  const [revision, setRevision] = useState(0);
  const reload = useCallback(() => setRevision(r => r + 1), []);
  useEffect(() => {
    let disposed = false;
    let inFlight = false;
    let timer: ReturnType<typeof setTimeout> | undefined;
    const controller = new AbortController();
    // Also refresh decisions/assignees on focus after switching between accounts/windows.
    async function load(initial = false) {
      if (disposed || inFlight) return;
      inFlight = true;
      if (initial) { setLoading(true); setError(null); }
      try {
        const next = await api<Ticket>(`/tickets/${id}`, { signal: controller.signal });
        if (disposed) return;
        setTicket(next); setError(null);
        const extras = await Promise.allSettled([
          next.current_task_id ? api<Task>(`/tickets/${id}/task/${next.current_task_id}`, { signal: controller.signal }) : Promise.resolve(null),
          api<Duplicate[]>(`/tickets/${id}/duplicates`, { signal: controller.signal }),
        ]);
        if (disposed) return;
        setTask(extras[0].status === 'fulfilled' ? extras[0].value : null);
        setDuplicates(extras[1].status === 'fulfilled' ? extras[1].value : []);
        const failure = extras.find(item => item.status === 'rejected');
        setExtraError(failure?.status === 'rejected' ? failure.reason : null);
        // Recursive timeout prevents overlapping requests, including slow responses.
        const running = next.current_task_state === 'pending' || next.current_task_state === 'running';
        if (running && !failure) timer = setTimeout(() => load(), 3000);
      } catch (error) { if (!disposed) setError(error); }
      finally { inFlight = false; if (!disposed) setLoading(false); }
    }
    // Requests in the previous effect are aborted; each effect owns its concurrency guard.
    void load(true);
    const focus = () => { if (timer) clearTimeout(timer); void load(); };
    window.addEventListener('focus', focus);
    return () => { disposed = true; controller.abort(); if (timer) clearTimeout(timer); window.removeEventListener('focus', focus); };
  }, [id, revision, api]);
  const currentTicket = ticket && String(ticket.id) === id ? ticket : null;
  return { ticket: currentTicket, task, duplicates, error, extraError, loading, reload };
}

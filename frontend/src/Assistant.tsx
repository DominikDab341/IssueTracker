import { useEffect, useRef, useState, type FormEvent } from 'react';
import { Link } from 'react-router';
import { ApiError } from './api';
import { useAuth } from './auth';

interface ChatResponse {
  parts: { text: string; ticket_id: number }[];
  message: string | null;
}

interface Turn {
  question: string;
  response: ChatResponse;
}

export default function Assistant() {
  const { api } = useAuth();
  const [question, setQuestion] = useState('');
  const [resolvedOnly, setResolvedOnly] = useState(true);
  const [turns, setTurns] = useState<Turn[]>([]);
  const [pending, setPending] = useState('');
  const [error, setError] = useState('');
  const [denied, setDenied] = useState(false);
  const inFlight = useRef<AbortController | null>(null);
  useEffect(() => () => inFlight.current?.abort(), []);

  async function send(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const text = question.trim();
    if (!text || inFlight.current) return;
    const controller = new AbortController();
    inFlight.current = controller;
    setPending(text);
    setError('');
    try {
      const response = await api<ChatResponse>('/assistant/chat', {
        method: 'POST',
        body: JSON.stringify({
          question: text,
          previous_questions: turns.slice(-2).map(turn => turn.question),
          resolved_only: resolvedOnly,
        }),
        signal: controller.signal,
        timeoutMs: 75000,
      });
      setTurns(previous => [...previous, { question: text, response }]);
      setQuestion('');
    } catch (failure) {
      if (controller.signal.aborted) return;
      if (failure instanceof ApiError && failure.status === 403) {
        setTurns([]);
        setQuestion('');
        setDenied(true);
      }
      setError(failure instanceof Error ? failure.message : 'Could not get a response.');
    } finally {
      inFlight.current = null;
      if (!controller.signal.aborted) setPending('');
    }
  }

  return <>
    <div className="page-heading"><div><h1>AI Assistant</h1>
      <p className="muted">Ask about tickets or describe a problem to find similar resolved cases.</p>
    </div></div>
    <section className="panel assistant-panel" aria-label="Assistant conversation">
      <div className="assistant-transcript" role="log" aria-label="Conversation history">
        {turns.map(({ question: text, response }, index) => <article className="assistant-turn" key={index}>
          <p className="assistant-question"><strong>You</strong><br />{text}</p>
          <div><strong>Assistant</strong>
            {response.message && <p>{response.message}</p>}
            {response.parts.map((part, position) => <p key={position}>
              {part.text} <Link to={`/tickets/${part.ticket_id}`}>Ticket #{part.ticket_id}</Link>
            </p>)}
          </div>
        </article>)}
        {pending && <div className="assistant-turn"><p className="assistant-question"><strong>You</strong><br />{pending}</p>
          <p role="status">Searching tickets and preparing an answer…</p></div>}
      </div>
      {error && <p role="alert" className="danger">{error}</p>}
      {!denied && <form onSubmit={send}>
        <label className="check"><input type="checkbox" checked={resolvedOnly} disabled={!!pending}
          onChange={event => setResolvedOnly(event.target.checked)} /> Only tickets with a documented resolution</label>
        <label>Question
          <textarea value={question} maxLength={600} required disabled={!!pending}
            onChange={event => setQuestion(event.target.value)}
            placeholder="How did we fix VPN disconnects after waking a laptop?" />
        </label>
        <button disabled={!!pending || !question.trim()}>Send question</button>
      </form>}
    </section>
  </>;
}

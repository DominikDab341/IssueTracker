import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from 'react';
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
  const transcript = useRef<HTMLDivElement>(null);
  const hasMessages = turns.length > 0 || !!pending;
  useEffect(() => () => inFlight.current?.abort(), []);
  useEffect(() => {
    const log = transcript.current;
    if (log) log.scrollTop = log.scrollHeight;
  }, [turns, pending]);

  function handleQuestionKey(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key !== 'Enter' || event.shiftKey || event.nativeEvent.isComposing) return;
    event.preventDefault();
    if (question.trim() && !inFlight.current) event.currentTarget.form?.requestSubmit();
  }

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

  return <section className="assistant-chat" aria-labelledby="assistant-title">
    <header className={`assistant-heading${hasMessages || denied ? ' assistant-heading-compact' : ''}`}>
      <span className="assistant-mark" aria-hidden="true">✦</span>
      <h1 id="assistant-title">AI Assistant</h1>
      {!hasMessages && !denied && <p>Find fixes in past tickets or ask about an IT issue.</p>}
    </header>

    {hasMessages && <div className="assistant-transcript" ref={transcript} role="log" aria-label="Conversation history" tabIndex={0}>
      {turns.map(({ question: text, response }, index) => <article className="assistant-turn" key={index}>
        <p className="assistant-question" aria-label="Your question">{text}</p>
        <div className="assistant-answer">
          <span className="assistant-mark" aria-hidden="true">✦</span>
          <div className="assistant-answer-body">
            <strong>Assistant</strong>
            {response.message && <p className="assistant-answer-text">{response.message}</p>}
            {response.parts.map((part, position) => <div className="assistant-answer-part" key={position}>
              <p className="assistant-answer-text">{part.text}</p>
              <Link className="assistant-source" to={`/tickets/${part.ticket_id}`}>
                Ticket #{part.ticket_id}<span aria-hidden="true">↗</span>
              </Link>
            </div>)}
          </div>
        </div>
      </article>)}
      {pending && <div className="assistant-turn">
        <p className="assistant-question" aria-label="Your question">{pending}</p>
        <div className="assistant-answer">
          <span className="assistant-mark" aria-hidden="true">✦</span>
          <p className="assistant-progress" role="status">Searching tickets…</p>
        </div>
      </div>}
    </div>}

    {error && <p role="alert" className="notice error assistant-error">{error}</p>}
    {!denied && <form className="assistant-composer" onSubmit={send}>
      <textarea aria-label="Question" value={pending ? '' : question} rows={1}
        maxLength={600} required readOnly={!!pending}
        onChange={event => setQuestion(event.target.value)} onKeyDown={handleQuestionKey}
        placeholder="Ask about a ticket or describe an issue…" />
      <div className="assistant-composer-actions">
        <label className="check"><input type="checkbox" checked={resolvedOnly} disabled={!!pending}
          onChange={event => setResolvedOnly(event.target.checked)} /> Only tickets with a documented resolution</label>
        <button className="assistant-send" type="submit" aria-label="Send question" disabled={!!pending || !question.trim()}>
          <span aria-hidden="true">↑</span>
        </button>
      </div>
    </form>}
  </section>;
}

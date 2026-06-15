import { useEffect, useRef, useState } from 'react';
import './EmailModal.css';

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function EmailModal({ open, onClose }) {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const inputRef = useRef(null);
  const closeBtnRef = useRef(null);

  useEffect(() => {
    if (!open) {
      // Reset state on close
      setEmail('');
      setError('');
      setSubmitted(false);
      return;
    }
    const t = setTimeout(() => inputRef.current?.focus(), 50);
    const onKey = (e) => { if (e.key === 'Escape') onClose?.(); };
    document.addEventListener('keydown', onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      clearTimeout(t);
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = prev;
    };
  }, [open, onClose]);

  if (!open) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = email.trim();
    if (!EMAIL_RE.test(trimmed)) {
      setError('Please enter a valid email address.');
      return;
    }
    setError('');
    // Stubbed submission — wire to a real endpoint later.
    try {
      const key = 'placeholder.signups';
      const existing = JSON.parse(localStorage.getItem(key) || '[]');
      existing.push({ email: trimmed, at: new Date().toISOString() });
      localStorage.setItem(key, JSON.stringify(existing));
    } catch {
      // ignore storage failures
    }
    setSubmitted(true);
  };

  return (
    <div className="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <button
        type="button"
        className="modal__backdrop"
        aria-label="Close"
        onClick={onClose}
      />
      <div className="modal__panel" role="document">
        <button
          ref={closeBtnRef}
          type="button"
          className="modal__close"
          onClick={onClose}
          aria-label="Close dialog"
        >×</button>

        {!submitted ? (
          <>
            <h2 id="modal-title" className="modal__title">Get on the list</h2>
            <p className="modal__sub text-muted">
              Enter your email and we'll be in touch.
            </p>
            <form className="modal__form" onSubmit={handleSubmit} noValidate>
              <label htmlFor="modal-email" className="sr-only">Email</label>
              <input
                ref={inputRef}
                id="modal-email"
                type="email"
                className={`modal__input ${error ? 'has-error' : ''}`}
                placeholder="you@example.com"
                value={email}
                onChange={(e) => { setEmail(e.target.value); if (error) setError(''); }}
                aria-invalid={!!error}
                aria-describedby={error ? 'modal-error' : undefined}
                autoComplete="email"
              />
              {error && (
                <p id="modal-error" className="modal__error" role="alert">{error}</p>
              )}
              <button type="submit" className="btn btn-primary modal__submit">
                Next
              </button>
            </form>
          </>
        ) : (
          <div className="modal__success">
            <h2 id="modal-title" className="modal__title">You're in.</h2>
            <p className="modal__sub text-muted">
              Thanks — we've saved <strong>{email}</strong>. We'll reach out soon.
            </p>
            <button type="button" className="btn btn-primary modal__submit" onClick={onClose}>
              Done
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

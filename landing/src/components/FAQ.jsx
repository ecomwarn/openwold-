import { useState } from 'react';
import { siteConfig } from '../config.js';
import './FAQ.css';

const items = [
  { q: 'Placeholder question one?', a: 'Placeholder answer copy. Replace with your real answer text later.' },
  { q: 'Placeholder question two?', a: 'Placeholder answer copy. Replace with your real answer text later.' },
  { q: 'Placeholder question three?', a: 'Placeholder answer copy. Replace with your real answer text later.' },
  { q: 'Placeholder question four?', a: 'Placeholder answer copy. Replace with your real answer text later.' },
  { q: 'Placeholder question five?', a: 'Placeholder answer copy. Replace with your real answer text later.' },
];

export default function FAQ() {
  const multi = siteConfig.faqMultiOpen;
  const [openSet, setOpenSet] = useState(() => new Set());

  const toggle = (i) => {
    setOpenSet((prev) => {
      const next = new Set(multi ? prev : []);
      if (prev.has(i)) next.delete(i);
      else next.add(i);
      return next;
    });
  };

  return (
    <section id="faq" className="faq">
      <div className="container">
        <p className="section-eyebrow">FAQ</p>
        <h2 className="section-heading">Frequently asked.</h2>

        <ul className="faq__list">
          {items.map((it, i) => {
            const isOpen = openSet.has(i);
            return (
              <li className={`faq__item ${isOpen ? 'is-open' : ''}`} key={i}>
                <button
                  type="button"
                  className="faq__q"
                  aria-expanded={isOpen}
                  aria-controls={`faq-panel-${i}`}
                  onClick={() => toggle(i)}
                >
                  <span>{it.q}</span>
                  <span className="faq__icon" aria-hidden="true">{isOpen ? '–' : '+'}</span>
                </button>
                <div
                  id={`faq-panel-${i}`}
                  className="faq__panel"
                  role="region"
                  hidden={!isOpen}
                >
                  <p className="faq__a text-muted">{it.a}</p>
                </div>
              </li>
            );
          })}
        </ul>
      </div>
    </section>
  );
}

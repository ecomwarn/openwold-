import { useEffect, useState } from 'react';
import './Nav.css';

export default function Nav({ onCtaClick }) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => {
      setScrolled(window.scrollY > window.innerHeight - 80);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <header className={`nav ${scrolled ? 'nav--solid' : 'nav--transparent'}`}>
      <div className="container nav__inner">
        <a href="#top" className="nav__logo" aria-label="Home">
          <span className="nav__logo-mark" aria-hidden="true" />
          <span className="nav__logo-text">Placeholder</span>
        </a>

        <nav className="nav__links" aria-label="Primary">
          <a href="#how-it-works" className="nav__util">How it works</a>
          <a href="#faq" className="nav__util">Support</a>
        </nav>

        <div className="nav__actions">
          <a href="#login" className="nav__login">Log In</a>
          <button type="button" className="btn btn-primary nav__cta" onClick={onCtaClick}>
            Get started
          </button>
        </div>
      </div>
    </header>
  );
}

import './Footer.css';

export default function Footer({ onSignUpClick }) {
  return (
    <footer className="footer">
      <div className="footer__marquee" aria-hidden="true">
        <div className="footer__marquee-track">
          {Array.from({ length: 8 }).map((_, i) => (
            <span className="footer__marquee-item" key={i}>Tagline placeholder · </span>
          ))}
          {Array.from({ length: 8 }).map((_, i) => (
            <span className="footer__marquee-item" key={`b-${i}`}>Tagline placeholder · </span>
          ))}
        </div>
      </div>

      <div className="container footer__inner">
        <div className="footer__cols">
          <div className="footer__col">
            <span className="footer__brand">Placeholder</span>
            <button type="button" className="btn btn-primary footer__signup" onClick={onSignUpClick}>
              Sign up
            </button>
          </div>

          <div className="footer__col">
            <h4 className="footer__heading">Resources</h4>
            <ul className="footer__links">
              <li><a href="#link">Placeholder link</a></li>
              <li><a href="#link">Placeholder link</a></li>
              <li><a href="#link">Placeholder link</a></li>
              <li><a href="#link">Placeholder link</a></li>
            </ul>
          </div>

          <div className="footer__col">
            <h4 className="footer__heading">Follow</h4>
            <ul className="footer__social" aria-label="Social">
              {Array.from({ length: 4 }).map((_, i) => (
                <li key={i}>
                  <a href="#social" className="footer__social-icon" aria-label="Social link">
                    <span className="img-placeholder square" />
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="footer__legal">
          <ul className="footer__legal-links">
            <li><a href="#terms">Terms</a></li>
            <li><a href="#privacy">Privacy</a></li>
            <li><a href="#cookies">Cookies</a></li>
          </ul>
          <p className="footer__copyright text-soft">
            © {new Date().getFullYear()} Placeholder. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}

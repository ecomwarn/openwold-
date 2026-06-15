import { siteConfig } from '../config.js';
import './Hero.css';

export default function Hero({ onCtaClick }) {
  const handlePrimary = () => {
    if (siteConfig.primaryCtaMode === 'sms') {
      const body = encodeURIComponent(siteConfig.smsBody);
      const number = siteConfig.smsNumber;
      const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);
      const scheme = isIOS ? 'sms' : 'sms';
      window.location.href = `${scheme}:${number}?&body=${body}`;
    } else {
      onCtaClick?.();
    }
  };

  return (
    <section id="top" className="hero">
      <div className="hero__decor hero__decor--a" aria-hidden="true">
        <div className="img-placeholder tall">Image</div>
      </div>
      <div className="hero__decor hero__decor--b" aria-hidden="true">
        <div className="img-placeholder square">Image</div>
      </div>

      <div className="container hero__content">
        <h1 className="hero__headline">
          <span className="hero__line hero__line--xl">Something</span>
          <span className="hero__line hero__line--md">simply </span>
          <span className="hero__line hero__line--xl hero__line--italic">extraordinary</span>
          <span className="hero__line hero__line--sm">is waiting for you.</span>
        </h1>

        <div className="hero__cta-row">
          <button type="button" className="btn btn-primary hero__cta" onClick={handlePrimary}>
            Get started
          </button>
        </div>

        <p className="hero__legal text-soft">
          By continuing you agree to our{' '}
          <a href="#terms" className="hero__legal-link">Terms</a>{' '}and{' '}
          <a href="#privacy" className="hero__legal-link">Privacy Policy</a>.
        </p>
      </div>
    </section>
  );
}

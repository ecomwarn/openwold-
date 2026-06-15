import './SocialProof.css';

const stats = [
  { value: '10k+', label: 'Placeholder stat label' },
  { value: '98%', label: 'Placeholder stat label' },
  { value: '24/7', label: 'Placeholder stat label' },
];

export default function SocialProof() {
  return (
    <section className="social">
      <div className="container social__inner">
        <div className="social__logos" aria-label="Trusted by">
          {Array.from({ length: 6 }).map((_, i) => (
            <div className="social__logo img-placeholder" key={i}>Logo</div>
          ))}
        </div>

        <ul className="social__stats">
          {stats.map((s, i) => (
            <li className="social__stat" key={i}>
              <span className="social__stat-value">{s.value}</span>
              <span className="social__stat-label text-muted">{s.label}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}

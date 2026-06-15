import './Trust.css';

const points = [
  { label: 'Point one label', body: 'Short supporting placeholder copy.' },
  { label: 'Point two label', body: 'Short supporting placeholder copy.' },
  { label: 'Point three label', body: 'Short supporting placeholder copy.' },
];

export default function Trust() {
  return (
    <section className="trust">
      <div className="container">
        <p className="section-eyebrow">Trust &amp; safety</p>
        <h2 className="section-heading">Built with care.</h2>

        <ul className="trust__list">
          {points.map((p, i) => (
            <li className="trust__item" key={i}>
              <div className="trust__media img-placeholder square">Image</div>
              <div className="trust__copy">
                <h3 className="trust__label">{p.label}</h3>
                <p className="trust__body text-muted">{p.body}</p>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}

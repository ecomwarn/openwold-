import './Features.css';

const features = [
  {
    title: 'Feature headline placeholder one',
    body: 'Short supporting copy placeholder describing this feature in a sentence or two.',
  },
  {
    title: 'Feature headline placeholder two',
    body: 'Short supporting copy placeholder describing this feature in a sentence or two.',
  },
  {
    title: 'Feature headline placeholder three',
    body: 'Short supporting copy placeholder describing this feature in a sentence or two.',
  },
];

export default function Features() {
  return (
    <section id="features" className="features">
      <div className="container">
        <p className="section-eyebrow">Features</p>
        <h2 className="section-heading">Built around three core ideas.</h2>

        <div className="features__stack">
          {features.map((f, i) => (
            <article className="features__row" key={i}>
              <div className="features__copy">
                <h3 className="features__title">{f.title}</h3>
                <p className="features__body text-muted">{f.body}</p>
              </div>
              {/* Separate image slots for mobile vs desktop */}
              <div className="features__media features__media--desktop img-placeholder wide">Image · desktop</div>
              <div className="features__media features__media--mobile img-placeholder square">Image · mobile</div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

import './HowItWorks.css';

const steps = [
  {
    n: '01',
    title: 'Step one heading',
    body: 'Short one-line description placeholder for the first step.',
  },
  {
    n: '02',
    title: 'Step two heading',
    body: 'Short one-line description placeholder for the second step.',
  },
  {
    n: '03',
    title: 'Step three heading',
    body: 'Short one-line description placeholder for the third step.',
  },
  {
    n: '04',
    title: 'Step four heading',
    body: 'Short one-line description placeholder for the fourth step.',
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="how">
      <div className="container">
        <p className="section-eyebrow">How it works</p>
        <h2 className="section-heading">A simple four-step flow.</h2>

        <ol className="how__grid">
          {steps.map((s) => (
            <li className="how__step" key={s.n}>
              <div className="how__media img-placeholder wide">Image</div>
              <div className="how__copy">
                <span className="how__num">{s.n}</span>
                <h3 className="how__title">{s.title}</h3>
                <p className="how__body text-muted">{s.body}</p>
              </div>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}

import './Comparison.css';

export default function Comparison() {
  return (
    <section className="compare">
      <div className="container">
        <p className="section-eyebrow">Comparison</p>
        <h2 className="section-heading">A better way, side by side.</h2>

        <div className="compare__grid">
          <article className="compare__col compare__col--positive">
            <div className="compare__media img-placeholder wide">Image · ours</div>
            <h3 className="compare__title">Our approach</h3>
            <p className="compare__body text-muted">
              Placeholder copy describing the positive approach in a sentence or two.
            </p>
          </article>

          <article className="compare__col compare__col--negative">
            <div className="compare__media img-placeholder wide">Image · old way</div>
            <h3 className="compare__title">The old way</h3>
            <p className="compare__body text-muted">
              Placeholder copy contrasting the old approach in a sentence or two.
            </p>
          </article>
        </div>
      </div>
    </section>
  );
}

import './Marquee.css';

export default function Marquee() {
  const items = Array.from({ length: 8 });
  return (
    <section className="marquee" aria-label="Gallery">
      <div className="marquee__track">
        {/* duplicated for seamless looping */}
        {[0, 1].map((dup) => (
          <ul className="marquee__list" key={dup} aria-hidden={dup === 1}>
            {items.map((_, i) => (
              <li className="marquee__item" key={i}>
                <div className="img-placeholder square">Image</div>
              </li>
            ))}
          </ul>
        ))}
      </div>
    </section>
  );
}

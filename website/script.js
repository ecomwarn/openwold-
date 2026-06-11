// Navbar border on scroll
const navbar = document.getElementById("navbar");
window.addEventListener("scroll", () => {
  navbar.classList.toggle("scrolled", window.scrollY > 8);
});

// Mobile menu
const navToggle = document.getElementById("navToggle");
const navLinks = document.getElementById("navLinks");
navToggle.addEventListener("click", () => navLinks.classList.toggle("open"));
navLinks.querySelectorAll("a").forEach((a) =>
  a.addEventListener("click", () => navLinks.classList.remove("open"))
);

// Animated stat counters (run once when scrolled into view)
const stats = document.querySelectorAll(".stat-num");
const animateCount = (el) => {
  const target = parseInt(el.dataset.count, 10);
  const duration = 1200;
  const start = performance.now();
  const tick = (now) => {
    const progress = Math.min((now - start) / duration, 1);
    el.textContent = Math.round(target * (1 - Math.pow(1 - progress, 3)));
    if (progress < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
};

const statsObserver = new IntersectionObserver(
  (entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        animateCount(entry.target);
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.5 }
);
stats.forEach((el) => statsObserver.observe(el));

// Monthly / yearly pricing toggle
const billingSwitch = document.getElementById("billingSwitch");
billingSwitch.addEventListener("change", () => {
  const yearly = billingSwitch.checked;
  document.querySelectorAll(".price .amount").forEach((el) => {
    el.textContent = "$" + (yearly ? el.dataset.yearly : el.dataset.monthly);
  });
});

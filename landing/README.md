# Landing

Responsive single-page marketing site built with React + Vite. All copy, imagery, and branding are neutral placeholders.

## Run

```bash
cd landing
pnpm install   # or npm install / yarn
pnpm dev       # http://localhost:5173
pnpm build     # production build to ./dist
pnpm preview   # serve the production build
```

## Structure

- `src/App.jsx` — composes the page sections and the email-capture modal.
- `src/styles/tokens.css` — centralized design tokens (colors, spacing, type scale). Re-skin the whole app by editing this file.
- `src/styles/global.css` — base resets, container, button, and placeholder image utilities.
- `src/config.js` — runtime configuration:
  - `primaryCtaMode`: `"modal"` opens the email-capture modal, `"sms"` deep-links to SMS/iMessage.
  - `smsNumber`, `smsBody`: SMS deep-link parameters.
  - `faqMultiOpen`: allow multiple FAQ items open at once.
- `src/components/` — one folder-per-section component, each with its own CSS module file:
  - `Nav` — sticky top bar, transparent over hero, gains solid background after scroll.
  - `Hero` — full-viewport hero with mixed-weight headline and two decorative image placeholders.
  - `HowItWorks` — 4-step numbered flow.
  - `SocialProof` — small logo row plus three large stat callouts.
  - `Features` — 3 stacked feature rows with separate mobile/desktop image slots.
  - `Marquee` — auto-scrolling infinite image strip (pauses on hover).
  - `Comparison` — two-column "ours vs old way" panel.
  - `Trust` — three labeled trust/safety points.
  - `FAQ` — accordion with single- or multi-open behavior.
  - `Footer` — repeating tagline marquee, resources column, social icons, legal links.
  - `EmailModal` — validated email-capture modal (stub stores submissions to `localStorage`).

## Replacing placeholders

- Images: every image slot is rendered with the `.img-placeholder` div. Swap it for an `<img>` tag (or component) in place.
- Copy: each section file holds its own copy as inline strings or arrays at the top of the component.
- Brand styling: edit values in `src/styles/tokens.css`.

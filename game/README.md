# Maplewood Tales — Starter Area

A small, self-contained browser game in the spirit of classic monster-taming
RPG opening areas: a quiet lakeside starter town and a grassy route to the
north. All maps, names, art, and code are original.

## Play

Open `game/index.html` in any browser — no build step or server needed.
(Or serve the folder: `npx serve game`.)

## Controls

| Key | Action |
| --- | --- |
| Arrow keys / WASD | Move |
| Z / Enter / Space | Talk, read signs, confirm |
| Up / Down (in battle) | Choose FIGHT or RUN |

## What's in it

- **Maplewood Town** — your house, a neighbor, a professor's lab, a lake,
  and your mom (talk to her).
- **Route 1 — Brambleway** — tall grass with random wild-critter encounters,
  hop-down ledges, signs, and two NPCs.
- **Battles** — your partner EMBOLT vs. wild SPROUTLE, FLITT, and the rare
  PUDDLIT. Faint and you'll wake up back home, fully healed.

Everything is rendered procedurally on a `<canvas>` — there are no image
assets, just `index.html` and `game.js`.

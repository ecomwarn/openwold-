// Maplewood Tales — an original mini top-down adventure.
// A small starter town and a grassy route, in the spirit of classic
// monster-taming RPG opening areas. All art, maps, names and code original.

'use strict';

const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
ctx.imageSmoothingEnabled = false;

const TILE = 32;
const VIEW_W = canvas.width;   // 768 = 24 tiles
const VIEW_H = canvas.height;  // 576 = 18 tiles

// ---------------------------------------------------------------------------
// Maps
// ---------------------------------------------------------------------------
// Tile legend:
//   T tree (solid)      W water (solid)     S sign (solid, readable)
//   l ledge (jump down) G tall grass        f flowers
//   p path              . grass

const MAPS = {
  town: {
    name: 'Maplewood Town',
    rows: [
      'TTTTTTTTTTTppTTTTTTTTTTT',
      'T..........pp..........T',
      'T..f.......pp.......f..T',
      'T..........pp..........T',
      'T..........pp..........T',
      'T..........pp..........T',
      'T..........pp..........T',
      'T..........pp..........T',
      'T...pppppppppppppppp...T',
      'T..........pp..........T',
      'T..........pp..........T',
      'T..........pp..........T',
      'T..........pp..........T',
      'T..........pp..........T',
      'TWW........pp..........T',
      'TWWW.......pp....f.....T',
      'TWWWW......pp..........T',
      'TWWWWW...S.pp..........T',
      'TWWWW......pp..........T',
      'TTTTTTTTTTTTTTTTTTTTTTTT',
    ],
    buildings: [
      { x: 4,  y: 4,  w: 4, h: 4, style: 'house', roof: '#c0492f',
        door: { x: 6, y: 7 },
        doorText: 'Your house. You just left, and the whole world is waiting!' },
      { x: 16, y: 4,  w: 4, h: 4, style: 'house', roof: '#3c6fb1',
        door: { x: 17, y: 7 },
        doorText: 'The door is locked. Someone inside is humming off-key.' },
      { x: 15, y: 11, w: 6, h: 4, style: 'lab',   roof: '#5a6e8c',
        door: { x: 17, y: 14 },
        doorText: 'PROFESSOR BIRCHWOOD\'S LAB — out doing fieldwork. Back never, probably.' },
    ],
    signs: {
      '9,17': 'MAPLEWOOD TOWN — "Where every journey sprouts."',
    },
    npcs: [
      { x: 8, y: 10, dir: 'down', pal: 'mom', solid: true, text: [
        'MOM: Off already? Keep EMBOLT close — wild critters live in the tall grass!',
        'MOM: And if you get hurt, come straight home. I mean it.',
      ] },
    ],
    // Walking off the top edge through the gap leads to the route.
    exits: [
      { edge: 'top', cols: [11, 12], to: 'route', spawnY: 22 },
    ],
    encounterRate: 0,
  },

  route: {
    name: 'Route 1 — Brambleway',
    rows: [
      'TTTTTTTTTTTTTTTTTTTTTTTT',
      'T..........pp..........T',
      'T..GGGGG...pp...GGGGG..T',
      'T..GGGGG...pp...GGGGG..T',
      'T..GGGGG...pp...GGGGG..T',
      'T..........pp..........T',
      'T...f......pp......f...T',
      'TllllllllllppllllllllllT',
      'T..........pp..........T',
      'T..GGGG....pp....GGGG..T',
      'T..GGGG....pp....GGGG..T',
      'T..GGGG....pp....GGGG..T',
      'T..GGGG....pp....GGGG..T',
      'T..........pp..........T',
      'T.....S....pp..........T',
      'T..........pp..........T',
      'T....GGG...pp...GGGG...T',
      'T....GGG...pp...GGGG...T',
      'T....GGG...pp...GGGG...T',
      'T..........pp..........T',
      'T..f.......pp.......f..T',
      'T..........pp..........T',
      'T..........pp..........T',
      'TTTTTTTTTTTppTTTTTTTTTTT',
    ],
    buildings: [],
    signs: {
      '6,14': 'ROUTE 1 — BRAMBLEWAY. North: Brambleway Woods (closed).',
    },
    npcs: [
      { x: 11, y: 1, dir: 'down', pal: 'ranger', solid: true, text: [
        'RANGER: Whoa there! The woods ahead are closed while we count the Flitt swarms.',
        'RANGER: Hop the ledges on your way back down — it\'s the best part of this job.',
      ] },
      { x: 17, y: 13, dir: 'left', pal: 'kid', solid: true, text: [
        'KID: I saw a blue PUDDLIT in the grass once!',
        'KID: ...or maybe it was a puddle. It was very round.',
      ] },
    ],
    exits: [
      { edge: 'bottom', cols: [11, 12], to: 'town', spawnY: 1 },
    ],
    encounterRate: 0.13,
  },
};

// ---------------------------------------------------------------------------
// Critters (all original)
// ---------------------------------------------------------------------------
const SPECIES = {
  sproutle: { name: 'SPROUTLE', color: '#5cb85c', dark: '#3e8e41', shape: 'leaf', weight: 45 },
  flitt:    { name: 'FLITT',    color: '#f2c14e', dark: '#c9961f', shape: 'wing', weight: 40 },
  puddlit:  { name: 'PUDDLIT',  color: '#5aa9e6', dark: '#3779b3', shape: 'fin',  weight: 15 },
};

const PALETTES = {
  player: { hat: '#d64545', hatDark: '#a83232', skin: '#f3c89c', shirt: '#3a6ea5', legs: '#3b3b4f' },
  mom:    { hat: '#a05a2c', hatDark: '#7d4521', skin: '#f3c89c', shirt: '#c2547d', legs: '#5b4a68' },
  ranger: { hat: '#3e8e41', hatDark: '#2c6b2f', skin: '#e8b88a', shirt: '#6d4c41', legs: '#3b3b4f' },
  kid:    { hat: '#f4b400', hatDark: '#c79200', skin: '#f3c89c', shirt: '#7e57c2', legs: '#3b3b4f' },
};

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
const state = {
  mode: 'title',          // title | world | dialog | battle
  mapId: 'town',
  fade: 0,                // black overlay, decays to 0
  locTimer: 0,            // seconds left to show the location banner
  dialog: { lines: [], index: 0 },
  battle: null,
  time: 0,
};

const player = {
  tx: 6, ty: 8,           // tile position
  px: 6 * TILE, py: 8 * TILE,
  dir: 'down',
  moving: false,
  fromX: 0, fromY: 0, toX: 0, toY: 0,
  progress: 0, dist: 1,
  hopping: false,
  partner: { species: 'embolt', name: 'EMBOLT', level: 5, hp: 20, maxHp: 20 },
};

const keys = {};

function map() { return MAPS[state.mapId]; }
function mapW() { return map().rows[0].length; }
function mapH() { return map().rows.length; }
function tileAt(x, y) {
  if (x < 0 || y < 0 || x >= mapW() || y >= mapH()) return 'T';
  return map().rows[y][x];
}
function hash(x, y) {
  let h = (x * 73856093) ^ (y * 19349663) ^ (state.mapId === 'town' ? 7 : 131);
  h = (h ^ (h >> 13)) >>> 0;
  return h;
}
function rand(n) { return Math.floor(Math.random() * n); }

// ---------------------------------------------------------------------------
// Input
// ---------------------------------------------------------------------------
const ACTION_KEYS = ['KeyZ', 'Enter', 'Space'];
const DIR_KEYS = {
  ArrowUp: 'up', KeyW: 'up',
  ArrowDown: 'down', KeyS: 'down',
  ArrowLeft: 'left', KeyA: 'left',
  ArrowRight: 'right', KeyD: 'right',
};

document.addEventListener('keydown', (e) => {
  if (e.code in DIR_KEYS || ACTION_KEYS.includes(e.code)) e.preventDefault();
  if (!e.repeat) handlePress(e.code);
  keys[e.code] = true;
});
document.addEventListener('keyup', (e) => { keys[e.code] = false; });
window.addEventListener('blur', () => { for (const k in keys) keys[k] = false; });

function heldDir() {
  for (const code in DIR_KEYS) if (keys[code]) return DIR_KEYS[code];
  return null;
}

function handlePress(code) {
  const isAction = ACTION_KEYS.includes(code);
  if (state.mode === 'title') {
    if (isAction) { state.mode = 'world'; state.locTimer = 2.5; }
  } else if (state.mode === 'dialog') {
    if (isAction) advanceDialog();
  } else if (state.mode === 'battle') {
    battleKey(code, isAction);
  } else if (state.mode === 'world') {
    if (isAction && !player.moving) interact();
  }
}

// ---------------------------------------------------------------------------
// World logic
// ---------------------------------------------------------------------------
const DIR_DELTA = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] };
const OPPOSITE = { up: 'down', down: 'up', left: 'right', right: 'left' };

function buildingAt(x, y) {
  for (const b of map().buildings) {
    if (x >= b.x && x < b.x + b.w && y >= b.y && y < b.y + b.h) return b;
  }
  return null;
}
function npcAt(x, y) {
  return map().npcs.find((n) => n.x === x && n.y === y) || null;
}

function isSolid(x, y) {
  const t = tileAt(x, y);
  if (t === 'T' || t === 'W' || t === 'S' || t === 'l') return true;
  if (buildingAt(x, y)) return true;
  if (npcAt(x, y)) return true;
  return false;
}

function tryMove(dir) {
  player.dir = dir;
  const [dx, dy] = DIR_DELTA[dir];
  const nx = player.tx + dx;
  const ny = player.ty + dy;

  // Map exits at the edges.
  for (const exit of map().exits) {
    const offEdge = (exit.edge === 'top' && ny < 0) || (exit.edge === 'bottom' && ny >= mapH());
    if (offEdge && exit.cols.includes(nx)) { switchMap(exit.to, nx, exit.spawnY, dir); return; }
  }

  // Ledge hop: only downward, landing two tiles away.
  if (tileAt(nx, ny) === 'l' && dir === 'down' && !isSolid(nx, ny + 1)) {
    startMove(nx, ny + 1, 2, true);
    return;
  }

  if (!isSolid(nx, ny)) startMove(nx, ny, 1, false);
}

function startMove(toX, toY, dist, hop) {
  player.moving = true;
  player.hopping = hop;
  player.fromX = player.tx; player.fromY = player.ty;
  player.toX = toX; player.toY = toY;
  player.progress = 0;
  player.dist = dist;
}

function switchMap(id, spawnX, spawnY, dir) {
  state.mapId = id;
  player.tx = spawnX; player.ty = spawnY;
  player.px = spawnX * TILE; player.py = spawnY * TILE;
  player.moving = false;
  player.dir = dir;
  state.fade = 1;
  state.locTimer = 2.5;
}

function finishMove() {
  player.tx = player.toX; player.ty = player.toY;
  player.px = player.tx * TILE; player.py = player.ty * TILE;
  player.moving = false;
  player.hopping = false;
  if (tileAt(player.tx, player.ty) === 'G' && Math.random() < map().encounterRate) {
    startBattle();
  }
}

function interact() {
  const [dx, dy] = DIR_DELTA[player.dir];
  const fx = player.tx + dx;
  const fy = player.ty + dy;

  const npc = npcAt(fx, fy);
  if (npc) {
    npc.dir = OPPOSITE[player.dir];
    openDialog(npc.text);
    return;
  }
  const signText = map().signs[fx + ',' + fy];
  if (signText && tileAt(fx, fy) === 'S') {
    openDialog([signText]);
    return;
  }
  const b = buildingAt(fx, fy);
  if (b && b.door.x === fx && b.door.y === fy) {
    openDialog([b.doorText]);
  }
}

function openDialog(lines) {
  state.dialog.lines = lines.slice();
  state.dialog.index = 0;
  state.mode = 'dialog';
}

function advanceDialog() {
  state.dialog.index++;
  if (state.dialog.index >= state.dialog.lines.length) state.mode = 'world';
}

function updateWorld(dt) {
  if (player.moving) {
    player.progress += (4.5 / player.dist) * dt; // 4.5 tiles per second
    if (player.progress >= 1) {
      finishMove();
    } else {
      const t = player.progress;
      player.px = (player.fromX + (player.toX - player.fromX) * t) * TILE;
      player.py = (player.fromY + (player.toY - player.fromY) * t) * TILE;
    }
  } else {
    const dir = heldDir();
    if (dir) tryMove(dir);
  }
}

// ---------------------------------------------------------------------------
// Battle
// ---------------------------------------------------------------------------
function pickSpecies() {
  const ids = Object.keys(SPECIES);
  let total = 0;
  for (const id of ids) total += SPECIES[id].weight;
  let roll = rand(total);
  for (const id of ids) {
    roll -= SPECIES[id].weight;
    if (roll < 0) return id;
  }
  return ids[0];
}

function startBattle() {
  const speciesId = pickSpecies();
  const level = 2 + rand(3);
  const maxHp = 9 + level * 2;
  state.battle = {
    foe: { speciesId, name: SPECIES[speciesId].name, level, hp: maxHp, maxHp },
    phase: 'msg',          // msg | menu
    msgs: ['A wild ' + SPECIES[speciesId].name + ' appeared!'],
    msgIndex: 0,
    after: () => { state.battle.phase = 'menu'; },
    menuIndex: 0,
    outcome: null,         // null | 'win' | 'run' | 'lose'
  };
  state.mode = 'battle';
  state.fade = 1;
}

function queueMsgs(msgs, after) {
  const b = state.battle;
  b.msgs = msgs;
  b.msgIndex = 0;
  b.after = after;
  b.phase = 'msg';
}

function battleKey(code, isAction) {
  const b = state.battle;
  if (!b) return;
  if (b.phase === 'msg') {
    if (isAction) {
      b.msgIndex++;
      if (b.msgIndex >= b.msgs.length) b.after();
    }
  } else if (b.phase === 'menu') {
    if (code === 'ArrowUp' || code === 'KeyW') b.menuIndex = 0;
    else if (code === 'ArrowDown' || code === 'KeyS') b.menuIndex = 1;
    else if (isAction) (b.menuIndex === 0 ? doFight : doRun)();
  }
}

function doFight() {
  const b = state.battle;
  const mine = player.partner;
  const dmg = 4 + rand(4);
  b.foe.hp = Math.max(0, b.foe.hp - dmg);
  const msgs = [mine.name + ' used SPARK!'];

  if (b.foe.hp <= 0) {
    msgs.push('The wild ' + b.foe.name + ' fainted!');
    b.outcome = 'win';
    queueMsgs(msgs, endBattle);
    return;
  }

  const foeDmg = 2 + rand(3);
  mine.hp = Math.max(0, mine.hp - foeDmg);
  msgs.push('The wild ' + b.foe.name + ' tackled back!');
  if (mine.hp <= 0) {
    msgs.push(mine.name + ' fainted!');
    b.outcome = 'lose';
    queueMsgs(msgs, endBattle);
    return;
  }
  queueMsgs(msgs, () => { b.phase = 'menu'; });
}

function doRun() {
  state.battle.outcome = 'run';
  queueMsgs(['Got away safely!'], endBattle);
}

function endBattle() {
  const outcome = state.battle.outcome;
  state.battle = null;
  state.mode = 'world';
  state.fade = 1;
  if (outcome === 'lose') {
    player.partner.hp = player.partner.maxHp;
    switchMap('town', 6, 8, 'down');
    openDialog([
      'You scurried back home...',
      'MOM: Told you so! There. EMBOLT is all patched up.',
    ]);
  }
}

// ---------------------------------------------------------------------------
// Rendering — tiles
// ---------------------------------------------------------------------------
function drawGrass(sx, sy, x, y) {
  ctx.fillStyle = '#8fd06a';
  ctx.fillRect(sx, sy, TILE, TILE);
  const h = hash(x, y);
  if (h % 5 === 0) {
    ctx.fillStyle = '#7cbe58';
    const ox = 6 + (h % 17);
    const oy = 8 + ((h >> 4) % 15);
    ctx.fillRect(sx + ox, sy + oy, 3, 2);
    ctx.fillRect(sx + ox + 5, sy + oy + 4, 3, 2);
  }
}

function drawPath(sx, sy, x, y) {
  ctx.fillStyle = '#e8d8a0';
  ctx.fillRect(sx, sy, TILE, TILE);
  const h = hash(x, y);
  ctx.fillStyle = '#d8c488';
  ctx.fillRect(sx + (h % 20) + 4, sy + ((h >> 3) % 20) + 4, 3, 3);
  ctx.fillRect(sx + ((h >> 6) % 22) + 2, sy + ((h >> 9) % 22) + 2, 2, 2);
}

function drawTree(sx, sy) {
  drawGrassPlain(sx, sy);
  ctx.fillStyle = '#8a5a30';
  ctx.fillRect(sx + 12, sy + 22, 8, 8);
  ctx.fillStyle = '#2e7d32';
  ctx.fillRect(sx + 3, sy + 10, 26, 14);
  ctx.fillStyle = '#3f9c42';
  ctx.fillRect(sx + 6, sy + 3, 20, 13);
  ctx.fillStyle = '#66bb6a';
  ctx.fillRect(sx + 9, sy + 5, 8, 4);
}

function drawGrassPlain(sx, sy) {
  ctx.fillStyle = '#8fd06a';
  ctx.fillRect(sx, sy, TILE, TILE);
}

function drawWater(sx, sy, x, y) {
  ctx.fillStyle = '#4aa3df';
  ctx.fillRect(sx, sy, TILE, TILE);
  const phase = Math.sin(state.time * 2 + x * 1.7 + y * 2.3);
  if (phase > 0.2) {
    ctx.fillStyle = '#7cc4ec';
    ctx.fillRect(sx + 6, sy + 10 + Math.round(phase * 3), 12, 2);
    ctx.fillRect(sx + 20, sy + 22 - Math.round(phase * 3), 8, 2);
  }
}

function drawTallGrass(sx, sy, x, y) {
  drawGrass(sx, sy, x, y);
  drawGrassBlades(sx, sy, x, y, 0);
}

function drawGrassBlades(sx, sy, x, y, topOnly) {
  // topOnly > 0 draws only the lower blades (used to overlay characters).
  const h = hash(x, y);
  const sway = Math.sin(state.time * 3 + h) > 0.6 ? 1 : 0;
  ctx.fillStyle = '#3e8e41';
  for (let i = 0; i < 4; i++) {
    const bx = sx + 3 + i * 8 + (i % 2 ? sway : 0);
    const by = sy + 8 + ((h >> i) % 5) + topOnly;
    ctx.fillRect(bx, by, 4, TILE - (by - sy) - 2);
    ctx.fillStyle = i % 2 ? '#3e8e41' : '#54a857';
  }
}

function drawFlowers(sx, sy, x, y) {
  drawGrass(sx, sy, x, y);
  const h = hash(x, y);
  const petal = h % 2 ? '#ff6b6b' : '#ffffff';
  const wob = Math.sin(state.time * 2.5 + h) > 0 ? 0 : 1;
  for (const [ox, oy] of [[8, 8], [20, 18]]) {
    ctx.fillStyle = petal;
    ctx.fillRect(sx + ox - 2 + wob, sy + oy, 8, 3);
    ctx.fillRect(sx + ox + 1 + wob, sy + oy - 3, 3, 8);
    ctx.fillStyle = '#f4b400';
    ctx.fillRect(sx + ox + 1 + wob, sy + oy, 3, 3);
  }
}

function drawLedge(sx, sy, x, y) {
  drawGrass(sx, sy, x, y);
  ctx.fillStyle = '#6da84e';
  ctx.fillRect(sx, sy + 18, TILE, 10);
  ctx.fillStyle = '#54793a';
  ctx.fillRect(sx, sy + 26, TILE, 4);
  ctx.fillStyle = 'rgba(0,0,0,0.18)';
  ctx.fillRect(sx, sy + 30, TILE, 2);
}

function drawSign(sx, sy) {
  drawGrassPlain(sx, sy);
  ctx.fillStyle = '#8a5a30';
  ctx.fillRect(sx + 14, sy + 14, 4, 14);
  ctx.fillStyle = '#b07b42';
  ctx.fillRect(sx + 5, sy + 4, 22, 12);
  ctx.fillStyle = '#8a5a30';
  ctx.fillRect(sx + 8, sy + 7, 16, 2);
  ctx.fillRect(sx + 8, sy + 11, 12, 2);
}

function drawTile(t, sx, sy, x, y) {
  switch (t) {
    case 'T': drawTree(sx, sy); break;
    case 'W': drawWater(sx, sy, x, y); break;
    case 'G': drawTallGrass(sx, sy, x, y); break;
    case 'f': drawFlowers(sx, sy, x, y); break;
    case 'p': drawPath(sx, sy, x, y); break;
    case 'l': drawLedge(sx, sy, x, y); break;
    case 'S': drawSign(sx, sy); break;
    default:  drawGrass(sx, sy, x, y); break;
  }
}

// ---------------------------------------------------------------------------
// Rendering — buildings & characters
// ---------------------------------------------------------------------------
function drawBuilding(b, camX, camY) {
  const X = b.x * TILE - camX;
  const Y = b.y * TILE - camY;
  const W = b.w * TILE;
  const H = b.h * TILE;
  const roofH = Math.floor(H * 0.45);
  const wall = b.style === 'lab' ? '#cfd6e4' : '#f3e9d2';
  const wallDark = b.style === 'lab' ? '#aab3c5' : '#d9cbab';

  // walls
  ctx.fillStyle = wall;
  ctx.fillRect(X + 2, Y + roofH, W - 4, H - roofH);
  ctx.fillStyle = wallDark;
  ctx.fillRect(X + 2, Y + H - 6, W - 4, 6);

  // roof with overhang
  ctx.fillStyle = b.roof;
  ctx.fillRect(X - 2, Y, W + 4, roofH);
  ctx.fillStyle = 'rgba(255,255,255,0.25)';
  ctx.fillRect(X - 2, Y, W + 4, 6);
  ctx.fillStyle = 'rgba(0,0,0,0.2)';
  ctx.fillRect(X - 2, Y + roofH - 5, W + 4, 5);

  // windows
  ctx.fillStyle = '#7cc4ec';
  for (let i = 0; i < b.w - 1; i++) {
    const wx = X + 14 + i * TILE;
    if (Math.floor((wx + camX - X) / TILE) + b.x === b.door.x) continue;
    ctx.fillRect(wx, Y + roofH + 8, 16, 14);
    ctx.strokeStyle = wallDark;
    ctx.strokeRect(wx + 0.5, Y + roofH + 8.5, 15, 13);
  }

  // door
  const dX = b.door.x * TILE - camX;
  const dY = b.door.y * TILE - camY;
  ctx.fillStyle = '#7a4a22';
  ctx.fillRect(dX + 6, dY + 4, 20, 28);
  ctx.fillStyle = '#5c3617';
  ctx.fillRect(dX + 6, dY + 4, 20, 4);
  ctx.fillStyle = '#f4d35e';
  ctx.fillRect(dX + 21, dY + 18, 3, 3);

  // lab plaque
  if (b.style === 'lab') {
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(X + 8, Y + roofH + 4, 34, 10);
    ctx.fillStyle = '#5a6e8c';
    ctx.fillRect(X + 10, Y + roofH + 7, 30, 2);
  }
}

function drawCharacter(sx, sy, dir, walkFrame, pal, zOff) {
  const z = zOff || 0;
  // shadow
  ctx.fillStyle = 'rgba(0,0,0,0.25)';
  ctx.beginPath();
  ctx.ellipse(sx + 16, sy + 29, 9, 4, 0, 0, Math.PI * 2);
  ctx.fill();

  const y = sy + z;
  // legs
  ctx.fillStyle = pal.legs;
  const lift = walkFrame ? 3 : 0;
  ctx.fillRect(sx + 10, y + 23 - lift, 5, 7 + (walkFrame ? lift - 2 : 0));
  ctx.fillRect(sx + 17, y + 23 - (walkFrame ? 0 : 0), 5, 7);
  if (walkFrame) {
    ctx.fillRect(sx + 17, y + 23, 5, 5);
  }
  // body
  ctx.fillStyle = pal.shirt;
  ctx.fillRect(sx + 8, y + 15, 16, 10);
  // arms
  ctx.fillStyle = pal.skin;
  ctx.fillRect(sx + 6, y + 16, 3, 7);
  ctx.fillRect(sx + 23, y + 16, 3, 7);
  // head
  ctx.fillRect(sx + 9, y + 5, 14, 12);
  // hat / hair
  ctx.fillStyle = pal.hat;
  ctx.fillRect(sx + 8, y + 2, 16, 6);
  ctx.fillStyle = pal.hatDark;
  if (dir === 'down') ctx.fillRect(sx + 8, y + 7, 16, 2);
  if (dir === 'left') ctx.fillRect(sx + 4, y + 6, 10, 2);
  if (dir === 'right') ctx.fillRect(sx + 18, y + 6, 10, 2);
  if (dir === 'up') { ctx.fillStyle = pal.hat; ctx.fillRect(sx + 9, y + 7, 14, 6); }

  // eyes
  ctx.fillStyle = '#222';
  if (dir === 'down') {
    ctx.fillRect(sx + 12, y + 11, 2, 3);
    ctx.fillRect(sx + 18, y + 11, 2, 3);
  } else if (dir === 'left') {
    ctx.fillRect(sx + 11, y + 11, 2, 3);
  } else if (dir === 'right') {
    ctx.fillRect(sx + 19, y + 11, 2, 3);
  }
}

// ---------------------------------------------------------------------------
// Rendering — world
// ---------------------------------------------------------------------------
function camera() {
  let camX = Math.round(player.px + TILE / 2 - VIEW_W / 2);
  let camY = Math.round(player.py + TILE / 2 - VIEW_H / 2);
  camX = Math.max(0, Math.min(camX, mapW() * TILE - VIEW_W));
  camY = Math.max(0, Math.min(camY, mapH() * TILE - VIEW_H));
  return { camX, camY };
}

function drawWorld() {
  const { camX, camY } = camera();
  const x0 = Math.floor(camX / TILE);
  const y0 = Math.floor(camY / TILE);
  const x1 = Math.min(mapW() - 1, x0 + Math.ceil(VIEW_W / TILE));
  const y1 = Math.min(mapH() - 1, y0 + Math.ceil(VIEW_H / TILE));

  for (let y = y0; y <= y1; y++) {
    for (let x = x0; x <= x1; x++) {
      drawTile(tileAt(x, y), x * TILE - camX, y * TILE - camY, x, y);
    }
  }

  for (const b of map().buildings) drawBuilding(b, camX, camY);

  // characters sorted by vertical position
  const ents = map().npcs.map((n) => ({
    py: n.y * TILE, draw: () =>
      drawCharacter(n.x * TILE - camX, n.y * TILE - camY, n.dir, 0, PALETTES[n.pal], 0),
    gx: n.x, gy: n.y,
  }));
  const walkFrame = player.moving && Math.floor(player.progress * player.dist * 4) % 2 === 1 ? 1 : 0;
  const hopZ = player.hopping ? -Math.sin(player.progress * Math.PI) * 12 : 0;
  ents.push({
    py: player.py, draw: () =>
      drawCharacter(player.px - camX, player.py - camY, player.dir, walkFrame, PALETTES.player, hopZ),
    gx: Math.round(player.px / TILE), gy: Math.round(player.py / TILE),
  });
  ents.sort((a, b) => a.py - b.py);
  for (const e of ents) {
    e.draw();
    if (tileAt(e.gx, e.gy) === 'G') {
      drawGrassBlades(e.gx * TILE - camX, e.gy * TILE - camY, e.gx, e.gy, 10);
    }
  }

  drawLocationBanner();
}

function drawLocationBanner() {
  if (state.locTimer <= 0) return;
  const alpha = Math.min(1, state.locTimer);
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.fillStyle = '#fffdf4';
  ctx.strokeStyle = '#5a4632';
  roundRect(12, 12, 320, 44, 8, true, true);
  ctx.fillStyle = '#3b3b4f';
  ctx.font = 'bold 20px monospace';
  ctx.textAlign = 'left';
  ctx.fillText(map().name, 28, 40);
  ctx.restore();
}

// ---------------------------------------------------------------------------
// Rendering — UI helpers
// ---------------------------------------------------------------------------
function roundRect(x, y, w, h, r, fill, stroke) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
  ctx.lineWidth = 3;
  if (fill) ctx.fill();
  if (stroke) ctx.stroke();
}

function wrapText(text, maxW) {
  const words = text.split(' ');
  const lines = [];
  let line = '';
  for (const w of words) {
    const test = line ? line + ' ' + w : w;
    if (ctx.measureText(test).width > maxW && line) {
      lines.push(line);
      line = w;
    } else {
      line = test;
    }
  }
  if (line) lines.push(line);
  return lines;
}

function drawTextBox(text, showArrow) {
  ctx.fillStyle = '#fffdf4';
  ctx.strokeStyle = '#5a4632';
  roundRect(12, 444, VIEW_W - 24, 120, 10, true, true);
  ctx.fillStyle = '#2b2b3a';
  ctx.font = '20px monospace';
  ctx.textAlign = 'left';
  const lines = wrapText(text, VIEW_W - 80);
  lines.slice(0, 3).forEach((l, i) => ctx.fillText(l, 36, 482 + i * 28));
  if (showArrow && Math.floor(state.time * 2) % 2 === 0) {
    ctx.fillText('▼', VIEW_W - 56, 548);
  }
}

// ---------------------------------------------------------------------------
// Rendering — battle
// ---------------------------------------------------------------------------
function drawCritter(speciesId, cx, cy, scale, backView) {
  const sp = SPECIES[speciesId] || { color: '#e8a33d', dark: '#b5762a', shape: 'bolt' };
  const s = scale;
  const bob = Math.sin(state.time * 3) * 3 * s;
  const y = cy + bob;

  ctx.fillStyle = 'rgba(0,0,0,0.2)';
  ctx.beginPath();
  ctx.ellipse(cx, cy + 34 * s, 34 * s, 9 * s, 0, 0, Math.PI * 2);
  ctx.fill();

  // body
  ctx.fillStyle = sp.color;
  ctx.beginPath();
  ctx.ellipse(cx, y, 30 * s, 26 * s, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = backView ? sp.dark : 'rgba(255,255,255,0.35)';
  ctx.beginPath();
  ctx.ellipse(cx - 8 * s, y - (backView ? -4 : 8) * s, 12 * s, 8 * s, 0, 0, Math.PI * 2);
  ctx.fill();

  // shape accents
  ctx.fillStyle = sp.dark;
  if (sp.shape === 'leaf') {
    ctx.beginPath();
    ctx.ellipse(cx + 4 * s, y - 30 * s, 12 * s, 5 * s, -0.6, 0, Math.PI * 2);
    ctx.fill();
  } else if (sp.shape === 'wing') {
    ctx.beginPath();
    ctx.ellipse(cx - 30 * s, y - 6 * s, 10 * s, 16 * s, 0.4, 0, Math.PI * 2);
    ctx.ellipse(cx + 30 * s, y - 6 * s, 10 * s, 16 * s, -0.4, 0, Math.PI * 2);
    ctx.fill();
  } else if (sp.shape === 'fin') {
    ctx.beginPath();
    ctx.moveTo(cx, y - 24 * s);
    ctx.lineTo(cx - 8 * s, y - 40 * s);
    ctx.lineTo(cx + 8 * s, y - 38 * s);
    ctx.closePath();
    ctx.fill();
  } else { // bolt — the player's partner
    ctx.beginPath();
    ctx.moveTo(cx + 26 * s, y - 8 * s);
    ctx.lineTo(cx + 42 * s, y - 20 * s);
    ctx.lineTo(cx + 36 * s, y - 4 * s);
    ctx.lineTo(cx + 48 * s, y - 12 * s);
    ctx.closePath();
    ctx.fill();
  }

  if (!backView) {
    ctx.fillStyle = '#fff';
    ctx.beginPath();
    ctx.ellipse(cx - 10 * s, y - 6 * s, 5 * s, 6 * s, 0, 0, Math.PI * 2);
    ctx.ellipse(cx + 10 * s, y - 6 * s, 5 * s, 6 * s, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#222';
    ctx.beginPath();
    ctx.ellipse(cx - 9 * s, y - 5 * s, 2.4 * s, 3 * s, 0, 0, Math.PI * 2);
    ctx.ellipse(cx + 11 * s, y - 5 * s, 2.4 * s, 3 * s, 0, 0, Math.PI * 2);
    ctx.fill();
  }
}

function drawHpBox(x, y, name, level, hp, maxHp, showNumbers) {
  ctx.fillStyle = '#fffdf4';
  ctx.strokeStyle = '#5a4632';
  roundRect(x, y, 300, showNumbers ? 96 : 80, 10, true, true);
  ctx.fillStyle = '#2b2b3a';
  ctx.font = 'bold 18px monospace';
  ctx.textAlign = 'left';
  ctx.fillText(name, x + 18, y + 28);
  ctx.textAlign = 'right';
  ctx.fillText('Lv' + level, x + 284, y + 28);
  ctx.textAlign = 'left';

  // bar
  ctx.fillStyle = '#d0c8b0';
  ctx.fillRect(x + 18, y + 42, 264, 12);
  const ratio = hp / maxHp;
  ctx.fillStyle = ratio > 0.5 ? '#4caf50' : ratio > 0.2 ? '#f4b400' : '#e23b3b';
  ctx.fillRect(x + 18, y + 42, Math.round(264 * ratio), 12);
  ctx.strokeStyle = '#5a4632';
  ctx.lineWidth = 2;
  ctx.strokeRect(x + 18, y + 42, 264, 12);

  if (showNumbers) {
    ctx.fillStyle = '#2b2b3a';
    ctx.font = '16px monospace';
    ctx.textAlign = 'right';
    ctx.fillText(hp + ' / ' + maxHp, x + 284, y + 78);
    ctx.textAlign = 'left';
  }
}

function drawBattle() {
  const b = state.battle;
  const grad = ctx.createLinearGradient(0, 0, 0, VIEW_H);
  grad.addColorStop(0, '#cfe8b8');
  grad.addColorStop(1, '#9fce7e');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, VIEW_W, VIEW_H);

  // platforms
  ctx.fillStyle = '#b9dd9a';
  ctx.beginPath();
  ctx.ellipse(560, 240, 130, 36, 0, 0, Math.PI * 2);
  ctx.ellipse(195, 432, 150, 40, 0, 0, Math.PI * 2);
  ctx.fill();

  drawCritter(b.foe.speciesId, 560, 200, 1, false);
  drawCritter('embolt', 195, 380, 1.6, true);

  drawHpBox(24, 24, b.foe.name, b.foe.level, b.foe.hp, b.foe.maxHp, false);
  drawHpBox(444, 312, player.partner.name, player.partner.level,
    player.partner.hp, player.partner.maxHp, true);

  if (b.phase === 'msg') {
    drawTextBox(b.msgs[b.msgIndex], true);
  } else {
    drawTextBox('What will ' + player.partner.name + ' do?', false);
    ctx.fillStyle = '#fffdf4';
    ctx.strokeStyle = '#5a4632';
    roundRect(540, 444, 216, 120, 10, true, true);
    ctx.fillStyle = '#2b2b3a';
    ctx.font = 'bold 20px monospace';
    ctx.fillText('FIGHT', 600, 488);
    ctx.fillText('RUN', 600, 530);
    ctx.fillText('▶', 568, b.menuIndex === 0 ? 488 : 530);
  }
}

// ---------------------------------------------------------------------------
// Rendering — title
// ---------------------------------------------------------------------------
function drawTitle() {
  const grad = ctx.createLinearGradient(0, 0, 0, VIEW_H);
  grad.addColorStop(0, '#27406b');
  grad.addColorStop(0.6, '#4d7ab8');
  grad.addColorStop(1, '#8fd06a');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, VIEW_W, VIEW_H);

  for (let i = 0; i < 9; i++) drawTree(40 + i * 80, 470);
  drawCharacter(VIEW_W / 2 - 16, 440, 'down', 0, PALETTES.player, 0);

  ctx.textAlign = 'center';
  ctx.fillStyle = 'rgba(0,0,0,0.35)';
  ctx.font = 'bold 56px monospace';
  ctx.fillText('MAPLEWOOD TALES', VIEW_W / 2 + 4, 184);
  ctx.fillStyle = '#fffdf4';
  ctx.fillText('MAPLEWOOD TALES', VIEW_W / 2, 180);
  ctx.font = '20px monospace';
  ctx.fillStyle = '#e8f0d8';
  ctx.fillText('an original mini adventure', VIEW_W / 2, 220);

  ctx.font = '18px monospace';
  ctx.fillText('Arrows / WASD: move    Z / Enter: talk & confirm', VIEW_W / 2, 300);
  if (Math.floor(state.time * 2) % 2 === 0) {
    ctx.font = 'bold 24px monospace';
    ctx.fillText('- PRESS Z TO START -', VIEW_W / 2, 360);
  }
  ctx.textAlign = 'left';
}

// ---------------------------------------------------------------------------
// Main loop
// ---------------------------------------------------------------------------
let lastTime = 0;
function frame(now) {
  const dt = Math.min(0.05, (now - lastTime) / 1000 || 0);
  lastTime = now;
  state.time += dt;
  if (state.fade > 0) state.fade = Math.max(0, state.fade - dt * 2.5);
  if (state.locTimer > 0 && state.mode !== 'title') state.locTimer -= dt;

  if (state.mode === 'world') updateWorld(dt);

  if (state.mode === 'title') {
    drawTitle();
  } else if (state.mode === 'battle') {
    drawBattle();
  } else {
    drawWorld();
    if (state.mode === 'dialog') {
      drawTextBox(state.dialog.lines[state.dialog.index], true);
    }
  }

  if (state.fade > 0) {
    ctx.fillStyle = 'rgba(0,0,0,' + state.fade.toFixed(2) + ')';
    ctx.fillRect(0, 0, VIEW_W, VIEW_H);
  }

  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);

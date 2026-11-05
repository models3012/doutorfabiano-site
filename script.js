const CLINIC = {
  // SUBSTITUIR se mudar: número do WhatsApp com DDI + DDD, só dígitos
  whatsapp: '5562995540548',
  message: 'Olá! Vim pelo site do Dr. Fabiano e gostaria de agendar uma avaliação.',
};

function waLink(treatment) {
  const text = treatment
    ? `Olá! Vim pelo site do Dr. Fabiano e gostaria de saber mais sobre ${treatment}.`
    : CLINIC.message;
  return `https://wa.me/${CLINIC.whatsapp}?text=${encodeURIComponent(text)}`;
}

document.querySelectorAll('[data-wa]').forEach((a) => {
  a.href = waLink(a.dataset.wa);
  a.target = '_blank';
  a.rel = 'noopener';
});

document.getElementById('year').textContent = new Date().getFullYear();

/* ---------- Header: scroll state, mobile menu, active link ---------- */
const header = document.querySelector('.site-header');
const nav = document.getElementById('main-nav');
const toggle = document.getElementById('menu-toggle');
const waFloat = document.querySelector('.wa-float');
const footer = document.getElementById('contato');

let lastY = window.scrollY;
function onScroll() {
  const y = window.scrollY;
  const max = document.documentElement.scrollHeight - window.innerHeight;
  header.classList.toggle('scrolled', y > 12);
  header.style.setProperty('--progress', max > 0 ? (y / max).toFixed(4) : 0);
  if (Math.abs(y - lastY) > 6) {
    const goingDown = y > lastY;
    const keep = nav.classList.contains('open') || header.matches(':focus-within');
    header.classList.toggle('hide', goingDown && y > 480 && !keep);
    lastY = y;
  }
  const overFooter = footer.getBoundingClientRect().top < window.innerHeight - 40;
  waFloat.classList.toggle('show', y > window.innerHeight * 0.6 && !overFooter);
}
window.addEventListener('scroll', onScroll, { passive: true });
onScroll();

function setMenu(open) {
  nav.classList.toggle('open', open);
  header.classList.toggle('menu-open', open);
  toggle.setAttribute('aria-expanded', String(open));
  toggle.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
  document.body.style.overflow = open ? 'hidden' : '';
}
toggle.addEventListener('click', () => setMenu(!nav.classList.contains('open')));
nav.addEventListener('click', (e) => { if (e.target.closest('a')) setMenu(false); });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && nav.classList.contains('open')) setMenu(false); });
window.matchMedia('(min-width: 961px)').addEventListener('change', (e) => { if (e.matches) setMenu(false); });

const navLinks = [...nav.querySelectorAll('ul a')];
const sections = navLinks.map((a) => document.querySelector(a.getAttribute('href'))).filter(Boolean);
const activeObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (!entry.isIntersecting) return;
    navLinks.forEach((a) => a.classList.toggle('active', a.getAttribute('href') === `#${entry.target.id}`));
  });
}, { rootMargin: '-45% 0px -50% 0px' });
sections.forEach((s) => activeObserver.observe(s));

/* ---------- Scroll reveal ---------- */
const reveals = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window) {
  document.querySelectorAll('.treat-grid, .why-grid, .hero-copy, .journey, .exp-grid').forEach((group) => {
    group.querySelectorAll(':scope > .reveal').forEach((el, i) => el.style.setProperty('--d', `${i * 0.07}s`));
  });
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('in');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.05 });
  reveals.forEach((el) => revealObserver.observe(el));
} else {
  reveals.forEach((el) => el.classList.add('in'));
}

/* ---------- Before / After ---------- */
const CASES = [
  {
    slug: 'lentes',
    kicker: 'Caso 01 · Lentes de contato',
    title: 'Lentes de contato em porcelana',
    desc: 'Fechamento de diastema, correção de cor e proporção dos dentes anteriores com mínimo desgaste.',
    dur: '21 dias', ses: '3', el: '10 lentes',
  },
  {
    slug: 'clareamento',
    kicker: 'Caso 02 · Clareamento',
    title: 'Clareamento a laser',
    desc: 'Protocolo em consultório com controle de sensibilidade e ganho de vários tons na escala de cor.',
    dur: '1 dia', ses: '1', el: 'Arcada completa',
  },
  {
    slug: 'invisalign',
    kicker: 'Caso 03 · Invisalign',
    title: 'Alinhamento com Invisalign',
    desc: 'Correção de apinhamento e rotações com alinhadores transparentes, sem bráquetes.',
    dur: '11 meses', ses: '8', el: '22 alinhadores',
  },
  {
    slug: 'diastema',
    kicker: 'Caso 04 · Diastema',
    title: 'Fechamento de diastemas',
    desc: 'Espaços entre os dentes fechados com lentes ultrafinas, preservando a anatomia natural.',
    dur: '14 dias', ses: '2', el: '6 lentes',
  },
  {
    slug: 'facetas',
    kicker: 'Caso 05 · Facetas',
    title: 'Facetas para harmonia de cor',
    desc: 'Cor uniforme e brilho natural em toda a linha do sorriso, mantendo o formato original dos dentes.',
    dur: '28 dias', ses: '3', el: '10 facetas',
  },
];

const slider = document.getElementById('ba-slider');
const range = document.getElementById('ba-range');
const beforeImg = document.getElementById('ba-before');
const afterImg = document.getElementById('ba-after');
const info = document.querySelector('.ba-info');
const tabs = [...document.querySelectorAll('.ba-tab')];
const src = (slug, kind) => `images/casos/${slug}-${kind}.webp`;

function setPos(p) {
  const v = Math.max(0, Math.min(100, p));
  slider.style.setProperty('--pos', `${v}%`);
  range.value = Math.round(v);
}

function loadImage(url) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = img.onerror = () => resolve();
    img.src = url;
  });
}

let current = 0;
async function showCase(i) {
  current = i;
  const c = CASES[i];
  tabs.forEach((t, j) => t.setAttribute('aria-selected', String(i === j)));
  slider.classList.add('loading');
  await Promise.all([loadImage(src(c.slug, 'antes')), loadImage(src(c.slug, 'depois'))]);
  if (current !== i) return;
  beforeImg.src = src(c.slug, 'antes');
  afterImg.src = src(c.slug, 'depois');
  beforeImg.alt = `Antes: ${c.title}`;
  afterImg.alt = `Depois: ${c.title}`;
  slider.classList.remove('loading');
  document.getElementById('ba-kicker').textContent = c.kicker;
  document.getElementById('ba-title').textContent = c.title;
  document.getElementById('ba-desc').textContent = c.desc;
  document.getElementById('ba-dur').textContent = c.dur;
  document.getElementById('ba-ses').textContent = c.ses;
  document.getElementById('ba-el').textContent = c.el;
  info.classList.remove('swap');
  void info.offsetWidth;
  info.classList.add('swap');
}

tabs.forEach((t, i) => t.addEventListener('click', () => { showCase(i); setPos(50); }));
tabs.forEach((t, i) => t.addEventListener('keydown', (e) => {
  if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
  const next = (i + (e.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
  tabs[next].focus();
  tabs[next].click();
}));

// A drag only starts after a clear horizontal move, so vertical swipes keep scrolling the page.
let pointerId = null, startX = 0, dragging = false;
function posFromEvent(e) {
  const r = slider.getBoundingClientRect();
  setPos(((e.clientX - r.left) / r.width) * 100);
}
slider.addEventListener('pointerdown', (e) => {
  pointerId = e.pointerId;
  startX = e.clientX;
  dragging = false;
  if (e.pointerType === 'mouse') {
    dragging = true;
    slider.setPointerCapture(e.pointerId);
    slider.classList.add('dragging');
    posFromEvent(e);
  }
});
slider.addEventListener('pointermove', (e) => {
  if (e.pointerId !== pointerId) return;
  if (!dragging && Math.abs(e.clientX - startX) > 6) {
    dragging = true;
    slider.setPointerCapture(e.pointerId);
    slider.classList.add('dragging');
  }
  if (dragging) posFromEvent(e);
});
function endDrag(e) {
  if (e.pointerId !== pointerId) return;
  if (!dragging && e.type === 'pointerup') posFromEvent(e);
  pointerId = null;
  dragging = false;
  slider.classList.remove('dragging');
}
slider.addEventListener('pointerup', endDrag);
slider.addEventListener('pointercancel', endDrag);
range.addEventListener('input', () => setPos(Number(range.value)));

setPos(50);

/* ---------- Hero: animated 3D-scan reveal cycling through the cases ---------- */
const scan = document.getElementById('hero-scan');
const arch = scan.closest('.arch');
const scanBefore = scan.querySelector('.scan-before');
const scanAfter = scan.querySelector('.scan-after');
const scanCase = document.getElementById('scan-case');
const scanStage = document.getElementById('scan-stage');
const SCAN_LABELS = ['Lentes de contato', 'Clareamento', 'Invisalign', 'Diastema', 'Facetas'];
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

let heroVisible = true;
const waiters = [];
const canRun = () => heroVisible && !document.hidden;
const waitRun = () => (canRun() ? Promise.resolve() : new Promise((r) => waiters.push(r)));
const wake = () => { if (canRun()) waiters.splice(0).forEach((r) => r()); };
new IntersectionObserver(([e]) => { heroVisible = e.isIntersecting; wake(); }).observe(arch);
document.addEventListener('visibilitychange', wake);

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const setScan = (p) => scan.style.setProperty('--p', `${p}%`);
function setStage(text) {
  scanStage.classList.add('swap');
  setTimeout(() => { scanStage.textContent = text; scanStage.classList.remove('swap'); }, 250);
}
function sweep(duration) {
  return new Promise((resolve) => {
    const t0 = performance.now();
    const frame = (now) => {
      const t = Math.min(1, (now - t0) / duration);
      const e = t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2;
      setScan(e * 100);
      if (t < 1) requestAnimationFrame(frame); else resolve();
    };
    requestAnimationFrame(frame);
  });
}
function restartZoom(img) {
  img.style.animation = 'none';
  void img.offsetWidth;
  img.style.animation = '';
}

async function runHeroScan() {
  let i = 0;
  await sleep(2800);
  for (;;) {
    await waitRun();
    i = (i + 1) % CASES.length;
    const slug = CASES[i].slug;
    await Promise.all([loadImage(src(slug, 'antes')), loadImage(src(slug, 'depois'))]);
    scan.classList.add('fading');
    await sleep(600);
    setScan(0);
    scanBefore.src = src(slug, 'antes');
    scanAfter.src = src(slug, 'depois');
    scanAfter.alt = `Depois: ${CASES[i].title}`;
    restartZoom(scanBefore);
    restartZoom(scanAfter);
    scanCase.textContent = SCAN_LABELS[i];
    scanStage.textContent = 'Antes';
    scan.classList.remove('fading');
    await sleep(1500);
    await waitRun();
    scan.classList.add('scanning');
    arch.classList.add('is-scanning');
    setStage('Escaneando');
    await sweep(2400);
    scan.classList.remove('scanning');
    arch.classList.remove('is-scanning');
    setStage('Depois');
    await sleep(3000);
  }
}
if (!reduceMotion) runHeroScan();

// Warm the cache for the other cases once the page is idle.
(window.requestIdleCallback || ((fn) => setTimeout(fn, 1500)))(() => {
  CASES.slice(1).forEach((c) => { loadImage(src(c.slug, 'antes')); loadImage(src(c.slug, 'depois')); });
});

/* Gentle hint animation the first time the slider is seen */
const hintObserver = new IntersectionObserver(([entry]) => {
  if (!entry.isIntersecting || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  hintObserver.disconnect();
  const frames = [50, 36, 64, 50];
  let k = 0;
  const step = () => {
    if (dragging || k >= frames.length - 1) return;
    const from = frames[k], to = frames[k + 1], t0 = performance.now();
    const tick = (now) => {
      const t = Math.min(1, (now - t0) / 650);
      const ease = t < 0.5 ? 2 * t * t : 1 - (-2 * t + 2) ** 2 / 2;
      if (!dragging) setPos(from + (to - from) * ease);
      if (t < 1) requestAnimationFrame(tick); else { k++; step(); }
    };
    requestAnimationFrame(tick);
  };
  setTimeout(step, 500);
}, { threshold: 0.6 });
hintObserver.observe(slider);

/* ---------- Testimonials carousel ---------- */
const track = document.getElementById('testi-track');
const prev = document.getElementById('testi-prev');
const next = document.getElementById('testi-next');

function cardStep() {
  const card = track.querySelector('.testi-card');
  return card.getBoundingClientRect().width + parseFloat(getComputedStyle(track).columnGap || 20);
}
function updateNav() {
  prev.disabled = track.scrollLeft < 4;
  next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 4;
}
prev.addEventListener('click', () => track.scrollBy({ left: -cardStep() }));
next.addEventListener('click', () => track.scrollBy({ left: cardStep() }));
track.addEventListener('scroll', updateNav, { passive: true });
track.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowRight') { e.preventDefault(); next.click(); }
  if (e.key === 'ArrowLeft') { e.preventDefault(); prev.click(); }
});
window.addEventListener('resize', updateNav);
updateNav();

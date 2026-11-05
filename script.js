const CLINIC = {
  // SUBSTITUIR se mudar: número do WhatsApp com DDI + DDD, só dígitos
  whatsapp: '5562995540548',
  message: 'Olá! Vim pelo site do Dr. Fabiano e gostaria de agendar uma avaliação.',
  // Cole aqui o ID do Google Analytics 4 (ex.: 'G-XXXXXXXXXX'). Vazio = nada é carregado.
  ga4: '',
};

const $ = (sel) => document.querySelector(sel);
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

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

const year = $('#year');
if (year) year.textContent = new Date().getFullYear();

/* ---------- Header: scroll state, hide on scroll down, progress, mobile menu ---------- */
const header = $('.site-header');
const nav = $('#main-nav');
const toggle = $('#menu-toggle');
const waFloat = $('.wa-float');
const footer = $('#contato');

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
  if (waFloat && footer) {
    const overFooter = footer.getBoundingClientRect().top < window.innerHeight - 40;
    waFloat.classList.toggle('show', y > window.innerHeight * 0.6 && !overFooter);
  }
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

const navLinks = [...nav.querySelectorAll(':scope > ul > li > a')];
const sections = navLinks
  .map((a) => { const h = a.getAttribute('href').split('#')[1]; return h ? document.getElementById(h) : null; })
  .filter(Boolean);
const activeObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (!entry.isIntersecting) return;
    navLinks.forEach((a) => a.classList.toggle('active', a.getAttribute('href').endsWith(`#${entry.target.id}`)));
  });
}, { rootMargin: '-45% 0px -50% 0px' });
sections.forEach((s) => activeObserver.observe(s));

/* ---------- Scroll reveal ---------- */
const reveals = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window) {
  document.querySelectorAll('.treat-grid, .why-grid, .hero-copy, .journey, .exp-grid, .price-grid, .related-grid').forEach((group) => {
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

/* ---------- Shared case data ---------- */
const CASES = [
  { slug: 'lentes', label: 'Lentes de contato', kicker: 'Caso 01 · Lentes de contato', title: 'Lentes de contato em porcelana',
    desc: 'Fechamento de diastema, correção de cor e proporção dos dentes anteriores com mínimo desgaste.', dur: '21 dias', ses: '3', el: '10 lentes' },
  { slug: 'clareamento', label: 'Clareamento', kicker: 'Caso 02 · Clareamento', title: 'Clareamento a laser',
    desc: 'Protocolo em consultório com controle de sensibilidade e ganho de vários tons na escala de cor.', dur: '1 dia', ses: '1', el: 'Arcada completa' },
  { slug: 'invisalign', label: 'Invisalign', kicker: 'Caso 03 · Invisalign', title: 'Alinhamento com Invisalign',
    desc: 'Correção de apinhamento e rotações com alinhadores transparentes, sem bráquetes.', dur: '11 meses', ses: '8', el: '22 alinhadores' },
  { slug: 'diastema', label: 'Diastema', kicker: 'Caso 04 · Diastema', title: 'Fechamento de diastemas',
    desc: 'Espaços entre os dentes fechados com lentes ultrafinas, preservando a anatomia natural.', dur: '14 dias', ses: '2', el: '6 lentes' },
  { slug: 'facetas', label: 'Facetas', kicker: 'Caso 05 · Facetas', title: 'Facetas para harmonia de cor',
    desc: 'Cor uniforme e brilho natural em toda a linha do sorriso, mantendo o formato original dos dentes.', dur: '28 dias', ses: '3', el: '10 facetas' },
];
const src = (slug, kind, size = '') => `/images/casos/${slug}-${kind}${size}.webp`;
function loadImage(url) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = img.onerror = () => resolve();
    img.src = url;
  });
}

/* ---------- Before / After slider (home) ---------- */
const slider = $('#ba-slider');
if (slider) {
  const range = $('#ba-range');
  const beforeImg = $('#ba-before');
  const afterImg = $('#ba-after');
  const info = $('.ba-info');
  const tabs = [...document.querySelectorAll('.ba-tab')];

  const setPos = (p) => {
    const v = Math.max(0, Math.min(100, p));
    slider.style.setProperty('--pos', `${v}%`);
    range.value = Math.round(v);
  };

  let current = 0;
  const showCase = async (i) => {
    current = i;
    const c = CASES[i];
    tabs.forEach((t, j) => t.setAttribute('aria-selected', String(i === j)));
    slider.classList.add('loading');
    await Promise.all([loadImage(src(c.slug, 'antes')), loadImage(src(c.slug, 'depois'))]);
    if (current !== i) return;
    beforeImg.src = src(c.slug, 'antes');
    afterImg.src = src(c.slug, 'depois');
    beforeImg.alt = `Antes: ${c.title} – Dr. Fabiano, Goiânia`;
    afterImg.alt = `Depois: ${c.title} – Dr. Fabiano, Goiânia`;
    slider.classList.remove('loading');
    $('#ba-kicker').textContent = c.kicker;
    $('#ba-title').textContent = c.title;
    $('#ba-desc').textContent = c.desc;
    $('#ba-dur').textContent = c.dur;
    $('#ba-ses').textContent = c.ses;
    $('#ba-el').textContent = c.el;
    info.classList.remove('swap');
    void info.offsetWidth;
    info.classList.add('swap');
  };

  tabs.forEach((t, i) => t.addEventListener('click', () => { showCase(i); setPos(50); }));
  tabs.forEach((t, i) => t.addEventListener('keydown', (e) => {
    if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
    const next = (i + (e.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
    tabs[next].focus();
    tabs[next].click();
  }));

  // A drag only starts after a clear horizontal move, so vertical swipes keep scrolling the page.
  let pointerId = null, startX = 0, dragging = false;
  const posFromEvent = (e) => {
    const r = slider.getBoundingClientRect();
    setPos(((e.clientX - r.left) / r.width) * 100);
  };
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
  const endDrag = (e) => {
    if (e.pointerId !== pointerId) return;
    if (!dragging && e.type === 'pointerup') posFromEvent(e);
    pointerId = null;
    dragging = false;
    slider.classList.remove('dragging');
  };
  slider.addEventListener('pointerup', endDrag);
  slider.addEventListener('pointercancel', endDrag);
  range.addEventListener('input', () => setPos(Number(range.value)));
  setPos(50);

  (window.requestIdleCallback || ((fn) => setTimeout(fn, 1500)))(() => {
    CASES.slice(1).forEach((c) => { loadImage(src(c.slug, 'antes')); loadImage(src(c.slug, 'depois')); });
  });

  const hintObserver = new IntersectionObserver(([entry]) => {
    if (!entry.isIntersecting || reduceMotion) return;
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
}

/* ---------- Hero: animated 3D-scan reveal cycling through the cases ---------- */
const scan = $('#hero-scan');
if (scan && !reduceMotion) {
  const arch = scan.closest('.arch');
  const scanBefore = scan.querySelector('.scan-before');
  const scanAfter = scan.querySelector('.scan-after');
  const scanCase = $('#scan-case');
  const scanStage = $('#scan-stage');

  let heroVisible = true;
  const waiters = [];
  const canRun = () => heroVisible && !document.hidden;
  const waitRun = () => (canRun() ? Promise.resolve() : new Promise((r) => waiters.push(r)));
  const wake = () => { if (canRun()) waiters.splice(0).forEach((r) => r()); };
  new IntersectionObserver(([e]) => { heroVisible = e.isIntersecting; wake(); }).observe(arch);
  document.addEventListener('visibilitychange', wake);

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const setScan = (p) => scan.style.setProperty('--p', `${p}%`);
  const setStage = (text) => {
    scanStage.classList.add('swap');
    setTimeout(() => { scanStage.textContent = text; scanStage.classList.remove('swap'); }, 250);
  };
  const sweep = (duration) => new Promise((resolve) => {
    const t0 = performance.now();
    const frame = (now) => {
      const t = Math.min(1, (now - t0) / duration);
      const e = t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2;
      setScan(e * 100);
      if (t < 1) requestAnimationFrame(frame); else resolve();
    };
    requestAnimationFrame(frame);
  });
  const restartZoom = (img) => { img.style.animation = 'none'; void img.offsetWidth; img.style.animation = ''; };

  (async () => {
    let i = 0;
    await sleep(2800);
    for (;;) {
      await waitRun();
      i = (i + 1) % CASES.length;
      const c = CASES[i];
      await Promise.all([loadImage(src(c.slug, 'antes', '-m')), loadImage(src(c.slug, 'depois', '-m'))]);
      scan.classList.add('fading');
      await sleep(600);
      setScan(0);
      scanBefore.src = src(c.slug, 'antes', '-m');
      scanAfter.src = src(c.slug, 'depois', '-m');
      scanAfter.alt = `Depois: ${c.title} – Dr. Fabiano, Goiânia`;
      restartZoom(scanBefore);
      restartZoom(scanAfter);
      scanCase.textContent = c.label;
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
  })();
}

/* ---------- Testimonials carousel ---------- */
const track = $('#testi-track');
if (track) {
  const prev = $('#testi-prev');
  const next = $('#testi-next');
  const cardStep = () => {
    const card = track.querySelector('.testi-card');
    return card.getBoundingClientRect().width + parseFloat(getComputedStyle(track).columnGap || 20);
  };
  const updateNav = () => {
    prev.disabled = track.scrollLeft < 4;
    next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 4;
  };
  prev.addEventListener('click', () => track.scrollBy({ left: -cardStep() }));
  next.addEventListener('click', () => track.scrollBy({ left: cardStep() }));
  track.addEventListener('scroll', updateNav, { passive: true });
  track.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') { e.preventDefault(); next.click(); }
    if (e.key === 'ArrowLeft') { e.preventDefault(); prev.click(); }
  });
  window.addEventListener('resize', updateNav);
  updateNav();
}

/* ---------- Cookie consent (LGPD) + Google Analytics 4 ---------- */
const CONSENT_KEY = 'drfabiano-cookies';
const readConsent = () => { try { return localStorage.getItem(CONSENT_KEY); } catch { return null; } };
const saveConsent = (v) => { try { localStorage.setItem(CONSENT_KEY, v); } catch { /* sem armazenamento: pergunta de novo na próxima visita */ } };

function loadAnalytics() {
  if (!CLINIC.ga4 || window.gtag) return;
  window.dataLayer = window.dataLayer || [];
  window.gtag = function gtag() { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', CLINIC.ga4, { anonymize_ip: true });
  const s = document.createElement('script');
  s.async = true;
  s.src = `https://www.googletagmanager.com/gtag/js?id=${CLINIC.ga4}`;
  document.head.appendChild(s);
}

function showCookieBanner() {
  if ($('.cookie-banner')) return;
  const box = document.createElement('div');
  box.className = 'cookie-banner';
  box.setAttribute('role', 'dialog');
  box.setAttribute('aria-label', 'Aviso de cookies');
  box.innerHTML = `
    <strong>Sua privacidade</strong>
    <p>Usamos cookies essenciais para o site funcionar e, com a sua permissão, cookies de medição para entender quais conteúdos ajudam mais nossos pacientes. Saiba mais na <a href="/politica-de-cookies/">Política de Cookies</a>.</p>
    <div class="cookie-actions">
      <button type="button" class="btn btn-navy" data-consent="accepted">Aceitar</button>
      <button type="button" class="btn btn-ghost" data-consent="essential">Somente essenciais</button>
    </div>`;
  box.addEventListener('click', (e) => {
    const choice = e.target.closest('[data-consent]')?.dataset.consent;
    if (!choice) return;
    saveConsent(choice);
    box.remove();
    if (choice === 'accepted') loadAnalytics();
  });
  document.body.appendChild(box);
}

const consent = readConsent();
if (consent === 'accepted') loadAnalytics();
else if (!consent) setTimeout(showCookieBanner, 1200);
document.querySelectorAll('[data-cookie-settings]').forEach((b) => b.addEventListener('click', showCookieBanner));

// Lead tracking: WhatsApp and phone clicks become GA4 events (only when analytics was accepted).
document.addEventListener('click', (e) => {
  if (!window.gtag) return;
  const wa = e.target.closest('[data-wa]');
  if (wa) window.gtag('event', 'whatsapp_click', { treatment: wa.dataset.wa || 'geral', page: location.pathname });
  const tel = e.target.closest('a[href^="tel:"]');
  if (tel) window.gtag('event', 'phone_click', { page: location.pathname });
});

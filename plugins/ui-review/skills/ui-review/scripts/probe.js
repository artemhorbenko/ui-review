// ui-review page probe. One async function, no dependencies.
// Used by inspect_ui.py (Playwright) and, without a shell, pasted into a
// browser tool's JavaScript runner: `(<this file>)({sels: {cta: '.btn'}})`.
// Reads only: it scrolls the page to measure, then scrolls back to the top.
// Returns measurements for the viewport it runs in; boxes are % of the
// viewport (or of the whole page with full: true) at scroll 0.
async ({sels = {}, full = false, scan = true} = {}) => {
  const vw = innerWidth, vh = innerHeight, de = document.documentElement;
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const parse = c => { const m = c && c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number); return {r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1}; };
  const hex = c => c ? '#' + [c.r, c.g, c.b].map(v => Math.round(v).toString(16).padStart(2, '0')).join('') + (c.a < 1 ? Math.round(c.a * 255).toString(16).padStart(2, '0') : '') : null;
  const blend = (t, b) => ({r: t.r * t.a + b.r * (1 - t.a), g: t.g * t.a + b.g * (1 - t.a), b: t.b * t.a + b.b * (1 - t.a), a: 1});
  const lum = c => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const visible = el => { const r = el.getBoundingClientRect(), cs = getComputedStyle(el); return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none' && parseFloat(cs.opacity) > 0.05 && cs.clip !== 'rect(0px, 0px, 0px, 0px)'; };
  const ownText = el => [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.nodeValue).join(' ').replace(/\s+/g, ' ').trim();
  const path = el => { if (el.id) return '#' + CSS.escape(el.id); const parts = [];
    for (let e = el, i = 0; e && e !== document.body && i < 3; e = e.parentElement, i++) {
      if (e.id) { parts.unshift('#' + CSS.escape(e.id)); break; }
      parts.unshift(e.tagName.toLowerCase() + [...e.classList].filter(c => !/^(is-|has-|js-)/.test(c)).slice(0, 2).map(c => '.' + CSS.escape(c)).join('')); }
    return parts.join(' > '); };
  // Background under an element: the paint stack at a point inside it, so
  // backgrounds from siblings, overlays and pseudo-elements count too.
  const layer = cs => (cs.backgroundImage && cs.backgroundImage !== 'none') ? 'img' : (() => { const c = parse(cs.backgroundColor); return c && c.a > 0 ? c : null; })();
  const fin = ls => { if (ls.includes('img')) return null; let b = {r: 255, g: 255, b: 255, a: 1}; for (let i = ls.length - 1; i >= 0; i--) b = blend(ls[i], b); return b; };
  const bgAt = el => { const r = el.getBoundingClientRect();
    const x = Math.min(Math.max(r.left + Math.min(8, r.width / 2), 1), vw - 2), y = Math.min(Math.max(r.top + r.height / 2, 1), vh - 2);
    const ls = [];
    for (const e of document.elementsFromPoint(x, y)) {
      if (e !== el && el.contains(e)) continue;
      for (const pe of ['::after', '::before']) { const p = getComputedStyle(e, pe);
        if (p.content && p.content !== 'none' && p.content !== 'normal' && (p.position === 'absolute' || p.position === 'fixed')) { const l = layer(p); if (l) { ls.push(l); if (l === 'img' || l.a >= 1) return fin(ls); } } }
      const l = layer(getComputedStyle(e)); if (l) { ls.push(l); if (l === 'img' || l.a >= 1) return fin(ls); } }
    return fin(ls); };
  const contrastOf = el => { const cs = getComputedStyle(el), fg = parse(cs.color), bg = bgAt(el);
    if (!fg || !bg) return {unknown: true, fg: hex(fg)};
    const f = fg.a < 1 ? blend(fg, bg) : fg, size = parseFloat(cs.fontSize), w = parseInt(cs.fontWeight) || 400;
    const large = size >= 24 || (size >= 18.66 && w >= 700), r = Math.round(ratio(f, bg) * 100) / 100, need = large ? 3 : 4.5;
    return {ratio: r, need, pass: r >= need, fg: hex(f), bg: hex(bg), size, weight: w, large}; };

  // Perceived performance: buffered layout shifts and LCP.
  const perf = {cls: null, lcp: null, shifts: []};
  try {
    await new Promise(res => { let cls = 0; const po = new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) { cls += e.value; if (perf.shifts.length < 5) perf.shifts.push({value: Math.round(e.value * 1000) / 1000, t: Math.round(e.startTime), nodes: (e.sources || []).map(s => s.node && s.node.nodeType === 1 ? path(s.node) : '').filter(Boolean).slice(0, 3)}); } perf.cls = Math.round(cls * 1000) / 1000; });
      po.observe({type: 'layout-shift', buffered: true}); setTimeout(() => { po.disconnect(); if (perf.cls === null) perf.cls = 0; res(); }, 150); });
    await new Promise(res => { const po = new PerformanceObserver(l => { const e = l.getEntries().pop(); if (e) perf.lcp = {ms: Math.round(e.startTime), el: e.element ? path(e.element) : ''}; });
      po.observe({type: 'largest-contentful-paint', buffered: true}); setTimeout(() => { po.disconnect(); res(); }, 150); });
  } catch (e) { perf.error = String(e); }

  // Contrast over the whole page: scroll in steps, measure what is fully in view.
  const contrast = {total: 0, pass: 0, unknown: 0, failN: 0, fails: []};
  const textEls = new Set(), seenC = new Set();
  const H = scan ? de.scrollHeight : vh;
  for (let y = 0; y < H; y += Math.round(vh * 0.8)) {
    if (scan) { scrollTo({top: y, behavior: 'instant'}); await sleep(250); }
    for (const el of document.querySelectorAll('body *')) {
      if (textEls.has(el) || ['SCRIPT', 'STYLE', 'NOSCRIPT', 'SVG', 'OPTION'].includes(el.tagName)) continue;
      const t = ownText(el); if (t.length < 2 || !visible(el)) continue;
      const r = el.getBoundingClientRect(); if (r.top < 0 || r.bottom > vh || r.left < 0 || r.right > vw) continue;
      textEls.add(el); contrast.total++;
      const c = contrastOf(el);
      if (c.unknown) { contrast.unknown++; continue; }
      if (c.pass) contrast.pass++;
      else { contrast.failN++; const k = c.fg + c.bg + c.size; if (!seenC.has(k) && contrast.fails.length < 25) { seenC.add(k); contrast.fails.push({text: t.slice(0, 50), sel: path(el), ratio: c.ratio, need: c.need, fg: c.fg, bg: c.bg, size: c.size + 'px', pageY: Math.round(r.top + scrollY)}); } }
    }
    if (!scan) break;
  }
  if (scan) { scrollTo({top: 0, behavior: 'instant'}); await sleep(300); }

  // Scale: what the page actually uses (typography, colour, radius, spacing).
  const count = (m, k) => m.set(k, (m.get(k) || 0) + 1);
  const fs = new Map(), fw = new Map(), ff = new Map(), col = new Map(), bgc = new Map(), rad = new Map(), sp = new Map(), lh = [];
  const all = [...document.querySelectorAll('body *')].filter(visible);
  for (const el of all) { const cs = getComputedStyle(el);
    if (ownText(el).length > 1) { count(fs, cs.fontSize); count(fw, cs.fontWeight); count(ff, cs.fontFamily.split(',')[0].replace(/["']/g, '').trim()); count(col, hex(parse(cs.color)));
      const l = parseFloat(cs.lineHeight), s = parseFloat(cs.fontSize); if (l && s && s < 24) lh.push(Math.round(l / s * 100) / 100); }
    const b = parse(cs.backgroundColor); if (b && b.a > 0) count(bgc, hex(b));
    if (cs.borderTopLeftRadius !== '0px') count(rad, cs.borderTopLeftRadius);
    for (const p of ['paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft', 'marginTop', 'marginBottom', 'rowGap', 'columnGap']) { const v = parseFloat(cs[p]); if (v > 0 && v < 200) count(sp, Math.round(v)); } }
  const top = (m, n = 12) => [...m.entries()].sort((a, b) => b[1] - a[1]).slice(0, n).map(([k, v]) => k + ' ×' + v);
  const spVals = [...sp.keys()], onScale = spVals.filter(v => v % 4 === 0).length;
  const scale = {fontSizes: {distinct: fs.size, top: top(fs)}, fontWeights: top(fw, 6), fontFamilies: top(ff, 5), textColours: {distinct: col.size, top: top(col, 10)},
    backgrounds: {distinct: bgc.size, top: top(bgc, 10)}, radii: {distinct: rad.size, top: top(rad, 8)},
    spacing: {distinct: spVals.length, onScale4: onScale, offScale: spVals.filter(v => v % 4 !== 0).sort((a, b) => a - b).slice(0, 20)},
    bodyLineHeight: lh.length ? lh.sort((a, b) => a - b)[Math.floor(lh.length / 2)] : null};

  // Stylesheet features: dark mode and reduced motion.
  const css = {sheets: 0, unreadable: 0, darkRules: 0, reducedMotionRules: 0};
  const walk = rules => { for (const r of rules) { if (r.media) { const m = r.media.mediaText; if (/prefers-color-scheme:\s*dark/.test(m)) css.darkRules++; if (/prefers-reduced-motion/.test(m)) css.reducedMotionRules++; }
    if (r.cssRules) walk(r.cssRules); } };
  for (const sh of document.styleSheets) { css.sheets++; try { walk(sh.cssRules); } catch (e) { css.unreadable++; } }
  css.colorSchemeMeta = (document.querySelector('meta[name=color-scheme]') || {}).content || '';
  css.rootColorScheme = getComputedStyle(de).colorScheme;

  // Motion: running animations now.
  const anims = document.getAnimations ? document.getAnimations() : [];
  const motion = {running: anims.filter(a => a.playState === 'running').length, infinite: anims.filter(a => a.effect && a.effect.getTiming && a.effect.getTiming().iterations === Infinity).length,
    targets: [...new Set(anims.map(a => a.effect && a.effect.target ? path(a.effect.target) : '').filter(Boolean))].slice(0, 8),
    autoplayMedia: [...document.querySelectorAll('video[autoplay]')].length};

  // Tap targets, small text, alt, fixed bars.
  const tSel = 'a[href], button, input:not([type=hidden]), select, textarea, summary, [role=button], [role=link], [role=tab], [onclick]';
  const targets = {total: 0, pass24: 0, pass44: 0, fails24: [], fails44: []};
  for (const el of document.querySelectorAll(tSel)) { if (!visible(el)) continue;
    if (el.tagName === 'A' && el.parentElement && ownText(el.parentElement).length > 0) continue; // inline link: WCAG 2.5.8 exception
    const r = el.getBoundingClientRect(), w = Math.round(r.width), h = Math.round(r.height); targets.total++;
    const item = {text: (el.innerText || el.getAttribute('aria-label') || el.value || '').trim().slice(0, 40), sel: path(el), size: w + '×' + h};
    if (w >= 24 && h >= 24) targets.pass24++; else if (targets.fails24.length < 20) targets.fails24.push(item);
    if (w >= 44 && h >= 44) targets.pass44++; else if (targets.fails44.length < 8) targets.fails44.push(item); }
  const smallEls = [...textEls].filter(el => parseFloat(getComputedStyle(el).fontSize) < 12);
  const small = {total: textEls.size, pass: textEls.size - smallEls.length, fails: smallEls.slice(0, 12).map(el => ({text: ownText(el).slice(0, 40), sel: path(el), size: getComputedStyle(el).fontSize}))};
  const imgs = [...document.querySelectorAll('img')].filter(visible);
  const alt = {total: imgs.length, pass: imgs.filter(i => i.hasAttribute('alt')).length, fails: imgs.filter(i => !i.hasAttribute('alt')).slice(0, 12).map(i => ({sel: path(i), src: (i.currentSrc || i.src).split('/').pop().slice(0, 50)}))};
  const unnamed = [...document.querySelectorAll('a[href], button')].filter(el => visible(el) && !(el.innerText || '').trim() && !el.getAttribute('aria-label') && !el.getAttribute('aria-labelledby') && !el.getAttribute('title') && ![...el.querySelectorAll('img')].some(i => (i.getAttribute('alt') || '').trim()) && ![...el.querySelectorAll('svg title')].length);
  const iconNames = {total: [...document.querySelectorAll('a[href], button')].filter(el => visible(el) && !(el.innerText || '').trim()).length, fails: unnamed.slice(0, 12).map(el => ({sel: path(el), href: (el.getAttribute('href') || '').slice(0, 50)}))};
  iconNames.pass = iconNames.total - unnamed.length;
  const fixed = [...document.querySelectorAll('body *')].filter(el => { const p = getComputedStyle(el).position; return (p === 'fixed' || p === 'sticky') && visible(el); })
    .map(el => { const r = el.getBoundingClientRect(); return {sel: path(el), top: Math.round(r.top), h: Math.round(r.height), w: Math.round(r.width)}; })
    .filter(f => f.w > vw * 0.5 && f.h < vh * 0.6 && (f.top <= 130 || f.top + f.h >= vh - 1));
  const fixedTop = fixed.filter(f => f.top <= 130).reduce((m, f) => Math.max(m, f.top + f.h), 0);

  // Requested elements.
  const box = el => { const r = el.getBoundingClientRect(), W = full ? Math.max(de.scrollWidth, vw) : vw, Hh = full ? Math.max(de.scrollHeight, vh) : vh, ox = full ? scrollX : 0, oy = full ? scrollY : 0;
    const x = (r.left + ox) / W * 100, y = (r.top + oy) / Hh * 100, cl = v => Math.round(Math.max(0, Math.min(100, v)) * 10) / 10;
    return {x: cl(x), y: cl(y), w: cl(Math.min(r.width / W * 100, 100 - Math.max(0, x))), h: cl(Math.min(r.height / Hh * 100, 100 - Math.max(0, y))), px: {x: Math.round(r.left), y: Math.round(r.top + scrollY), w: Math.round(r.width), h: Math.round(r.height)}, inView: full || (r.bottom > 0 && r.top < vh && r.right > 0 && r.left < vw)}; };
  const elements = {};
  for (const [name, sel] of Object.entries(sels)) { let list = [];
    try { list = [...document.querySelectorAll(sel)]; } catch (e) { elements[name] = {sel, error: String(e)}; continue; }
    const el = list.find(visible) || list[0]; if (!el) { elements[name] = {sel, count: 0}; continue; }
    const cs = getComputedStyle(el);
    elements[name] = {sel, count: list.length, box: box(el), text: (el.innerText || el.placeholder || '').trim().slice(0, 80),
      styles: {color: hex(parse(cs.color)), background: hex(parse(cs.backgroundColor)), backgroundImage: cs.backgroundImage.slice(0, 80), fontFamily: cs.fontFamily.split(',')[0].replace(/["']/g, ''), fontSize: cs.fontSize, fontWeight: cs.fontWeight, lineHeight: cs.lineHeight,
        padding: cs.padding, margin: cs.margin, gap: cs.gap, borderRadius: cs.borderRadius, border: cs.borderTopWidth + ' ' + cs.borderTopStyle + ' ' + hex(parse(cs.borderTopColor)), boxShadow: cs.boxShadow, position: cs.position,
        width: Math.round(el.getBoundingClientRect().width) + 'px', height: Math.round(el.getBoundingClientRect().height) + 'px', transition: cs.transitionDuration, animation: cs.animationName},
      contrast: visible(el) && el.getBoundingClientRect().top >= 0 && el.getBoundingClientRect().bottom <= vh ? contrastOf(el) : null}; }

  return {viewport: vw + 'x' + vh, shot: {w: full ? Math.max(de.scrollWidth, vw) : vw, h: full ? Math.max(de.scrollHeight, vh) : vh, full}, pageHeight: de.scrollHeight,
    lang: de.lang || '', title: document.title, hscroll: de.scrollWidth > vw + 1 ? de.scrollWidth : 0,
    fixed: {bars: fixed.slice(0, 6), topPx: fixedTop, topShare: Math.round(fixedTop / vh * 1000) / 10},
    checks: {contrast, targets, small, alt, iconNames}, scale, css, motion, perf, elements};
}

(() => {
  const P = ['Anto', 'Jothi Sai', 'John', 'Pawan', 'Dinesh', 'Pratap', 'Bhanu'];
  const SHORT = { Anto: 'An', 'Jothi Sai': 'JS', John: 'Jo', Pawan: 'Pa', Dinesh: 'Di', Pratap: 'Pr', Bhanu: 'Bh' };
  // Fixed thresholds and method settings chosen for this report.
  const K = {
    close3: '3', close5: '5', heavy: '8', regular: '10', oppmin: '15', band: '+1.5', bandneg: '−1.5',
    recentN: '20', weekmin: '8', boot: '2,000', halflife: '5', elostart: '1,500', eloK: '32', game: '21', ci: '90%'
  };
  const REGULAR = 10;
  const FMT = {
    int: d3.format(','), pct: d3.format('.1%'), pct0: d3.format('.0%'), s0: d3.format('+,'), s1: d3.format('+.1f'),
    s2: d3.format('+.2f'), f1: d3.format('.1f'), f2: d3.format('.2f')
  };
  const fmt = (v, f) => {
    if (v === null || v === undefined || v === '' || (typeof v === 'number' && Number.isNaN(v))) return '—';
    if (typeof v === 'boolean') return v ? 'Yes' : 'No';
    return FMT[f] ? FMT[f](+v) : String(v);
  };
  const color = (p) => dash.colors[Math.max(0, P.indexOf(p)) % dash.colors.length];

  const parseWhere = (s) => {
    const o = {};
    (s || '').split('&').filter(Boolean).forEach((part) => {
      const i = part.indexOf('=');
      o[decodeURIComponent(part.slice(0, i))] = decodeURIComponent(part.slice(i + 1));
    });
    return o;
  };
  const matches = (row, w) => Object.keys(w).every((k) => String(row[k]) === w[k]);
  const rowsOf = (id) => {
    const x = dash.data(id);
    return x.status === 'ok' && Array.isArray(x.data) ? x.data : null;
  };
  const stateOf = (ids) => {
    const st = ids.map((id) => dash.data(id).status);
    if (st.some((s) => s === 'error' || s === 'declined' || s === 'connect' || s === 'missing')) return 'error';
    return st.every((s) => s === 'ok') ? 'ok' : 'loading';
  };
  const keyCache = new WeakMap();
  const byKey = (rows, col) => {
    let m = keyCache.get(rows);
    if (!m) { m = new Map(); keyCache.set(rows, m); }
    if (!m.has(col)) m.set(col, new Map(rows.map((r) => [String(r[col]), r])));
    return m.get(col);
  };

  // ---------- inline values ----------
  dash.draw('f', (el) => {
    const d = rowsOf('facts');
    const r = d ? byKey(d, 'key').get(parseWhere(el.dataset.where).key) : null;
    el.textContent = r ? r.text : '—';
  });
  dash.draw('k', (el) => { el.textContent = K[el.dataset.k] || '—'; });
  dash.draw('v', (el) => {
    const d = rowsOf(el.dataset.source);
    const w = parseWhere(el.dataset.where);
    const r = d ? d.find((x) => matches(x, w)) : null;
    el.textContent = r ? fmt(r[el.dataset.field], el.dataset.fmt) : '—';
  });

  // ---------- tables ----------
  const cmpVal = (a, b) => {
    const na = a === null || a === undefined || a === ''; const nb = b === null || b === undefined || b === '';
    if (na || nb) return na === nb ? 0 : (na ? 1 : -1);
    if (typeof a === 'number' && typeof b === 'number') return a - b;
    return String(a).localeCompare(String(b), 'en', { numeric: true });
  };
  const fieldCmp = (f, desc) => (a, b) => {
    if (f === 'player' || f === 'partner' || f === 'opponent') {
      const ia = P.indexOf(a[f]); const ib = P.indexOf(b[f]);
      if (ia >= 0 && ib >= 0) return desc ? ib - ia : ia - ib;
    }
    const c = cmpVal(a[f], b[f]);
    return desc ? -c : c;
  };
  const orderCmp = (spec) => {
    const parts = spec.split(',').map((s) => (s[0] === '-' ? fieldCmp(s.slice(1), true) : fieldCmp(s, false)));
    return (a, b) => { for (const c of parts) { const v = c(a, b); if (v) return v; } return 0; };
  };
  dash.draw('t', (tbody) => {
    const table = tbody.closest('table');
    tbody.replaceChildren();
    if (!table) return;
    const d = rowsOf(table.dataset.source);
    if (!d) return;
    let rs = d.slice();
    if (table.dataset.filter) { const w = parseWhere(table.dataset.filter); rs = rs.filter((r) => matches(r, w)); }
    const ths = Array.from(table.querySelectorAll('thead th'));
    const cols = ths.map((th) => ({ f: th.dataset.field, fmt: th.dataset.fmt, num: th.classList.contains('num') }));
    let sorted = false;
    ths.forEach((th, i) => {
      const s = th.getAttribute('aria-sort');
      if (s === 'ascending' || s === 'descending') { rs.sort(fieldCmp(cols[i].f, s === 'descending')); sorted = true; }
    });
    if (!sorted && table.dataset.order) rs.sort(orderCmp(table.dataset.order));
    const keys = (table.dataset.rowKey || '').split(',');
    for (const r of rs) {
      const tr = document.createElement('tr');
      tr.dataset.key = keys.length === 1 ? String(r[keys[0]]) : keys.map((k) => encodeURIComponent(r[k])).join(',');
      for (const c of cols) {
        const td = document.createElement('td');
        td.textContent = fmt(r[c.f], c.fmt);
        if (c.num) td.className = 'num';
        if (c.f === 'rank') { const b = document.createElement('span'); b.className = `rk rk-${r[c.f]}`; b.textContent = td.textContent; td.textContent = ''; td.appendChild(b); }
        if ((c.f === 'player' || c.f === 'partner' || c.f === 'opponent') && P.includes(r[c.f])) { td.classList.add('pl'); td.style.setProperty('--pc', color(r[c.f])); }
        if (typeof r[c.f] === 'number' && c.fmt && c.fmt[0] === 's') td.classList.add(r[c.f] > 0 ? 'pos' : (r[c.f] < 0 ? 'neg' : 'zero'));
        tr.appendChild(td);
      }
      tbody.appendChild(tr);
    }
  });

  // ---------- chart helpers ----------
  const fail = (el) => {
    el.classList.remove('dash-skeleton');
    const box = document.createElement('div'); box.className = 'bx-fail';
    const dot = document.createElement('span'); dot.className = 'bx-fail-dot';
    box.append(dot, document.createTextNode('Failed to load'));
    el.replaceChildren(box);
  };
  const frame = (el, ids, h) => {
    const st = stateOf(ids);
    if (st === 'error') { fail(el); return null; }
    if (st !== 'ok') { el.replaceChildren(); el.classList.add('dash-skeleton'); return null; }
    el.classList.remove('dash-skeleton');
    const W = Math.floor(el.clientWidth);
    if (!W) return null;
    el.replaceChildren();
    const svg = d3.select(el).append('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${h}`).attr('class', 'bx-svg');
    return { svg, W, H: h, data: ids.map(rowsOf), tip: tipFor(el) };
  };
  const measure = (svg, texts, cls) => {
    const g = svg.append('g').attr('class', cls || 'bx-tx').attr('visibility', 'hidden');
    let m = 0;
    texts.forEach((t) => { const n = g.append('text').text(t).node(); m = Math.max(m, n.getComputedTextLength()); });
    g.remove();
    return Math.ceil(m);
  };
  const tipFor = (el) => {
    const t = document.createElement('div'); t.className = 'bx-tip'; t.hidden = true; el.appendChild(t);
    return {
      show(lines, x, y) {
        t.replaceChildren(...lines.map((l, i) => {
          const d = document.createElement('div');
          if (i === 0) d.className = 'bx-tip-h';
          if (l && typeof l === 'object') {
            if (l.c) { const s = document.createElement('span'); s.className = 'bx-sw'; s.style.background = l.c; d.append(s); }
            d.append(document.createTextNode(l.t));
          } else d.textContent = l;
          return d;
        }));
        t.hidden = false;
        const W = el.clientWidth; const tw = t.offsetWidth; const th = t.offsetHeight;
        let left = x + 14; if (left + tw > W) left = Math.max(0, x - tw - 14);
        let top = y - th / 2; top = Math.max(0, Math.min(top, el.clientHeight - th));
        t.style.left = `${left}px`; t.style.top = `${top}px`;
      },
      hide() { t.hidden = true; }
    };
  };
  const resolveColor = (el, c) => {
    const s = document.createElement('span'); s.style.color = c; s.style.display = 'none'; el.appendChild(s);
    const v = getComputedStyle(s).color; s.remove(); return v;
  };
  const xAxis = (g, scale, ticks, f) => {
    g.call(d3.axisBottom(scale).ticks(ticks).tickFormat(f).tickSizeOuter(0)).attr('font-size', null).attr('font-family', null).attr('class', 'bx-axis');
  };
  const weekTicks = (daily) => {
    const seen = new Map();
    daily.forEach((r) => { if (!seen.has(r.week) || r.day_index < seen.get(r.week)) seen.set(r.week, r.day_index); });
    return Array.from(seen.entries()).map(([w, i]) => ({ i, label: `W${w}` })).sort((a, b) => a.i - b.i);
  };
  const dayLabels = (daily) => {
    const m = new Map(); daily.forEach((r) => m.set(r.day_index, r.day)); return m;
  };
  const spread = (items, gap, lo, hi) => {
    items.sort((a, b) => a.y - b.y);
    for (let i = 1; i < items.length; i++) if (items[i].y - items[i - 1].y < gap) items[i].y = items[i - 1].y + gap;
    const over = items.length ? items[items.length - 1].y - hi : 0;
    if (over > 0) items.forEach((it) => { it.y -= over; });
    for (let i = items.length - 2; i >= 0; i--) if (items[i + 1].y - items[i].y < gap) items[i].y = items[i + 1].y - gap;
    items.forEach((it) => { it.y = Math.max(lo, it.y); });
    return items;
  };

  // Horizontal bars: rows [{label, v, lo, hi, text, fill, faded, tip}]
  const hbars = (c, rows, o) => {
    const { svg, W, H, tip } = c;
    const ml = measure(svg, rows.map((r) => r.label)) + 10;
    const mr = measure(svg, rows.map((r) => r.text)) + 10;
    const mt = 6; const mb = 24;
    const x = d3.scaleLinear().domain(o.domain).range([ml, W - mr]).nice();
    const y = d3.scaleBand().domain(rows.map((r) => r.label)).range([mt, H - mb]).paddingInner(0.28).paddingOuter(0.12);
    const ticks = Math.max(2, Math.floor((W - ml - mr) / 70));
    svg.append('g').attr('class', 'bx-grid').selectAll('line').data(x.ticks(ticks)).join('line')
      .attr('x1', (d) => x(d)).attr('x2', (d) => x(d)).attr('y1', mt).attr('y2', H - mb);
    xAxis(svg.append('g').attr('transform', `translate(0,${H - mb})`), x, ticks, o.axisFmt);
    const base = x(o.base !== undefined ? o.base : Math.max(o.domain[0], Math.min(0, o.domain[1])));
    const g = svg.append('g');
    rows.forEach((r) => {
      const yy = y(r.label); const bh = y.bandwidth();
      const row = g.append('g').attr('class', r.faded ? 'bx-faded' : null);
      row.append('rect').attr('class', 'bx-hit').attr('x', 0).attr('y', yy - 2).attr('width', W).attr('height', bh + 4);
      row.append('rect').attr('x', Math.min(base, x(r.v))).attr('y', yy).attr('width', Math.max(1, Math.abs(x(r.v) - base)))
        .attr('height', bh).attr('rx', 3).style('fill', r.fill);
      if (r.lo !== undefined && r.lo !== null) {
        row.append('line').attr('class', 'bx-whisk').attr('x1', x(r.lo)).attr('x2', x(r.hi)).attr('y1', yy + bh / 2).attr('y2', yy + bh / 2);
        [r.lo, r.hi].forEach((v) => row.append('line').attr('class', 'bx-whisk').attr('x1', x(v)).attr('x2', x(v)).attr('y1', yy + bh * 0.25).attr('y2', yy + bh * 0.75));
      }
      row.append('text').attr('class', 'bx-tx bx-lab').attr('x', ml - 8).attr('y', yy + bh / 2).attr('dy', '0.35em').attr('text-anchor', 'end').text(r.label);
      row.append('text').attr('class', 'bx-tx bx-val').attr('x', W - 2).attr('y', yy + bh / 2).attr('dy', '0.35em').attr('text-anchor', 'end').text(r.text);
      row.on('mousemove', (ev) => { const [px, py] = d3.pointer(ev, c.svg.node().parentNode); tip.show(r.tip, px, py); }).on('mouseleave', () => tip.hide());
    });
    if (o.ref !== undefined) {
      svg.append('line').attr('class', 'bx-ref').attr('x1', x(o.ref)).attr('x2', x(o.ref)).attr('y1', mt).attr('y2', H - mb);
    }
    if (o.zero) svg.append('line').attr('class', 'bx-zero').attr('x1', x(0)).attr('x2', x(0)).attr('y1', mt).attr('y2', H - mb);
  };

  // Line chart over session days: series [{name, color, vals: [{i, v}]}]
  const lineChart = (c, daily, series, o) => {
    const { svg, W, H, tip } = c;
    const labels = dayLabels(daily);
    const n = labels.size;
    const endTxt = series.map((s) => `${s.name} ${o.endFmt(s.vals[s.vals.length - 1].v)}`);
    const ml = measure(svg, o.yTickTexts || ['0000']) + 10;
    const mr = measure(svg, endTxt) + 12;
    const mt = 10; const mb = 24;
    const x = d3.scaleLinear().domain([0, n - 1]).range([ml, W - mr]);
    const all = series.flatMap((s) => s.vals.map((v) => v.v));
    const y = d3.scaleLinear().domain(o.yDomain || d3.extent(all)).range(o.invert ? [mt, H - mb] : [H - mb, mt]);
    if (!o.yDomain) y.nice();
    const yt = o.yTicks || y.ticks(Math.max(3, Math.floor((H - mt - mb) / 50)));
    svg.append('g').attr('class', 'bx-grid').selectAll('line').data(yt).join('line').attr('x1', ml).attr('x2', W - mr).attr('y1', (d) => y(d)).attr('y2', (d) => y(d));
    svg.append('g').selectAll('text').data(yt).join('text').attr('class', 'bx-tx').attr('x', ml - 6).attr('y', (d) => y(d)).attr('dy', '0.35em')
      .attr('text-anchor', 'end').text((d) => o.yFmt(d));
    const wt = weekTicks(daily);
    const xg = svg.append('g').attr('transform', `translate(0,${H - mb})`).attr('class', 'bx-axis');
    xg.append('line').attr('x1', ml).attr('x2', W - mr).attr('y1', 0).attr('y2', 0);
    wt.forEach((t) => {
      xg.append('line').attr('x1', x(t.i)).attr('x2', x(t.i)).attr('y1', 0).attr('y2', 5);
      xg.append('text').attr('class', 'bx-tx').attr('x', x(t.i)).attr('y', 17).attr('text-anchor', 'start').text(t.label);
    });
    if (o.ref !== undefined) svg.append('line').attr('class', 'bx-ref').attr('x1', ml).attr('x2', W - mr).attr('y1', y(o.ref)).attr('y2', y(o.ref));
    const line = d3.line().x((d) => x(d.i)).y((d) => y(d.v));
    const paths = svg.append('g');
    series.forEach((s) => {
      paths.append('path').datum(s.vals).attr('class', 'bx-line').attr('d', line).style('stroke', s.color).attr('data-name', s.name);
    });
    const ends = spread(series.map((s) => ({ s, y: y(s.vals[s.vals.length - 1].v) })), 13, mt + 4, H - mb - 2);
    ends.forEach((e) => {
      svg.append('circle').attr('cx', x(e.s.vals[e.s.vals.length - 1].i)).attr('cy', y(e.s.vals[e.s.vals.length - 1].v)).attr('r', 3).style('fill', e.s.color);
      svg.append('text').attr('class', 'bx-tx bx-end').attr('x', W - mr + 8).attr('y', e.y).attr('dy', '0.35em').style('fill', e.s.color)
        .text(`${e.s.name} ${o.endFmt(e.s.vals[e.s.vals.length - 1].v)}`);
    });
    const rule = svg.append('line').attr('class', 'bx-rule').attr('y1', mt).attr('y2', H - mb).attr('visibility', 'hidden');
    const dots = svg.append('g');
    svg.append('rect').attr('class', 'bx-hit').attr('x', ml).attr('y', mt).attr('width', Math.max(1, W - mr - ml)).attr('height', H - mt - mb)
      .on('mousemove', (ev) => {
        const [px, py] = d3.pointer(ev);
        const i = Math.max(0, Math.min(n - 1, Math.round(x.invert(px))));
        rule.attr('x1', x(i)).attr('x2', x(i)).attr('visibility', 'visible');
        const pts = series.map((s) => ({ s, p: s.vals.find((v) => v.i === i) })).filter((d) => d.p);
        dots.selectAll('circle').data(pts).join('circle').attr('cx', x(i)).attr('cy', (d) => y(d.p.v)).attr('r', 3.5).style('fill', (d) => d.s.color);
        pts.sort((a, b) => (o.invert ? a.p.v - b.p.v : b.p.v - a.p.v));
        tip.show([labels.get(i), ...pts.map((d) => ({ c: d.s.color, t: `${d.s.name}  ${o.tipFmt(d.p.v)}` }))], px, py);
      })
      .on('mouseleave', () => { rule.attr('visibility', 'hidden'); dots.selectAll('circle').remove(); tip.hide(); });
  };

  // Grid of cells: rows, cols labels; cell(r, c) -> {v, t1, t2, faded, tip} | null
  const gridChart = (c, rowsL, colsL, cell, o) => {
    const { svg, W, H, tip } = c;
    const ml = measure(svg, rowsL) + 10;
    const mt = 22; const mb = 4;
    const cw = (W - ml - 2) / colsL.length;
    const full = measure(svg, colsL) + 8 <= cw;
    const colText = colsL.map((l) => (full ? l : (o.shortCol ? o.shortCol(l) : l)));
    const ch = (H - mt - mb) / rowsL.length;
    const pos = resolveColor(c.svg.node().parentNode, 'var(--color-ok)');
    const neg = resolveColor(c.svg.node().parentNode, 'var(--color-bad)');
    colText.forEach((l, j) => svg.append('text').attr('class', 'bx-tx').attr('x', ml + cw * j + cw / 2).attr('y', 14).attr('text-anchor', 'middle').text(l));
    rowsL.forEach((l, i) => svg.append('text').attr('class', 'bx-tx bx-lab').attr('x', ml - 8).attr('y', mt + ch * i + ch / 2).attr('dy', '0.35em').attr('text-anchor', 'end').text(l));
    const showT2 = ch >= 34 && cw >= 52;
    rowsL.forEach((rl, i) => colsL.forEach((cl, j) => {
      const d = cell(rl, cl, i, j);
      const gx = ml + cw * j; const gy = mt + ch * i;
      const g = svg.append('g').attr('class', d && d.faded ? 'bx-faded' : null);
      g.append('rect').attr('class', 'bx-cellbg').attr('x', gx + 1).attr('y', gy + 1).attr('width', Math.max(0, cw - 2)).attr('height', Math.max(0, ch - 2)).attr('rx', 3);
      if (!d) return;
      const op = o.opacity(d.v);
      g.append('rect').attr('x', gx + 1).attr('y', gy + 1).attr('width', Math.max(0, cw - 2)).attr('height', Math.max(0, ch - 2)).attr('rx', 3)
        .style('fill', o.fill ? o.fill(d.v) : (d.v >= (o.mid || 0) ? pos : neg)).style('fill-opacity', op);
      const t1 = g.append('text').attr('class', 'bx-tx bx-cell').attr('x', gx + cw / 2).attr('y', gy + ch / 2).attr('text-anchor', 'middle')
        .attr('dy', showT2 && d.t2 ? '-0.2em' : '0.35em').text(d.t1);
      if (t1.node().getComputedTextLength() > cw - 4) t1.remove();
      if (showT2 && d.t2) {
        const t2 = g.append('text').attr('class', 'bx-tx bx-cell2').attr('x', gx + cw / 2).attr('y', gy + ch / 2).attr('dy', '1.05em').attr('text-anchor', 'middle').text(d.t2);
        if (t2.node().getComputedTextLength() > cw - 4) t2.remove();
      }
      g.append('rect').attr('class', 'bx-hit').attr('x', gx).attr('y', gy).attr('width', cw).attr('height', ch)
        .on('mousemove', (ev) => { const [px, py] = d3.pointer(ev, c.svg.node().parentNode); tip.show(d.tip, px, py); })
        .on('mouseleave', () => tip.hide());
    }));
  };
  const divOpacity = (max) => (v) => 0.08 + 0.5 * Math.min(1, Math.abs(v) / max);

  // ---------- Summary charts ----------
  dash.draw('c-win', (el) => {
    const c = frame(el, ['players'], 300); if (!c) return;
    const d = c.data[0].slice().sort((a, b) => b.win_pct - a.win_pct);
    hbars(c, d.map((r) => ({
      label: r.player, v: r.win_pct, lo: r.win_lo, hi: r.win_hi, fill: color(r.player), text: `${fmt(r.win_pct, 'pct')}  ${r.record}`,
      tip: [r.player, `Won ${r.record} (${fmt(r.win_pct, 'pct')})`, `90% range ${fmt(r.win_lo, 'pct0')}–${fmt(r.win_hi, 'pct0')}`, `${r.P} matches`]
    })), { domain: [0, 1], ref: 0.5, axisFmt: FMT.pct0, base: 0 });
  });
  dash.draw('c-dpm', (el) => {
    const c = frame(el, ['players', 'estimates'], 300); if (!c) return;
    const est = byKey(c.data[1], 'player');
    const d = c.data[0].map((r) => ({ p: r.player, raw: r.dpm, adj: est.get(r.player) ? est.get(r.player).adj : null })).filter((r) => r.adj !== null)
      .sort((a, b) => b.adj - a.adj);
    const { svg, W, H, tip } = c;
    const ml = measure(svg, d.map((r) => r.p)) + 10;
    const texts = d.map((r) => `${fmt(r.raw, 's2')} → ${fmt(r.adj, 's2')}`);
    const mr = measure(svg, texts) + 10;
    const mt = 6; const mb = 24;
    const ext = d3.extent(d.flatMap((r) => [r.raw, r.adj, 0]));
    const x = d3.scaleLinear().domain([ext[0] - 0.4, ext[1] + 0.4]).range([ml, W - mr]).nice();
    const y = d3.scaleBand().domain(d.map((r) => r.p)).range([mt, H - mb]).padding(0.3);
    const ticks = Math.max(2, Math.floor((W - ml - mr) / 60));
    svg.append('g').attr('class', 'bx-grid').selectAll('line').data(x.ticks(ticks)).join('line').attr('x1', (v) => x(v)).attr('x2', (v) => x(v)).attr('y1', mt).attr('y2', H - mb);
    xAxis(svg.append('g').attr('transform', `translate(0,${H - mb})`), x, ticks, FMT.s0);
    svg.append('line').attr('class', 'bx-zero').attr('x1', x(0)).attr('x2', x(0)).attr('y1', mt).attr('y2', H - mb);
    d.forEach((r, i) => {
      const yy = y(r.p) + y.bandwidth() / 2;
      const g = svg.append('g');
      g.append('rect').attr('class', 'bx-hit').attr('x', 0).attr('y', y(r.p) - 3).attr('width', W).attr('height', y.bandwidth() + 6);
      g.append('line').attr('class', 'bx-link').attr('x1', x(r.raw)).attr('x2', x(r.adj)).attr('y1', yy).attr('y2', yy).style('stroke', color(r.p));
      g.append('circle').attr('class', 'bx-hollow').attr('cx', x(r.raw)).attr('cy', yy).attr('r', 5).style('stroke', color(r.p));
      g.append('circle').attr('cx', x(r.adj)).attr('cy', yy).attr('r', 5.5).style('fill', color(r.p));
      g.append('text').attr('class', 'bx-tx bx-lab').attr('x', ml - 8).attr('y', yy).attr('dy', '0.35em').attr('text-anchor', 'end').text(r.p);
      g.append('text').attr('class', 'bx-tx bx-val').attr('x', W - 2).attr('y', yy).attr('dy', '0.35em').attr('text-anchor', 'end').text(texts[i]);
      g.on('mousemove', (ev) => { const [px, py] = d3.pointer(ev, el); tip.show([r.p, `Raw ${fmt(r.raw, 's2')} per match`, `Adjusted ${fmt(r.adj, 's2')} per match`, `Draw effect ${fmt(r.raw - r.adj, 's2')}`], px, py); })
        .on('mouseleave', () => tip.hide());
    });
  });
  dash.draw('c-cum', (el) => {
    const c = frame(el, ['daily'], 340); if (!c) return;
    const d = c.data[0];
    const series = P.map((p) => ({ name: p, color: color(p), vals: d.filter((r) => r.player === p).sort((a, b) => a.day_index - b.day_index).map((r) => ({ i: r.day_index, v: r.cum_diff })) }))
      .filter((s) => s.vals.length);
    lineChart(c, d, series, { yFmt: FMT.s0, endFmt: FMT.s0, tipFmt: FMT.s0, ref: 0, yTickTexts: ['+400', '−400'] });
  });

  // ---------- Player charts ----------
  dash.draw('p-daily', (el) => {
    const c = frame(el, ['daily'], 240); if (!c) return;
    const p = el.dataset.player;
    const all = c.data[0];
    const d = all.filter((r) => r.player === p).sort((a, b) => a.day_index - b.day_index);
    const { svg, W, H, tip } = c;
    const ext = d3.max(all.filter((r) => r.played), (r) => Math.abs(r.diff)) || 1;
    const ml = measure(svg, [fmt(-ext, 's0'), fmt(ext, 's0')]) + 10; const mr = 6; const mt = 14; const mb = 24;
    const x = d3.scaleBand().domain(d.map((r) => r.day_index)).range([ml, W - mr]).padding(0.22);
    const y = d3.scaleLinear().domain([-ext, ext]).range([H - mb, mt]).nice();
    const yt = y.ticks(4);
    svg.append('g').attr('class', 'bx-grid').selectAll('line').data(yt).join('line').attr('x1', ml).attr('x2', W - mr).attr('y1', (v) => y(v)).attr('y2', (v) => y(v));
    svg.append('g').selectAll('text').data(yt).join('text').attr('class', 'bx-tx').attr('x', ml - 6).attr('y', (v) => y(v)).attr('dy', '0.35em').attr('text-anchor', 'end').text((v) => FMT.s0(v));
    svg.append('line').attr('class', 'bx-zero').attr('x1', ml).attr('x2', W - mr).attr('y1', y(0)).attr('y2', y(0));
    const xg = svg.append('g').attr('class', 'bx-axis');
    weekTicks(d).forEach((t) => xg.append('text').attr('class', 'bx-tx').attr('x', x(t.i)).attr('y', H - 6).attr('text-anchor', 'start').text(t.label));
    d.forEach((r) => {
      const g = svg.append('g');
      g.append('rect').attr('class', 'bx-hit').attr('x', x(r.day_index)).attr('y', mt).attr('width', x.bandwidth()).attr('height', H - mt - mb);
      if (!r.played) {
        g.append('line').attr('class', 'bx-absent').attr('x1', x(r.day_index) + x.bandwidth() / 2).attr('x2', x(r.day_index) + x.bandwidth() / 2).attr('y1', y(0) - 3).attr('y2', y(0) + 3);
      } else {
        g.append('rect').attr('x', x(r.day_index)).attr('y', Math.min(y(0), y(r.diff))).attr('width', x.bandwidth()).attr('height', Math.max(1, Math.abs(y(r.diff) - y(0))))
          .attr('rx', 2).style('fill', color(p)).style('fill-opacity', r.diff >= 0 ? 0.9 : 0.45);
        if (r.final) {
          g.append('circle').attr('cx', x(r.day_index) + x.bandwidth() / 2).attr('cy', mt - 6).attr('r', 3.5)
            .attr('class', r.title ? null : 'bx-hollow').style(r.title ? 'fill' : 'stroke', color(p));
        }
      }
      g.on('mousemove', (ev) => {
        const [px, py] = d3.pointer(ev, el);
        tip.show(r.played ? [r.day, `Won ${r.W}–${r.L}`, `Points difference ${fmt(r.diff, 's0')}`, `Adjusted ${fmt(r.adj, 's2')} per match`,
          `Qualifier place ${r.seed} of ${r.field}`, r.title ? 'Won the title' : (r.final ? 'Lost the final' : 'No final')] : [r.day, 'Did not play'], px, py);
      }).on('mouseleave', () => tip.hide());
    });
  });
  dash.draw('p-partners', (el) => {
    const c = frame(el, ['partners'], 250); if (!c) return;
    const p = el.dataset.player;
    const d = c.data[0].filter((r) => r.player === p).sort((a, b) => b.dpm - a.dpm);
    const ext = d3.max(c.data[0], (r) => Math.abs(r.dpm)) || 1;
    hbars(c, d.map((r) => ({
      label: r.partner, v: r.dpm, fill: color(r.partner), faded: r.P < REGULAR, text: `${r.record} · ${r.P}`,
      tip: [`${p} + ${r.partner}`, `Won ${r.record} (${fmt(r.win_pct, 'pct0')})`, `${fmt(r.dpm, 's2')} per match`, `Expected ${fmt(r.exp_dpm, 's2')}`,
        `${r.partner} without ${p}: ${fmt(r.partner_without_dpm, 's2')}`]
    })), { domain: [-ext, ext], zero: true, axisFmt: FMT.s0 });
  });
  dash.draw('p-opps', (el) => {
    const c = frame(el, ['opponents'], 250); if (!c) return;
    const p = el.dataset.player;
    const d = c.data[0].filter((r) => r.player === p).sort((a, b) => b.win_pct - a.win_pct);
    hbars(c, d.map((r) => ({
      label: r.opponent, v: r.win_pct, fill: color(r.opponent), text: `${fmt(r.win_pct, 'pct0')}  ${r.record}`,
      tip: [`${p} against ${r.opponent}`, `Won ${r.record}`, `${fmt(r.dpm, 's2')} per match`, `Expected wins ${fmt(r.exp_W, 'f1')}`]
    })), { domain: [0, 1], ref: 0.5, axisFmt: FMT.pct0, base: 0 });
  });

  // ---------- Weekly ----------
  dash.draw('c-weekheat', (el) => {
    const c = frame(el, ['weekly'], 330); if (!c) return;
    const d = c.data[0];
    const weeks = Array.from(new Set(d.map((r) => r.week))).sort((a, b) => a - b);
    const m = new Map(d.map((r) => [`${r.player}|${r.week}`, r]));
    const max = d3.max(d, (r) => Math.abs(r.adj)) || 1;
    gridChart(c, P, weeks.map((w) => `Week ${w}`), (p, wl, i, j) => {
      const r = m.get(`${p}|${weeks[j]}`);
      return r ? { v: r.adj, t1: fmt(r.adj, 's2'), t2: r.record, tip: [`${p}, Week ${r.week}`, `Won ${r.record} over ${r.days} days`, `Points difference ${fmt(r.diff, 's0')}`, `Adjusted ${fmt(r.adj, 's2')} per match`] } : null;
    }, { opacity: divOpacity(max), shortCol: (l) => l.replace('Week ', 'W') });
  });

  // ---------- Partnerships ----------
  dash.draw('c-pairmatrix', (el) => {
    const c = frame(el, ['pairs'], 380); if (!c) return;
    const d = c.data[0];
    const m = new Map(); d.forEach((r) => { m.set(`${r.a}|${r.b}`, r); m.set(`${r.b}|${r.a}`, r); });
    const max = d3.max(d, (r) => Math.abs(r.dpm)) || 1;
    gridChart(c, P, P, (a, b) => {
      const r = m.get(`${a}|${b}`);
      return r ? { v: r.dpm, t1: fmt(r.dpm, 's1'), t2: r.record, faded: r.P < REGULAR, tip: [r.key, `Won ${r.record} over ${r.P} matches`, `${fmt(r.dpm, 's2')} per match`, `Expected ${fmt(r.exp_dpm, 's2')}`] } : null;
    }, { opacity: divOpacity(max), shortCol: (l) => SHORT[l] || l });
  });
  dash.draw('c-pairvs', (el) => {
    const c = frame(el, ['pairs'], 520); if (!c) return;
    const d = c.data[0].slice().sort((a, b) => b.vs_exp - a.vs_exp);
    const ext = d3.max(d, (r) => Math.abs(r.vs_exp) + r.vs_exp_se) || 1;
    hbars(c, d.map((r) => ({
      label: r.key, v: r.vs_exp, lo: r.vs_exp - r.vs_exp_se, hi: r.vs_exp + r.vs_exp_se, faded: r.P < REGULAR,
      fill: r.vs_exp >= 0 ? 'var(--color-ok)' : 'var(--color-bad)', text: `${fmt(r.vs_exp, 's1')} · ${r.P}`,
      tip: [r.key, `Won ${r.record} over ${r.P} matches`, `Actual ${fmt(r.dpm, 's2')} per match`, `Expected ${fmt(r.exp_dpm, 's2')}`, `Difference ${fmt(r.vs_exp, 's2')} ± ${fmt(r.vs_exp_se, 'f1')}`]
    })), { domain: [-ext, ext], zero: true, axisFmt: FMT.s0 });
  });

  // ---------- Opponents ----------
  dash.draw('c-oppmatrix', (el) => {
    const c = frame(el, ['opponents'], 380); if (!c) return;
    const d = c.data[0];
    const m = new Map(d.map((r) => [`${r.player}|${r.opponent}`, r]));
    gridChart(c, P, P, (a, b) => {
      const r = m.get(`${a}|${b}`);
      return r ? { v: r.win_pct - 0.5, t1: fmt(r.win_pct, 'pct0'), t2: r.record, tip: [`${a} against ${b}`, `Won ${r.record}`, `${fmt(r.dpm, 's2')} per match`, `Expected wins ${fmt(r.exp_W, 'f1')}`] } : null;
    }, { opacity: divOpacity(0.4), shortCol: (l) => SHORT[l] || l });
  });

  // ---------- Pressure ----------
  dash.draw('c-clutch', (el) => {
    const c = frame(el, ['pressure'], 320); if (!c) return;
    const d = c.data[0].slice().sort((a, b) => b.clutch - a.clutch);
    const { svg, W, H, tip } = c;
    const ml = measure(svg, d.map((r) => r.player)) + 10;
    const texts = d.flatMap((r) => [fmt(r.c3_vs, 's1'), fmt(r.ko_vs, 's1')]);
    const mr = measure(svg, texts) + 10; const mt = 6; const mb = 24;
    const ext = d3.max(d, (r) => Math.max(Math.abs(r.c3_vs) + r.c3_sd, Math.abs(r.ko_vs) + r.ko_sd)) || 1;
    const x = d3.scaleLinear().domain([-ext, ext]).range([ml, W - mr]).nice();
    const y = d3.scaleBand().domain(d.map((r) => r.player)).range([mt, H - mb]).padding(0.2);
    const sub = d3.scaleBand().domain(['c3', 'ko']).range([0, y.bandwidth()]).padding(0.12);
    const ticks = Math.max(2, Math.floor((W - ml - mr) / 60));
    svg.append('g').attr('class', 'bx-grid').selectAll('line').data(x.ticks(ticks)).join('line').attr('x1', (v) => x(v)).attr('x2', (v) => x(v)).attr('y1', mt).attr('y2', H - mb);
    xAxis(svg.append('g').attr('transform', `translate(0,${H - mb})`), x, ticks, FMT.s0);
    const cols = { c3: dash.colors[0], ko: dash.colors[1] };
    d.forEach((r) => {
      const g = svg.append('g');
      g.append('rect').attr('class', 'bx-hit').attr('x', 0).attr('y', y(r.player)).attr('width', W).attr('height', y.bandwidth());
      [['c3', r.c3_vs, r.c3_sd], ['ko', r.ko_vs, r.ko_sd]].forEach(([k, v, sd]) => {
        const yy = y(r.player) + sub(k);
        g.append('rect').attr('x', Math.min(x(0), x(v))).attr('y', yy).attr('width', Math.max(1, Math.abs(x(v) - x(0)))).attr('height', sub.bandwidth()).attr('rx', 2).style('fill', cols[k]);
        g.append('line').attr('class', 'bx-whisk').attr('x1', x(v - sd)).attr('x2', x(v + sd)).attr('y1', yy + sub.bandwidth() / 2).attr('y2', yy + sub.bandwidth() / 2);
        g.append('text').attr('class', 'bx-tx bx-val').attr('x', W - 2).attr('y', yy + sub.bandwidth() / 2).attr('dy', '0.35em').attr('text-anchor', 'end').text(fmt(v, 's1'));
      });
      g.append('text').attr('class', 'bx-tx bx-lab').attr('x', ml - 8).attr('y', y(r.player) + y.bandwidth() / 2).attr('dy', '0.35em').attr('text-anchor', 'end').text(r.player);
      g.on('mousemove', (ev) => {
        const [px, py] = d3.pointer(ev, el);
        tip.show([r.player, { c: cols.c3, t: `Close: ${r.c3_record}, expected ${fmt(r.c3_exp, 'f1')} (${fmt(r.c3_vs, 's1')})` },
          { c: cols.ko, t: `Knockout: ${r.ko_record}, expected ${fmt(r.ko_exp, 'f1')} (${fmt(r.ko_vs, 's1')})` }], px, py);
      }).on('mouseleave', () => tip.hide());
    });
    svg.append('line').attr('class', 'bx-zero').attr('x1', x(0)).attr('x2', x(0)).attr('y1', mt).attr('y2', H - mb);
  });
  dash.draw('c-consist', (el) => {
    const c = frame(el, ['daily', 'estimates'], 320); if (!c) return;
    const d = c.data[0].filter((r) => r.played);
    const est = byKey(c.data[1], 'player');
    const { svg, W, H, tip } = c;
    const ml = measure(svg, P) + 10; const mr = 8; const mt = 6; const mb = 24;
    const ext = d3.max(d, (r) => Math.abs(r.adj)) || 1;
    const x = d3.scaleLinear().domain([-ext, ext]).range([ml, W - mr]).nice();
    const y = d3.scaleBand().domain(P).range([mt, H - mb]).padding(0.25);
    const ticks = Math.max(2, Math.floor((W - ml - mr) / 60));
    svg.append('g').attr('class', 'bx-grid').selectAll('line').data(x.ticks(ticks)).join('line').attr('x1', (v) => x(v)).attr('x2', (v) => x(v)).attr('y1', mt).attr('y2', H - mb);
    xAxis(svg.append('g').attr('transform', `translate(0,${H - mb})`), x, ticks, FMT.s0);
    svg.append('line').attr('class', 'bx-zero').attr('x1', x(0)).attr('x2', x(0)).attr('y1', mt).attr('y2', H - mb);
    P.forEach((p) => {
      const e = est.get(p); if (!e) return;
      const yy = y(p); const bh = y.bandwidth();
      svg.append('rect').attr('x', x(e.implied_mean - e.noise_sd)).attr('y', yy).attr('width', Math.max(1, x(e.implied_mean + e.noise_sd) - x(e.implied_mean - e.noise_sd)))
        .attr('height', bh).attr('rx', 3).style('fill', color(p)).style('fill-opacity', 0.14);
      svg.append('line').attr('x1', x(e.implied_mean)).attr('x2', x(e.implied_mean)).attr('y1', yy).attr('y2', yy + bh).style('stroke', color(p)).attr('class', 'bx-mean');
      svg.append('text').attr('class', 'bx-tx bx-lab').attr('x', ml - 8).attr('y', yy + bh / 2).attr('dy', '0.35em').attr('text-anchor', 'end').text(p);
      const pts = d.filter((r) => r.player === p);
      pts.forEach((r, k) => {
        const jitter = ((k * 7) % 5 - 2) * (bh / 10);
        svg.append('circle').attr('cx', x(r.adj)).attr('cy', yy + bh / 2 + jitter).attr('r', 3.2).style('fill', color(p)).style('fill-opacity', 0.85)
          .on('mousemove', (ev) => { const [px, py] = d3.pointer(ev, el); tip.show([`${p}, ${r.day}`, `Won ${r.W}–${r.L}, ${fmt(r.diff, 's0')}`, `Adjusted ${fmt(r.adj, 's2')} per match`], px, py); })
          .on('mouseleave', () => tip.hide());
      });
    });
  });

  // ---------- Models ----------
  dash.draw('c-forest', (el) => {
    const c = frame(el, ['estimates'], 330); if (!c) return;
    const d = c.data[0].slice().sort((a, b) => b.adj - a.adj);
    const { svg, W, H, tip } = c;
    const ml = measure(svg, d.map((r) => r.player)) + 10;
    const texts = d.map((r) => fmt(r.adj, 's2'));
    const mr = measure(svg, texts) + 10; const mt = 6; const mb = 24;
    const lo = d3.min(d, (r) => Math.min(r.adj_lo, r.recent_lo)); const hi = d3.max(d, (r) => Math.max(r.adj_hi, r.recent_hi));
    const x = d3.scaleLinear().domain([lo - 0.3, hi + 0.3]).range([ml, W - mr]).nice();
    const y = d3.scaleBand().domain(d.map((r) => r.player)).range([mt, H - mb]).padding(0.2);
    const ticks = Math.max(2, Math.floor((W - ml - mr) / 60));
    svg.append('g').attr('class', 'bx-grid').selectAll('line').data(x.ticks(ticks)).join('line').attr('x1', (v) => x(v)).attr('x2', (v) => x(v)).attr('y1', mt).attr('y2', H - mb);
    xAxis(svg.append('g').attr('transform', `translate(0,${H - mb})`), x, ticks, FMT.s0);
    svg.append('line').attr('class', 'bx-zero').attr('x1', x(0)).attr('x2', x(0)).attr('y1', mt).attr('y2', H - mb);
    d.forEach((r, i) => {
      const y1 = y(r.player) + y.bandwidth() * 0.32; const y2 = y(r.player) + y.bandwidth() * 0.78;
      const g = svg.append('g');
      g.append('rect').attr('class', 'bx-hit').attr('x', 0).attr('y', y(r.player)).attr('width', W).attr('height', y.bandwidth());
      g.append('line').attr('class', 'bx-ci').attr('x1', x(r.adj_lo)).attr('x2', x(r.adj_hi)).attr('y1', y1).attr('y2', y1).style('stroke', color(r.player));
      g.append('circle').attr('cx', x(r.adj)).attr('cy', y1).attr('r', 5).style('fill', color(r.player));
      g.append('line').attr('class', 'bx-ci bx-ci-thin').attr('x1', x(r.recent_lo)).attr('x2', x(r.recent_hi)).attr('y1', y2).attr('y2', y2).style('stroke', color(r.player));
      g.append('circle').attr('class', 'bx-hollow').attr('cx', x(r.recent_adj)).attr('cy', y2).attr('r', 4).style('stroke', color(r.player));
      g.append('text').attr('class', 'bx-tx bx-lab').attr('x', ml - 8).attr('y', y(r.player) + y.bandwidth() / 2).attr('dy', '0.35em').attr('text-anchor', 'end').text(r.player);
      g.append('text').attr('class', 'bx-tx bx-val').attr('x', W - 2).attr('y', y1).attr('dy', '0.35em').attr('text-anchor', 'end').text(texts[i]);
      g.on('mousemove', (ev) => {
        const [px, py] = d3.pointer(ev, el);
        tip.show([r.player, `Season ${fmt(r.adj, 's2')} (${fmt(r.adj_lo, 's2')} to ${fmt(r.adj_hi, 's2')})`, `Recent ${fmt(r.recent_adj, 's2')} (${fmt(r.recent_lo, 's2')} to ${fmt(r.recent_hi, 's2')})`, `Ranked first in ${fmt(r.p_first, 'pct0')} of resamples`], px, py);
      }).on('mouseleave', () => tip.hide());
    });
  });
  dash.draw('c-elo', (el) => {
    const c = frame(el, ['daily'], 360); if (!c) return;
    const d = c.data[0];
    const series = P.map((p) => ({ name: p, color: color(p), vals: d.filter((r) => r.player === p).sort((a, b) => a.day_index - b.day_index).map((r) => ({ i: r.day_index, v: r.elo })) }));
    lineChart(c, d, series, { yFmt: FMT.int, endFmt: FMT.int, tipFmt: FMT.int, ref: 1500, yTickTexts: ['1,800'] });
  });
  dash.draw('c-wbr', (el) => {
    const c = frame(el, ['daily'], 300); if (!c) return;
    const d = c.data[0];
    const m = new Map(d.map((r) => [`${r.player}|${r.day_index}`, r]));
    const idx = Array.from(new Set(d.map((r) => r.day_index))).sort((a, b) => a - b);
    const wt = new Map(weekTicks(d).map((t) => [t.i, t.label]));
    const base = resolveColor(el, dash.colors[0]);
    gridChart(c, P, idx.map((i) => wt.get(i) || ''), (p, cl, i, j) => {
      const r = m.get(`${p}|${idx[j]}`);
      return r && r.played && r.wb_rating !== null ? { v: r.wb_rating, t1: String(r.wb_rating), tip: [`${p}, ${r.day}`, `Workbook rating ${r.wb_rating}`] } : null;
    }, { opacity: (v) => 0.1 + 0.16 * v, fill: () => base, mid: 0 });
  });
  dash.draw('c-bump', (el) => {
    const c = frame(el, ['daily'], 300); if (!c) return;
    const d = c.data[0];
    const series = P.map((p) => ({ name: p, color: color(p), vals: d.filter((r) => r.player === p).sort((a, b) => a.day_index - b.day_index).map((r) => ({ i: r.day_index, v: r.cum_rank })) }));
    lineChart(c, d, series, { yFmt: (v) => `#${v}`, endFmt: (v) => `#${v}`, tipFmt: (v) => `#${v}`, yDomain: [1, 7], yTicks: [1, 2, 3, 4, 5, 6, 7], invert: true, yTickTexts: ['#7'] });
  });

  // ---------- player colours and header chips ----------
  const BYSLUG = { anto: 'Anto', jothi: 'Jothi Sai', john: 'John', pawan: 'Pawan', dinesh: 'Dinesh', pratap: 'Pratap', bhanu: 'Bhanu' };
  document.querySelectorAll('[data-player]').forEach((el) => {
    const p = P.includes(el.dataset.player) ? el.dataset.player : BYSLUG[el.dataset.player];
    if (p) el.style.setProperty('--pc', color(p));
  });
  document.querySelectorAll('[id^="sw-"]').forEach((el) => {
    const p = BYSLUG[el.id.slice(3)];
    if (p) el.style.setProperty('--pc', color(p));
  });
  dash.draw('hero-chips', (el) => {
    const pl = rowsOf('players'); const es = rowsOf('estimates');
    if (!pl || !es) { el.replaceChildren(); return; }
    const em = byKey(es, 'player');
    const rows = pl.filter((r) => em.has(r.player)).sort((a, b) => em.get(b.player).adj - em.get(a.player).adj);
    el.replaceChildren(...rows.map((r, i) => {
      const chip = document.createElement('div'); chip.className = 'bx-chip';
      chip.style.setProperty('--pc', color(r.player));
      const rank = document.createElement('span'); rank.className = 'bx-chip-rank'; rank.textContent = String(i + 1);
      const txt = document.createElement('span'); txt.className = 'bx-chip-txt';
      const name = document.createElement('span'); name.className = 'bx-chip-name'; name.textContent = r.player;
      const stat = document.createElement('span'); stat.className = 'bx-chip-stat'; stat.textContent = `${r.record} · ${fmt(em.get(r.player).adj, 's2')}`;
      txt.append(name, stat); chip.append(rank, txt);
      return chip;
    }));
  });

  // ---------- headline tile visuals ----------
  dash.draw('kpi-viz', (el) => {
    const kind = el.dataset.kind;
    const src = kind === 'weeks' ? 'daily' : 'facts';
    if (stateOf([src]) !== 'ok') { el.replaceChildren(); return; }
    el.replaceChildren();
    if (kind === 'ring') {
      const f = byKey(rowsOf('facts'), 'key').get(el.dataset.key);
      const v = f ? Math.max(0, Math.min(1, parseFloat(f.text) / 100)) : 0;
      const svg = d3.select(el).append('svg').attr('viewBox', '0 0 56 56').attr('width', 56).attr('height', 56);
      const arc = d3.arc().innerRadius(20).outerRadius(27).startAngle(0).cornerRadius(4);
      const g = svg.append('g').attr('transform', 'translate(28,28)');
      g.append('path').attr('class', 'v-off').attr('d', arc({ endAngle: 2 * Math.PI }));
      g.append('path').attr('class', 'v-on').attr('d', arc({ endAngle: 2 * Math.PI * v }));
      return;
    }
    const W = Math.floor(el.clientWidth);
    if (!W) return;
    const H = 30;
    const svg = d3.select(el).append('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`);
    if (kind === 'stages') {
      const facts = byKey(rowsOf('facts'), 'key');
      const parts = ['g.q', 'g.el', 'g.fi'].map((k) => +String((facts.get(k) || {}).text || '0').replace(/[^0-9.]/g, ''));
      const total = d3.sum(parts) || 1;
      let x = 0;
      parts.forEach((n, i) => {
        const w = W * n / total;
        svg.append('rect').attr('x', x).attr('y', 9).attr('width', Math.max(2, w - 4)).attr('height', 12).attr('rx', 6).attr('class', `v-on v-${i}`);
        x += w;
      });
    } else if (kind === 'weeks') {
      const per = d3.rollups(rowsOf('daily'), (v) => new Set(v.map((r) => r.day_index)).size, (r) => r.week).sort((a, b) => a[0] - b[0]);
      const max = d3.max(per, (q) => q[1]) || 1;
      const bw = W / per.length;
      per.forEach(([, n], i) => {
        const h = Math.max(3, (H - 2) * n / max);
        svg.append('rect').attr('x', i * bw + 2).attr('y', H - h).attr('width', Math.max(2, bw - 6)).attr('height', h).attr('rx', 4).attr('class', 'v-on');
      });
    }
  });

  // ---------- navigation ----------
  const openTab = (id, scroll) => {
    let found = false;
    document.querySelectorAll('[data-panel]').forEach((s) => { const on = s.dataset.panel === id; s.hidden = !on; if (on) found = true; });
    if (!found) return false;
    document.querySelectorAll('.bx-tab').forEach((b) => b.setAttribute('aria-selected', b.dataset.tab === id ? 'true' : 'false'));
    if (scroll) document.querySelectorAll('.bx-tabs').forEach((n) => { if (n.getBoundingClientRect().top < 0) n.scrollIntoView({ block: 'start' }); });
    dash.setLink(id);
    return true;
  };
  const pickPlayer = (slug) => {
    document.querySelectorAll('.bx-pr').forEach((a) => { a.hidden = a.dataset.player !== slug; });
    document.querySelectorAll('.bx-pick-b').forEach((b) => b.setAttribute('aria-pressed', b.dataset.player === slug ? 'true' : 'false'));
  };
  const goTo = (id) => {
    const target = document.getElementById(id);
    if (!target) return;
    const panel = target.closest('[data-panel]');
    if (panel) openTab(panel.dataset.panel, false);
    const art = target.closest('.bx-pr');
    if (art) pickPlayer(art.dataset.player);
    requestAnimationFrame(() => { target.scrollIntoView({ block: 'start' }); dash.setLink(id); });
  };
  document.addEventListener('click', (ev) => {
    const tab = ev.target.closest('.bx-tab');
    if (tab) { openTab(tab.dataset.tab, true); return; }
    const pick = ev.target.closest('.bx-pick-b');
    if (pick) {
      pickPlayer(pick.dataset.player); dash.setLink(`p-${pick.dataset.player}`);
      const art = document.getElementById(`p-${pick.dataset.player}`);
      if (art && art.getBoundingClientRect().top > window.innerHeight * 0.55) art.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }
    const pn = ev.target.closest('.bx-pn-b');
    if (pn) {
      pickPlayer(pn.dataset.goto); dash.setLink(`p-${pn.dataset.goto}`);
      const sec = document.getElementById('players');
      if (sec) sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }
    const jump = ev.target.closest('.bx-jump');
    if (jump) { ev.preventDefault(); goTo(jump.getAttribute('href').slice(1)); return; }
    const sortb = ev.target.closest('.bx-sort');
    if (sortb) {
      const th = sortb.closest('th');
      const cur = th.getAttribute('aria-sort');
      const next = cur === 'descending' ? 'ascending' : (cur === 'ascending' ? 'descending' : (th.classList.contains('num') ? 'descending' : 'ascending'));
      th.closest('tr').querySelectorAll('th').forEach((x) => x.setAttribute('aria-sort', 'none'));
      th.setAttribute('aria-sort', next);
      dash.draw('t');
    }
  });
  let started = false;
  dash.onData(() => {
    if (started) return;
    started = true;
    const h = location.hash.slice(1);
    if (h && !openTab(h, false)) goTo(h);
  });
})();

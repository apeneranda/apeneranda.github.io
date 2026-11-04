// Recherche dans le site, entièrement dans le navigateur (aucun service extérieur).
// L'index (search.json) est produit par Hugo à chaque publication et chargé à la première ouverture.
(function () {
  var dlg = document.getElementById('search-dialog');
  var btn = document.getElementById('search-open');
  if (!dlg || !btn) return;
  var input = dlg.querySelector('input');
  var list = dlg.querySelector('.search-results');
  var status = dlg.querySelector('.search-status');
  var L = dlg.dataset;
  var index = null, loading = null, timer = null;

  // Minuscules sans accents, avec la correspondance vers les positions du texte d'origine
  function fold(s) {
    var out = '', map = [];
    for (var i = 0; i < s.length; i++) {
      var c = s[i].normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
      for (var j = 0; j < c.length; j++) { out += c[j]; map.push(i); }
    }
    return { s: out, map: map };
  }

  function load() {
    if (!loading) {
      loading = fetch(L.index).then(function (r) { return r.json(); }).then(function (data) {
        index = data.map(function (e) {
          e.ft = fold(e.t); e.fx = fold(e.x);
          return e;
        });
      }).catch(function () { status.textContent = L.error; });
    }
    return loading;
  }

  function open() {
    dlg.showModal();
    input.focus();
    input.select();
    load().then(run);
  }

  function terms(q) {
    return fold(q).s.split(/[\s,;:.'’"«»()\[\]-]+/).filter(function (w) { return w.length > 0; });
  }

  // Texte avec les termes surlignés (<mark>), construit sans innerHTML
  function highlight(el, text, folded, words, start, end) {
    var marks = [];
    words.forEach(function (w) {
      var i = folded.s.indexOf(w);
      while (i !== -1) {
        var a = folded.map[i], b = folded.map[i + w.length - 1] + 1;
        if (a >= start && b <= end) marks.push([a, b]);
        i = folded.s.indexOf(w, i + w.length);
      }
    });
    marks.sort(function (x, y) { return x[0] - y[0]; });
    var pos = start;
    marks.forEach(function (m) {
      if (m[0] < pos) return;
      el.appendChild(document.createTextNode(text.slice(pos, m[0])));
      var mk = document.createElement('mark');
      mk.textContent = text.slice(m[0], m[1]);
      el.appendChild(mk);
      pos = m[1];
    });
    el.appendChild(document.createTextNode(text.slice(pos, end)));
  }

  function snippet(e, words) {
    var first = -1;
    words.forEach(function (w) {
      var i = e.fx.s.indexOf(w);
      if (i !== -1 && (first === -1 || i < first)) first = i;
    });
    var at = first === -1 ? 0 : e.fx.map[first];
    var start = Math.max(0, at - 60), end = Math.min(e.x.length, start + 200);
    if (start > 0) { var sp = e.x.indexOf(' ', start); if (sp !== -1 && sp < at) start = sp + 1; }
    if (end < e.x.length) { var sp2 = e.x.lastIndexOf(' ', end); if (sp2 > at) end = sp2; }
    return { start: start, end: end };
  }

  function run() {
    if (!index) return;
    var q = input.value.trim();
    list.textContent = '';
    if (!q) { status.textContent = L.hint; return; }
    var words = terms(q);
    var hits = [];
    index.forEach(function (e) {
      var score = 0;
      for (var i = 0; i < words.length; i++) {
        var inT = e.ft.s.indexOf(words[i]) !== -1, inX = e.fx.s.indexOf(words[i]) !== -1;
        if (!inT && !inX) return;
        score += inT ? 10 : 1;
      }
      if (e.k === 'page') score += 0.5;
      hits.push({ e: e, score: score });
    });
    hits.sort(function (a, b) { return b.score - a.score || b.e.y - a.e.y; });
    status.textContent = hits.length === 0 ? L.none
      : hits.length === 1 ? L.single : L.many.replace('%d', hits.length);
    hits.slice(0, 30).forEach(function (h) {
      var e = h.e;
      var li = document.createElement('li');
      var a = document.createElement('a');
      a.href = e.u;
      var head = document.createElement('span');
      head.className = 'search-title';
      highlight(head, e.t, e.ft, words, 0, e.t.length);
      var badge = document.createElement('span');
      badge.className = 'search-kind';
      badge.textContent = e.k === 'pub' ? L.pub + (e.y ? ' · ' + e.y : '') : L.page;
      var p = document.createElement('span');
      p.className = 'search-snippet';
      var sn = snippet(e, words);
      if (sn.start > 0) p.appendChild(document.createTextNode('… '));
      highlight(p, e.x, e.fx, words, sn.start, sn.end);
      if (sn.end < e.x.length) p.appendChild(document.createTextNode(' …'));
      a.appendChild(badge);
      a.appendChild(head);
      a.appendChild(p);
      li.appendChild(a);
      list.appendChild(li);
    });
  }

  btn.addEventListener('click', open);
  input.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(run, 80); });
  input.addEventListener('keydown', function (ev) {
    if (ev.key === 'Enter') {
      var first = list.querySelector('a');
      if (first) { ev.preventDefault(); window.location.href = first.href; }
    } else if (ev.key === 'ArrowDown') {
      var f = list.querySelector('a');
      if (f) { ev.preventDefault(); f.focus(); }
    }
  });
  list.addEventListener('keydown', function (ev) {
    var links = Array.prototype.slice.call(list.querySelectorAll('a'));
    var i = links.indexOf(document.activeElement);
    if (i === -1) return;
    if (ev.key === 'ArrowDown' && i < links.length - 1) { ev.preventDefault(); links[i + 1].focus(); }
    if (ev.key === 'ArrowUp') { ev.preventDefault(); (i > 0 ? links[i - 1] : input).focus(); }
  });
  dlg.querySelector('.search-close').addEventListener('click', function () { dlg.close(); });
  dlg.addEventListener('click', function (ev) { if (ev.target === dlg) dlg.close(); });
  // Raccourci clavier « / » (hors champ de saisie)
  document.addEventListener('keydown', function (ev) {
    var tag = (ev.target.tagName || '').toLowerCase();
    if (ev.key === '/' && !dlg.open && tag !== 'input' && tag !== 'textarea') { ev.preventDefault(); open(); }
  });
})();

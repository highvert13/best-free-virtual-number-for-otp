/* OTP Number Lab — ranking.js: filters and sorting for the ranking table.
   Progressive enhancement: all rows are in the HTML; without JS the table is fully readable. */
(function () {
  'use strict';

  var table = document.getElementById('ranking-table');
  var form = document.getElementById('ranking-filters');
  if (!table || !form) return;

  var tbody = table.tBodies[0];
  var rows = Array.prototype.slice.call(tbody.rows);
  var countEl = document.getElementById('ranking-count');
  var emptyEl = document.getElementById('ranking-empty');
  var headers = Array.prototype.slice.call(table.querySelectorAll('th[data-sort]'));

  var state = { platform: 'all', country: 'all', type: 'all', sort: 'rank', dir: 'asc' };

  form.hidden = false;

  /* Restore state from hash, e.g. #ranking?platform=telegram&country=uk */
  function readHash() {
    var h = window.location.hash;
    var i = h.indexOf('?');
    if (h.indexOf('#ranking') !== 0 || i === -1) return;
    h.slice(i + 1).split('&').forEach(function (pair) {
      var kv = pair.split('=');
      if (kv[0] in state && kv[1]) state[kv[0]] = decodeURIComponent(kv[1]);
    });
    ['platform', 'country', 'type'].forEach(function (k) {
      if (form.elements[k]) form.elements[k].value = state[k];
    });
  }

  function writeHash() {
    var parts = [];
    ['platform', 'country', 'type'].forEach(function (k) {
      if (state[k] !== 'all') parts.push(k + '=' + encodeURIComponent(state[k]));
    });
    var hash = '#ranking' + (parts.length ? '?' + parts.join('&') : '');
    if (window.location.hash !== hash) history.replaceState(null, '', hash);
  }

  function matches(row) {
    if (state.type !== 'all' && row.dataset.type !== state.type) return false;
    if (state.country !== 'all' && row.dataset.countries.split(' ').indexOf(state.country) === -1) return false;
    if (state.platform !== 'all' && row.dataset[state.platform] === 'fails') return false;
    return true;
  }

  function sortValue(row, key) {
    if (key === 'tested') return Date.parse(row.dataset.tested) || 0;
    return parseFloat(row.dataset[key]) || 0;
  }

  function render() {
    var shown = 0;
    var sorted = rows.slice().sort(function (a, b) {
      var d = sortValue(a, state.sort) - sortValue(b, state.sort);
      if (d === 0) d = sortValue(a, 'rank') - sortValue(b, 'rank');
      return state.dir === 'asc' ? d : -d;
    });
    sorted.forEach(function (row) {
      var ok = matches(row);
      row.hidden = !ok;
      if (ok) shown++;
      tbody.appendChild(row);
    });
    countEl.textContent = String(shown);
    emptyEl.hidden = shown !== 0;

    headers.forEach(function (th) {
      if (th.dataset.sort === state.sort) th.setAttribute('aria-sort', state.dir === 'asc' ? 'ascending' : 'descending');
      else th.removeAttribute('aria-sort');
    });
  }

  form.addEventListener('change', function (e) {
    var name = e.target.name;
    if (!(name in state)) return;
    state[name] = e.target.value;
    render();
    writeHash();
  });
  form.addEventListener('submit', function (e) { e.preventDefault(); });

  headers.forEach(function (th) {
    var btn = th.querySelector('button');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var key = th.dataset.sort;
      if (state.sort === key) {
        state.dir = state.dir === 'asc' ? 'desc' : 'asc';
      } else {
        state.sort = key;
        /* rank ascending by default; numbers and dates descending (best/newest first) */
        state.dir = key === 'rank' ? 'asc' : 'desc';
      }
      render();
    });
  });

  /* Number finder: sets the same hash the filters use, e.g. #ranking?platform=whatsapp&country=uk */
  var finder = document.getElementById('finder-form');
  if (finder) {
    finder.addEventListener('submit', function (e) {
      e.preventDefault();
      var parts = [];
      ['platform', 'country'].forEach(function (k) {
        var v = finder.elements[k].value;
        if (v !== 'all') parts.push(k + '=' + encodeURIComponent(v));
      });
      var hash = '#ranking' + (parts.length ? '?' + parts.join('&') : '');
      if (window.location.hash === hash) applyHash();
      else window.location.hash = hash;
    });
  }

  function applyHash() {
    state.platform = 'all'; state.country = 'all'; state.type = 'all';
    ['platform', 'country', 'type'].forEach(function (k) { if (form.elements[k]) form.elements[k].value = 'all'; });
    readHash();
    render();
    var section = document.getElementById('ranking');
    if (section && window.location.hash.indexOf('#ranking') === 0) section.scrollIntoView();
  }
  window.addEventListener('hashchange', applyHash);

  readHash();
  render();
})();

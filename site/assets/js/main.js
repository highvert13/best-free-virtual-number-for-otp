/* OTP Number Lab — main.js: navigation, dropdowns, outbound click tracking */
(function () {
  'use strict';

  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  var dropdowns = Array.prototype.slice.call(document.querySelectorAll('.has-dropdown'));

  /* Mobile menu */
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      nav.classList.toggle('is-open', !open);
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a') && nav.classList.contains('is-open')) {
        toggle.setAttribute('aria-expanded', 'false');
        nav.classList.remove('is-open');
      }
    });
  }

  /* Dropdowns */
  function closeAll(except) {
    dropdowns.forEach(function (dd) {
      if (dd === except) return;
      dd.classList.remove('is-open');
      var btn = dd.querySelector('.dropdown-toggle');
      if (btn) btn.setAttribute('aria-expanded', 'false');
    });
  }

  dropdowns.forEach(function (dd) {
    var btn = dd.querySelector('.dropdown-toggle');
    if (!btn) return;
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = dd.classList.contains('is-open');
      closeAll(dd);
      dd.classList.toggle('is-open', !open);
      btn.setAttribute('aria-expanded', String(!open));
    });
  });

  document.addEventListener('click', function (e) {
    if (!e.target.closest('.has-dropdown')) closeAll();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var openDd = dropdowns.filter(function (dd) { return dd.classList.contains('is-open'); })[0];
    closeAll();
    if (openDd) openDd.querySelector('.dropdown-toggle').focus();
    if (nav && nav.classList.contains('is-open')) {
      nav.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.focus();
    }
  });

  /* Analytics events (sent only if the visitor accepted analytics) */
  function track(name, params) {
    if (typeof window.gtag === 'function') window.gtag('event', name, params || {});
  }

  /* Outbound links */
  document.addEventListener('click', function (e) {
    var link = e.target.closest('a[href^="http"]');
    if (!link || link.host === window.location.host) return;
    track('outbound_click', { link_url: link.href, link_text: link.textContent.trim().slice(0, 100) });
  });

  /* Number finder (home page) */
  var finderForm = document.getElementById('finder-form');
  if (finderForm) {
    finderForm.addEventListener('submit', function () {
      track('finder_submit', { platform: finderForm.elements.platform.value, country: finderForm.elements.country.value });
    });
  }

  /* Cookie consent: analytics loads only after "Accept" (UK GDPR) */
  var GA_ID = 'G-CN16Q36XC1'; // Google Analytics 4 measurement ID
  var CONSENT_KEY = 'otp-consent';
  var banner = document.getElementById('cookie-banner');

  function readConsent() { try { return localStorage.getItem(CONSENT_KEY); } catch (err) { return null; } }
  function saveConsent(v) { try { localStorage.setItem(CONSENT_KEY, v); } catch (err) { /* storage blocked */ } }

  function loadAnalytics() {
    if (!GA_ID || window.gtag) return;
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', GA_ID);
  }

  var consent = readConsent();
  if (consent === 'accepted') loadAnalytics();
  else if (!consent && banner) banner.hidden = false;

  /* "Cookie settings" buttons (Privacy Policy): forget the choice and ask again */
  Array.prototype.forEach.call(document.querySelectorAll('[data-cookie-settings]'), function (btn) {
    btn.addEventListener('click', function () {
      try { localStorage.removeItem(CONSENT_KEY); } catch (err) { /* storage blocked */ }
      if (banner) {
        banner.hidden = false;
        var first = banner.querySelector('button');
        if (first) first.focus();
      }
    });
  });

  if (banner) {
    banner.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-consent]');
      if (!btn) return;
      saveConsent(btn.dataset.consent);
      banner.hidden = true;
      if (btn.dataset.consent === 'accepted') loadAnalytics();
      /* Withdrawing consent after analytics loaded: reload so the scripts are gone */
      else if (window.gtag && GA_ID) window.location.reload();
    });
  }

  /* Email addresses assembled in JS (simple scraping protection) */
  Array.prototype.forEach.call(document.querySelectorAll('.js-email[data-user][data-domain]'), function (el) {
    var addr = el.dataset.user + '@' + el.dataset.domain;
    var a = document.createElement('a');
    a.href = 'mailto:' + addr;
    a.textContent = addr;
    el.textContent = '';
    el.appendChild(a);
    /* Spans without data-* (e.g. in the success message) reuse the first address */
    Array.prototype.forEach.call(document.querySelectorAll('.js-email:not([data-user])'), function (other) {
      if (other.querySelector('a')) return;
      var b = a.cloneNode(true);
      other.textContent = '';
      other.appendChild(b);
    });
  });

  /* Table of contents: highlight the section in view */
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll('.toc a[href^="#"]'));
  if (tocLinks.length && 'IntersectionObserver' in window) {
    var byId = {};
    tocLinks.forEach(function (a) { byId[a.getAttribute('href').slice(1)] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        tocLinks.forEach(function (a) { a.classList.remove('is-active'); a.removeAttribute('aria-current'); });
        var link = byId[entry.target.id];
        if (link) { link.classList.add('is-active'); link.setAttribute('aria-current', 'true'); }
      });
    }, { rootMargin: '-90px 0px -70% 0px' });
    Object.keys(byId).forEach(function (id) {
      var target = document.getElementById(id);
      if (target) io.observe(target);
    });
  }

  /* Blog hub: filter cards by category (all cards stay in the HTML without JS) */
  var chipGroup = document.querySelector('.chips');
  if (chipGroup) {
    chipGroup.hidden = false;
    var chips = Array.prototype.slice.call(chipGroup.querySelectorAll('.chip'));
    var cards = Array.prototype.slice.call(document.querySelectorAll('.blog-card[data-category]'));
    chipGroup.addEventListener('click', function (e) {
      var chip = e.target.closest('.chip');
      if (!chip) return;
      var f = chip.dataset.filter;
      chips.forEach(function (c) { var on = c === chip; c.classList.toggle('is-active', on); c.setAttribute('aria-pressed', String(on)); });
      cards.forEach(function (card) { card.hidden = f !== 'all' && card.dataset.category !== f; });
    });
  }

  /* Header shadow on scroll */
  if (header) {
    var onScroll = function () { header.style.boxShadow = window.scrollY > 4 ? '0 1px 12px rgba(0,0,0,.06)' : 'none'; };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }
})();

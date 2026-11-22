/* OTP Number Lab — contact.js: email protection, form validation and submission */
(function () {
  'use strict';

  /* Contact email (the visible links are built by main.js) */
  var src = document.querySelector('.js-email[data-user][data-domain]');
  var email = src ? src.dataset.user + '@' + src.dataset.domain : '';

  /* ---------- Form ---------- */
  var form = document.getElementById('contact-form');
  if (!form) return;

  var statusEl = document.getElementById('cf-status');
  var successEl = document.getElementById('cf-success');
  var submitBtn = form.querySelector('button[type="submit"]');
  var message = form.elements.message;
  var countEl = document.getElementById('cf-count');
  var startedAt = Date.now();
  var MIN_FILL_MS = 3000;
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  var rules = {
    name: function (v) {
      if (!v) return 'Please enter your name.';
      if (v.length < 2) return 'Name must be at least 2 characters.';
      return '';
    },
    email: function (v) {
      if (!v) return 'Please enter your email.';
      if (!EMAIL_RE.test(v)) return 'Please enter a valid email, for example name@example.com.';
      return '';
    },
    topic: function (v) { return v ? '' : 'Please choose a topic.'; },
    message: function (v) {
      if (!v) return 'Please write a message.';
      if (v.length < 20) return 'Please write at least 20 characters (' + v.length + ' so far).';
      return '';
    },
    consent: function (v, el) { return el.checked ? '' : 'Please agree to the Privacy Policy so we can reply.'; }
  };

  function fieldValue(name) {
    var el = form.elements[name];
    return el.type === 'checkbox' ? el.checked : el.value.trim();
  }

  function setError(name, msg) {
    var el = form.elements[name];
    var err = document.getElementById(el.id + '-error');
    if (msg) el.setAttribute('aria-invalid', 'true');
    else el.removeAttribute('aria-invalid');
    if (err) err.textContent = msg;
  }

  function validateField(name) {
    var el = form.elements[name];
    var msg = rules[name](fieldValue(name), el);
    setError(name, msg);
    return !msg;
  }

  function validateAll() {
    var firstInvalid = null;
    Object.keys(rules).forEach(function (name) {
      if (!validateField(name) && !firstInvalid) firstInvalid = form.elements[name];
    });
    if (firstInvalid) firstInvalid.focus();
    return !firstInvalid;
  }

  /* Validate on blur; clear errors as the user fixes them */
  Object.keys(rules).forEach(function (name) {
    var el = form.elements[name];
    el.addEventListener('blur', function () { if (el.value || el.type === 'checkbox') validateField(name); });
    el.addEventListener(el.tagName === 'SELECT' || el.type === 'checkbox' ? 'change' : 'input', function () {
      if (el.getAttribute('aria-invalid') === 'true') validateField(name);
    });
  });

  /* Character counter */
  function updateCount() { countEl.textContent = String(message.value.length); }
  message.addEventListener('input', updateCount);
  updateCount();

  function setStatus(text, isError) {
    statusEl.textContent = text;
    statusEl.classList.toggle('is-error', !!isError);
  }

  function showSuccess() {
    form.hidden = true;
    successEl.hidden = false;
    successEl.focus();
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    setStatus('');
    if (!validateAll()) {
      setStatus('Please fix the highlighted fields.', true);
      return;
    }

    /* Bots: honeypot filled or form submitted too fast -> pretend success, send nothing */
    if (form.elements.website.value || Date.now() - startedAt < MIN_FILL_MS) {
      showSuccess();
      return;
    }

    var data = {
      name: fieldValue('name'),
      email: fieldValue('email'),
      topic: form.elements.topic.options[form.elements.topic.selectedIndex].text,
      message: fieldValue('message')
    };
    var endpoint = form.dataset.endpoint;

    /* No endpoint configured yet: hand the message to the visitor's email app */
    if (!endpoint) {
      if (!email) { setStatus('The contact form is not configured yet. Please try again later.', true); return; }
      var body = data.message + '\n\n— ' + data.name + ' (' + data.email + ')';
      window.location.href = 'mailto:' + email + '?subject=' + encodeURIComponent('[' + data.topic + '] Message from ' + data.name) + '&body=' + encodeURIComponent(body);
      setStatus('Your email app should open with the message ready to send.');
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Sending…';

    fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify(data)
    }).then(function (res) {
      if (!res.ok) throw new Error('HTTP ' + res.status);
      showSuccess();
      if (typeof window.gtag === 'function') window.gtag('event', 'contact_form_submit', { topic: data.topic });
    }).catch(function () {
      setStatus('Sorry, the message could not be sent. Please email us at ' + (email || 'our contact address') + '.', true);
    }).then(function () {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Send message';
    });
  });
})();

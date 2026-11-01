(function () {
  var desktop = window.matchMedia('(min-width: 1180px)');

  // Desktop dropdowns: click/keyboard toggle (hover is handled in CSS)
  var items = document.querySelectorAll('.nav-item.has-dd');
  function closeAll(except) {
    items.forEach(function (it) {
      if (it !== except) {
        it.classList.remove('open');
        var b = it.querySelector('.nav-link');
        if (b) b.setAttribute('aria-expanded', 'false');
      }
    });
  }
  items.forEach(function (it) {
    var btn = it.querySelector('.nav-link');
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      var open = !it.classList.contains('open');
      closeAll(it);
      it.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', String(open));
    });
    it.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { closeAll(); btn.focus(); }
    });
  });
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.nav-item.has-dd')) closeAll();
  });

  // Mobile menu
  var toggle = document.querySelector('.menu-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var open = document.body.classList.toggle('menu-open');
      toggle.setAttribute('aria-expanded', String(open));
    });
    desktop.addEventListener('change', function (m) {
      if (m.matches) { document.body.classList.remove('menu-open'); toggle.setAttribute('aria-expanded', 'false'); }
    });
  }
  document.querySelectorAll('.m-toggle').forEach(function (b) {
    b.addEventListener('click', function () {
      b.setAttribute('aria-expanded', String(b.getAttribute('aria-expanded') !== 'true'));
    });
  });

  // Reveal on scroll
  var els = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    els.forEach(function (el) { io.observe(el); });
  } else {
    els.forEach(function (el) { el.classList.add('in'); });
  }

  // Forms: no backend yet. data-redirect forms go to their thank-you page;
  // others show an inline success message. Swap for Formspree / WP / CRM endpoint at launch.
  document.querySelectorAll('form[data-demo]').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      if (f.getAttribute('action')) return; // real endpoint configured
      e.preventDefault();
      if (!f.reportValidity()) return;
      var to = f.getAttribute('data-redirect');
      if (to) { window.location.href = to; return; }
      var ok = f.parentElement.querySelector('.form-success');
      if (ok) { f.style.display = 'none'; ok.classList.add('show'); }
    });
  });

  // Field validation: email and phone (the server checks again)
  var EMAIL_RE = /^[A-Za-z0-9._%+'-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$/;
  function phoneDigits(v) {
    if (/[^0-9\s().+-]/.test(v)) return null;           // letters or other symbols
    var d = v.replace(/\D/g, '');
    if (d.length === 11 && d.charAt(0) === '1') d = d.slice(1);
    return /^[2-9]\d{2}[2-9]\d{6}$/.test(d) ? d : null;  // North American 10-digit number
  }
  var CHECKS = {
    email: function (input) {
      var v = input.value.trim();
      if (!v) return 'Please enter your email address.';
      if (!EMAIL_RE.test(v) || v.indexOf('..') !== -1) return 'Please enter a valid email address, e.g. name@example.com.';
      return '';
    },
    phone: function (input) {
      var v = input.value.trim();
      if (!v) return 'Please enter your phone number.';
      return phoneDigits(v) ? '' : 'Please enter a valid 10-digit phone number, e.g. 604-555-1234.';
    }
  };
  function checkField(input, show) {
    var msg = CHECKS[input.getAttribute('data-validate')](input);
    input.setCustomValidity(msg);
    var err = document.getElementById(input.getAttribute('aria-describedby'));
    if (show) {
      input.setAttribute('aria-invalid', msg ? 'true' : 'false');
      if (err) err.textContent = msg;
    } else if (!msg) {
      input.removeAttribute('aria-invalid');
      if (err) err.textContent = '';
    }
    return !msg;
  }
  document.querySelectorAll('[data-validate]').forEach(function (input) {
    input.addEventListener('blur', function () {
      if (input.value.trim() === '') return;
      if (checkField(input, true) && input.getAttribute('data-validate') === 'phone') {
        var d = phoneDigits(input.value.trim());
        input.value = d.slice(0, 3) + '-' + d.slice(3, 6) + '-' + d.slice(6);   // tidy to 604-555-1234
      }
    });
    input.addEventListener('input', function () { checkField(input, input.getAttribute('aria-invalid') === 'true'); });
    checkField(input, false);
  });

  // Phone boxes accept only digits, spaces and ( ) + - .
  document.querySelectorAll('[data-validate="phone"]').forEach(function (input) {
    // Filter typed/pasted text BEFORE it goes in, so the length limit counts only real phone characters
    input.addEventListener('beforeinput', function (e) {
      if (!e.data || !/^insert/.test(e.inputType)) return;
      var clean = e.data.replace(/[^0-9\s().+-]/g, '');
      if (clean === e.data) return;
      e.preventDefault();
      var room = input.maxLength - (input.value.length - (input.selectionEnd - input.selectionStart));
      input.setRangeText(clean.slice(0, Math.max(0, room)), input.selectionStart, input.selectionEnd, 'end');
      input.dispatchEvent(new Event('input', { bubbles: true }));
    });
    input.addEventListener('paste', function (e) {
      var text = (e.clipboardData || window.clipboardData).getData('text') || '';
      var clean = text.replace(/[^0-9\s().+-]/g, '').trim();
      if (clean === text) return;
      e.preventDefault();
      var room = input.maxLength - (input.value.length - (input.selectionEnd - input.selectionStart));
      input.setRangeText(clean.slice(0, Math.max(0, room)), input.selectionStart, input.selectionEnd, 'end');
      input.dispatchEvent(new Event('input', { bubbles: true }));
    });
    input.addEventListener('input', function () {
      var cleaned = input.value.replace(/[^0-9\s().+-]/g, '');
      if (cleaned !== input.value) input.value = cleaned;
    });
  });

  // Character counter under long text boxes (e.g. "120 / 2000")
  document.querySelectorAll('textarea[maxlength]').forEach(function (ta) {
    var max = +ta.getAttribute('maxlength'), c = document.createElement('p');
    c.className = 'char-count'; c.setAttribute('aria-live', 'polite');
    ta.after(c);
    function upd() { c.textContent = ta.value.length + ' / ' + max; c.classList.toggle('near', ta.value.length > max * 0.9); }
    ta.addEventListener('input', upd); upd();
  });

  // ActiveCampaign guide form (loaded by their script): add max lengths to its fields once it appears
  var ac = document.getElementById('get-guide');
  if (ac && 'MutationObserver' in window) {
    var AC_LIMITS = { firstname: 50, lastname: 50, email: 254 };
    var applyAc = function () {
      Object.keys(AC_LIMITS).forEach(function (n) {
        var el = ac.querySelector('input[name="' + n + '"]');
        if (el && !el.hasAttribute('maxlength')) el.setAttribute('maxlength', AC_LIMITS[n]);
      });
    };
    new MutationObserver(applyAc).observe(ac, { childList: true, subtree: true });
    applyAc();
  }

  // Contact / referral forms: sent by the Python form mailer at /forms/send
  document.querySelectorAll('form[data-endpoint]').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var fieldsOk = true;
      f.querySelectorAll('[data-validate]').forEach(function (input) { if (!checkField(input, true)) fieldsOk = false; });
      if (!fieldsOk) { var bad = f.querySelector('[aria-invalid="true"]'); if (bad) bad.focus(); return; }
      if (!f.reportValidity()) return;
      var btn = f.querySelector('[type=submit]'), err = f.querySelector('.form-error');
      if (!err) { err = document.createElement('p'); err.className = 'form-error'; err.setAttribute('role', 'alert'); btn.after(err); }
      err.textContent = '';
      btn.disabled = true;
      fetch(f.getAttribute('data-endpoint'), { method: 'POST', body: new FormData(f), headers: { 'Accept': 'application/json' } })
        .then(function (r) { return r.json().catch(function () { return { ok: false }; }); })
        .then(function (res) {
          if (!res.ok) throw new Error(res.error || '');
          var ok = f.parentElement.querySelector('.form-success');
          f.style.display = 'none';
          if (ok) { ok.classList.add('show'); ok.setAttribute('tabindex', '-1'); ok.focus(); }
        })
        .catch(function (x) {
          err.textContent = (x && x.message) || 'Sorry, your message could not be sent. Please email us at hello@ystaxadvisory.ca or call 778-503-8310.';
          btn.disabled = false;
        });
    });
  });

  // Pricing: Health & Wellness / Other Industries toggle
  var tabs = document.querySelectorAll('.toggle-btn');
  tabs.forEach(function (t) {
    t.addEventListener('click', function () {
      tabs.forEach(function (o) {
        var on = o === t;
        o.setAttribute('aria-selected', String(on));
        var panel = document.getElementById(o.getAttribute('data-target'));
        if (panel) {
          panel.hidden = !on;
          if (on) panel.querySelectorAll('.reveal').forEach(function (el) { el.classList.add('in'); });
        }
      });
    });
  });

  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();
})();

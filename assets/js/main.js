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

  // Contact / referral forms: sent by /forms/send.php (PHP mail on the web host)
  document.querySelectorAll('form[data-endpoint]').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
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

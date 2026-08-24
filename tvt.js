/* TVT Capital — shared behaviour. No dependencies. */
(function () {
  "use strict";

  /* ---- Mobile nav ---- */
  var bar = document.getElementById("navBar");
  var toggle = bar && bar.querySelector(".nav-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = bar.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* ---- Scroll reveal ---- */
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var targets = document.querySelectorAll(".reveal");
  if (reduced || !("IntersectionObserver" in window)) {
    Array.prototype.forEach.call(targets, function (el) { el.classList.add("in"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var el = e.target;
        var delay = parseInt(el.getAttribute("data-reveal-delay") || "0", 10);
        setTimeout(function () { el.classList.add("in"); }, delay);
        io.unobserve(el);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });
    Array.prototype.forEach.call(targets, function (el) { io.observe(el); });
  }

  /* ---- Phone formatting, shared by every form ---- */
  function bindPhone(input) {
    input.addEventListener("input", function () {
      var d = input.value.replace(/\D/g, "").slice(0, 10);
      input.value = d.length > 6 ? "(" + d.slice(0, 3) + ") " + d.slice(3, 6) + "-" + d.slice(6)
                  : d.length > 3 ? "(" + d.slice(0, 3) + ") " + d.slice(3)
                  : d;
    });
  }
  Array.prototype.forEach.call(document.querySelectorAll('input[type="tel"]'), bindPhone);

  /* ---- Three-step borrower intake ---- */
  Array.prototype.forEach.call(document.querySelectorAll("[data-wizard]"), function (form) {
    var steps = form.querySelectorAll(".fstep");
    var total = steps.length || 1;
    var counter = form.querySelector("[data-wizard-now]");
    var barFill = form.querySelector("[data-wizard-bar]");
    var now = 1;

    function go(n) {
      now = Math.max(1, Math.min(total, n));
      Array.prototype.forEach.call(steps, function (s) {
        s.classList.toggle("on", parseInt(s.dataset.step, 10) === now);
      });
      if (counter) counter.textContent = now;
      if (barFill) barFill.style.width = (now / total * 100) + "%";
      var focusable = form.querySelector(".fstep.on input, .fstep.on select");
      if (focusable && now > 1 && focusable.type === "text") focusable.focus({ preventScroll: true });
    }

    form.addEventListener("change", function (e) {
      if (e.target.name === "Capital Needed" && now === 1) setTimeout(function () { go(2); }, 220);
      else if (e.target.name === "Use of Proceeds" && now === 2) setTimeout(function () { go(3); }, 220);
    });
    Array.prototype.forEach.call(form.querySelectorAll("[data-back]"), function (b) {
      b.addEventListener("click", function () { go(now - 1); });
    });

    form.addEventListener("submit", function () {
      var subj = form.querySelector('input[name="subject"]');
      if (!subj) return;
      var amt = form.querySelector('input[name="Capital Needed"]:checked');
      var co = form.querySelector('input[name="company"]');
      subj.value = "New borrower application — " +
        ((co && co.value.trim()) || "unnamed company") +
        (amt ? " (" + amt.value + ")" : "");
    });

    go(1);
  });

  /* ---- Subject lines for the partner and contact forms ---- */
  var partner = document.forms["partner-application"];
  if (partner) {
    partner.addEventListener("submit", function () {
      var subj = partner.querySelector('input[name="subject"]');
      if (!subj) return;
      var firm = partner.querySelector('input[name="firm"]');
      var vol = partner.querySelector('select[name="Annual Placement Volume"]');
      subj.value = "New partner application — " +
        ((firm && firm.value.trim()) || "unnamed firm") +
        (vol ? " (" + vol.value + ")" : "");
    });
  }

  var contact = document.forms["contact-message"];
  if (contact) {
    contact.addEventListener("submit", function () {
      var subj = contact.querySelector('input[name="subject"]');
      if (!subj) return;
      var r = contact.querySelector('input[name="Reason"]:checked');
      var n = contact.querySelector('input[name="name"]');
      subj.value = "New contact message — " + (r ? r.value : "General") +
        ((n && n.value.trim()) ? " — " + n.value.trim() : "");
    });
  }
})();

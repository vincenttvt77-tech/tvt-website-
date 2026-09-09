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
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
  }

  if (toggle) {
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && bar.classList.contains("open")) {
        bar.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", "Open menu");
        toggle.focus();
      }
    });
    document.addEventListener("click", function (e) {
      if (!bar.contains(e.target)) {
        bar.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", "Open menu");
      }
    });
  }

  /* Keep the confirmation page on the same site as the submitted form. */
  document.querySelectorAll('form input[name="redirect"]').forEach(function (input) {
    input.value = new URL("thanks.html", window.location.href).href;
  });

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
    form.noValidate = true;
    if (counter) counter.parentElement.setAttribute("aria-live", "polite");
    steps.forEach(function (step, index) {
      if (index === steps.length - 1) return;
      var next = document.createElement("button");
      next.type = "button";
      next.className = "btn btn-primary wizard-next";
      next.textContent = "Continue →";
      next.addEventListener("click", function () {
        var invalid = step.querySelector("input:invalid, select:invalid, textarea:invalid");
        if (invalid) { invalid.focus(); invalid.reportValidity(); return; }
        go(now + 1, true);
      });
      step.appendChild(next);
    });

    function go(n, focus) {
      now = Math.max(1, Math.min(total, n));
      Array.prototype.forEach.call(steps, function (s) {
        s.classList.toggle("on", parseInt(s.dataset.step, 10) === now);
      });
      if (counter) counter.textContent = now;
      if (barFill) barFill.style.width = (now / total * 100) + "%";
      var focusable = form.querySelector(".fstep.on input, .fstep.on select");
      if (focusable && focus) focusable.focus({ preventScroll: true });
    }

    Array.prototype.forEach.call(form.querySelectorAll("[data-back]"), function (b) {
      b.addEventListener("click", function () { go(now - 1, true); });
    });

    form.addEventListener("submit", function (event) {
      var invalid = form.querySelector("input:invalid, select:invalid, textarea:invalid");
      if (invalid) {
        event.preventDefault();
        var step = invalid.closest(".fstep");
        if (step) go(Number(step.dataset.step));
        invalid.focus();
        invalid.reportValidity();
        return;
      }
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

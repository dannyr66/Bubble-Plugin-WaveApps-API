// Inquiry forms: POST to data-endpoint when one is configured in build.py,
// otherwise tell the visitor to email us so no inquiry is silently lost.
(function () {
  var EMAIL = "hello@glambotphilly.com";

  document.querySelectorAll("form.inquiry").forEach(function (form) {
    var status = form.querySelector(".form-status");
    var date = form.querySelector('input[type="date"]');
    if (date) date.min = new Date().toISOString().slice(0, 10);

    function show(msg) {
      status.textContent = msg;
      status.hidden = false;
    }

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var missing = Array.prototype.filter.call(form.querySelectorAll("[required]"), function (el) {
        return !el.value.trim();
      });
      if (missing.length) {
        missing[0].focus();
        show("Please add your name, email and event date so we can check availability.");
        return;
      }
      var email = form.querySelector('input[type="email"]');
      if (email && !/^\S+@\S+\.\S+$/.test(email.value)) {
        email.focus();
        show("That email address doesn't look complete. Please check it and send again.");
        return;
      }

      var endpoint = form.getAttribute("data-endpoint");
      if (!endpoint) {
        show("Online booking is being connected. For now, email your date and details to " + EMAIL + " and we'll reply the same day.");
        return;
      }

      var button = form.querySelector('button[type="submit"]');
      button.disabled = true;
      button.textContent = "Sending...";
      fetch(endpoint, { method: "POST", body: new FormData(form), headers: { Accept: "application/json" } })
        .then(function (res) {
          if (!res.ok) throw new Error(res.status);
          form.reset();
          show("Got it. We'll check the calendar and reply with availability and a quote, usually the same day.");
        })
        .catch(function () {
          show("That didn't go through. Please email your details to " + EMAIL + " and we'll take it from there.");
        })
        .then(function () {
          button.disabled = false;
          button.textContent = "Send my date";
        });
    });
  });

  // Close the mobile menu after choosing a link on the same page.
  document.querySelectorAll(".menu-toggle a").forEach(function (a) {
    a.addEventListener("click", function () {
      var d = a.closest(".menu-toggle");
      if (d) d.removeAttribute("open");
    });
  });

  // Close the desktop Events dropdown when clicking elsewhere.
  document.addEventListener("click", function (ev) {
    document.querySelectorAll(".nav .dropdown[open]").forEach(function (d) {
      if (!d.contains(ev.target)) d.removeAttribute("open");
    });
  });
})();

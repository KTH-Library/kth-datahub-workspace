/* Digital services archive: search, filters, clickable tags and modals.
   State lives in the URL so a filtered view (and an open card) can be shared. */
(function () {
  "use strict";

  function init() {
    var archive = document.querySelector(".svc-archive");
    if (!archive || archive.dataset.ready === "1") return;
    archive.dataset.ready = "1";

    var form = archive.querySelector(".svc-filters");
    var search = form.querySelector('input[name="q"]');
    var selects = {
      provider: form.querySelector('select[name="provider"]'),
      group: form.querySelector('select[name="group"]'),
      type: form.querySelector('select[name="type"]')
    };
    var reset = form.querySelector(".svc-filters__reset");
    var cards = Array.prototype.slice.call(archive.querySelectorAll(".svc-card"));
    var count = archive.querySelector(".svc-count");
    var noresults = archive.querySelector(".svc-noresults");
    var lastFocus = null;

    function matches(card) {
      var q = search.value.trim().toLowerCase();
      if (q && card.dataset.search.indexOf(q) === -1) return false;
      for (var key in selects) {
        var value = selects[key].value;
        if (value && card.dataset[key] !== value) return false;
      }
      return true;
    }

    function apply(pushState) {
      var visible = 0;
      cards.forEach(function (card) {
        var show = matches(card);
        card.hidden = !show;
        if (show) visible++;
      });
      count.textContent = visible + " " + (archive.dataset.labelOf || "av") + " " +
        cards.length + " " + (archive.dataset.labelItems || "tjänster");

      noresults.hidden = visible !== 0;
      var dirty = !!search.value || !!selects.provider.value ||
        !!selects.group.value || !!selects.type.value;
      reset.disabled = !dirty;
      if (pushState !== false) writeUrl();
    }

    function writeUrl(openId) {
      var params = new URLSearchParams();
      if (search.value) params.set("q", search.value);
      for (var key in selects) if (selects[key].value) params.set(key, selects[key].value);
      var open = typeof openId !== "undefined" ? openId : currentOpenId();
      if (open) params.set("service", open);
      var qs = params.toString();
      history.replaceState(null, "", qs ? "?" + qs : location.pathname);
    }

    function currentOpenId() {
      var open = archive.querySelector(".svc-modal:not([hidden])");
      return open ? open.id.replace("svc-modal-", "") : "";
    }

    /* ---- modal ---- */

    function openModal(id, focusEl) {
      var modal = document.getElementById("svc-modal-" + id);
      if (!modal) return;
      closeModal(true);
      lastFocus = focusEl || document.activeElement;
      modal.hidden = false;
      document.body.classList.add("svc-modal-open");
      var close = modal.querySelector(".svc-modal__close");
      if (close) close.focus();
      writeUrl(id);
    }

    function closeModal(silent) {
      var open = archive.querySelector(".svc-modal:not([hidden])");
      if (open) open.hidden = true;
      document.body.classList.remove("svc-modal-open");
      if (!silent) {
        if (lastFocus && lastFocus.focus) lastFocus.focus();
        writeUrl("");
      }
    }

    archive.addEventListener("click", function (event) {
      var open = event.target.closest("[data-open]");
      if (open) {
        event.preventDefault();
        openModal(open.dataset.open, open);
        return;
      }
      var close = event.target.closest("[data-close]");
      if (close) {
        event.preventDefault();
        closeModal();
        return;
      }
      var tag = event.target.closest(".svc-tag");
      if (tag) {
        event.preventDefault();
        var kind = tag.dataset.tagKind;
        var value = tag.dataset.tagValue;
        if (selects[kind]) {
          selects[kind].value = selects[kind].value === value ? "" : value;
          search.value = "";
        } else {
          search.value = search.value === tag.textContent.trim() ? "" : tag.textContent.trim();
        }
        closeModal(true);
        document.body.classList.remove("svc-modal-open");
        apply();
        archive.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && archive.querySelector(".svc-modal:not([hidden])")) {
        closeModal();
      }
    });

    /* ---- wiring ---- */

    search.addEventListener("input", function () { apply(); });
    Object.keys(selects).forEach(function (key) {
      selects[key].addEventListener("change", function () { apply(); });
    });
    reset.addEventListener("click", function () {
      search.value = "";
      Object.keys(selects).forEach(function (key) { selects[key].value = ""; });
      apply();
    });

    var params = new URLSearchParams(location.search);
    search.value = params.get("q") || "";
    Object.keys(selects).forEach(function (key) {
      var value = params.get(key);
      if (value) selects[key].value = value;
    });
    apply(false);
    if (params.get("service")) openModal(params.get("service"));
  }

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(init);
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }
})();

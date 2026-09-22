/* ==========================================================================
   Digital service catalogue — search, filtering, tags and modals
   --------------------------------------------------------------------------
   WHY THIS EXISTS
   The site is a static MkDocs build with no backend, so all filtering happens
   in the browser against markup generated at build time by
   service_catalog/hooks/services.py. Every card carries the data it is
   filtered on (`data-search`, `data-provider`, `data-group`, `data-type`),
   which keeps this file free of any knowledge about individual services.

   INPUTS   The generated `.svc-archive` block, plus the query string.
   OUTPUT   Cards shown/hidden, a result counter, open/closed modals and a
            shareable URL (`?q=&provider=&group=&type=&service=`).

   HIDING CONTRACT — READ BEFORE CHANGING
   A card is hidden by setting its `hidden` attribute. That only takes effect
   because services.css restates `.svc-card[hidden] { display: none; }`; the
   browser's default `[hidden]` rule loses to the `.svc-card { display: flex }`
   rule. The original bug was exactly this: the counter updated but every card
   stayed on screen. If you hide a new element here, give it the same rule.

   DEPENDENCIES
   None. Written in ES5-compatible vanilla JS and re-initialised on Material's
   `document$` observable, because instant navigation swaps the page body
   without a full reload.
   ========================================================================== */
(function () {
  "use strict";

  /* Prefix of the generated modal element ids (`svc-modal-<service id>`). */
  var MODAL_ID_PREFIX = "svc-modal-";
  /* Marks an archive that has already been wired up, so instant navigation
     cannot attach a second set of listeners to the same DOM. */
  var READY_FLAG = "1";
  /* Fallbacks used only if the generated labels are missing (Swedish page). */
  var FALLBACK_LABEL_OF = "av";
  var FALLBACK_LABEL_ITEMS = "tjänster";

  function init() {
    var archive = document.querySelector(".svc-archive");
    if (!archive || archive.dataset.ready === READY_FLAG) return;
    archive.dataset.ready = READY_FLAG;

    var form = archive.querySelector(".svc-filters");
    var search = form.querySelector('input[name="q"]');

    /* Keys match both the `<select name>` and the card `data-*` attribute,
       which is what lets `matches()` stay generic. Adding a fourth filter is
       a matter of generating the select + data attribute and adding it here. */
    var selects = {
      provider: form.querySelector('select[name="provider"]'),
      group: form.querySelector('select[name="group"]'),
      type: form.querySelector('select[name="type"]')
    };

    var reset = form.querySelector(".svc-filters__reset");
    var cards = Array.prototype.slice.call(archive.querySelectorAll(".svc-card"));
    var count = archive.querySelector(".svc-count");
    var noresults = archive.querySelector(".svc-noresults");
    /* Element that had focus before a modal opened, so focus can be restored
       when it closes (keyboard and screen-reader users would otherwise be
       dropped back at the top of the document). */
    var lastFocus = null;

    /**
     * Decide whether a card passes the current search text and dropdowns.
     * Free text matches the pre-computed `data-search` blob (name, provider,
     * group, type, summary, access and all tag labels, lowercased at build
     * time). Dropdowns compare slugs, so they are accent- and case-safe.
     * @param {HTMLElement} card
     * @returns {boolean} true when the card should stay visible
     */
    function matches(card) {
      var q = search.value.trim().toLowerCase();
      if (q) {
        var terms = q.split(/\s+/);
        for (var i = 0; i < terms.length; i++) {
          if (card.dataset.search.indexOf(terms[i]) === -1) return false;
        }
      }
      for (var key in selects) {
        var value = selects[key].value;
        if (value && card.dataset[key] !== value) return false;
      }
      return true;
    }

    /**
     * Apply the current filter state to the grid.
     * Side effects: toggles `hidden` on every card, updates the counter and
     * the "no results" message, enables/disables Clear, and (unless
     * `pushState === false`) rewrites the query string.
     * @param {boolean} [pushState] pass false during initial load
     */
    function apply(pushState) {
      var visible = 0;
      cards.forEach(function (card) {
        var show = matches(card);
        /* See the HIDING CONTRACT note at the top of this file. */
        card.hidden = !show;
        if (show) visible++;
      });

      count.textContent = visible + " " + (archive.dataset.labelOf || FALLBACK_LABEL_OF) +
        " " + cards.length + " " + (archive.dataset.labelItems || FALLBACK_LABEL_ITEMS);

      noresults.hidden = visible !== 0;

      var dirty = !!search.value || !!selects.provider.value ||
        !!selects.group.value || !!selects.type.value;
      reset.disabled = !dirty;

      if (pushState !== false) writeUrl();
    }

    /**
     * Mirror the current state into the query string with replaceState, so a
     * filtered view (and an open card) can be copied, shared and reloaded
     * without filling the browser history with one entry per keystroke.
     * @param {string} [openId] service id of the modal to record; omit to
     *        reuse whichever modal is currently open
     */
    function writeUrl(openId) {
      var params = new URLSearchParams();
      if (search.value) params.set("q", search.value);
      for (var key in selects) if (selects[key].value) params.set(key, selects[key].value);
      var open = typeof openId !== "undefined" ? openId : currentOpenId();
      if (open) params.set("service", open);
      var qs = params.toString();
      history.replaceState(null, "", qs ? "?" + qs : location.pathname);
    }

    /** @returns {string} id of the open service modal, or "" if none is open */
    function currentOpenId() {
      var open = archive.querySelector(".svc-modal:not([hidden])");
      return open ? open.id.replace(MODAL_ID_PREFIX, "") : "";
    }

    /* ---- modal ----------------------------------------------------------
       Modals are pre-rendered and hidden; opening one never touches the grid,
       so closing it returns the reader to exactly the filtered view they came
       from. */

    /**
     * Open the modal for a service.
     * @param {string} id service id (the markdown filename, slugified)
     * @param {HTMLElement} [focusEl] element to return focus to on close
     */
    function openModal(id, focusEl) {
      var modal = document.getElementById(MODAL_ID_PREFIX + id);
      if (!modal) return;
      closeModal(true); /* only one modal at a time */
      lastFocus = focusEl || document.activeElement;
      modal.hidden = false;
      document.body.classList.add("svc-modal-open");
      var close = modal.querySelector(".svc-modal__close");
      if (close) close.focus();
      writeUrl(id);
    }

    /**
     * Close the open modal.
     * @param {boolean} [silent] when true, skip focus restore and URL update
     *        (used when immediately opening another modal or filtering)
     */
    function closeModal(silent) {
      var open = archive.querySelector(".svc-modal:not([hidden])");
      if (open) open.hidden = true;
      document.body.classList.remove("svc-modal-open");
      if (!silent) {
        if (lastFocus && lastFocus.focus) lastFocus.focus();
        writeUrl("");
      }
    }

    /* ---- event handling -------------------------------------------------
       One delegated click listener on the archive covers cards, close buttons
       and tags. Delegation matters because every card, tag and modal is
       generated markup: no per-element wiring has to be kept in sync. */

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
          /* Clicking the active tag again clears the filter (toggle). */
          selects[kind].value = selects[kind].value === value ? "" : value;
          search.value = "";
        } else {
          /* Tag families without a dropdown (data, location) fall back to a
             free-text search on the label. */
          search.value = search.value === tag.textContent.trim() ? "" : tag.textContent.trim();
        }
        /* Silent close: the reader asked for a new filtered view, so the URL
           should describe the filter, not the card they came from. */
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

    search.addEventListener("input", function () { apply(); });
    Object.keys(selects).forEach(function (key) {
      selects[key].addEventListener("change", function () { apply(); });
    });
    reset.addEventListener("click", function () {
      search.value = "";
      Object.keys(selects).forEach(function (key) { selects[key].value = ""; });
      apply();
    });

    /* ---- restore state from the URL ------------------------------------ */

    var params = new URLSearchParams(location.search);
    search.value = params.get("q") || "";
    Object.keys(selects).forEach(function (key) {
      var value = params.get(key);
      if (value) selects[key].value = value;
    });
    apply(false); /* false: don't rewrite the URL we just read */
    if (params.get("service")) openModal(params.get("service"));
  }

  /* Material for MkDocs uses instant navigation: the body is replaced without
     a page load, so `DOMContentLoaded` fires only once. `document$` emits on
     every page view; the READY_FLAG guard keeps that idempotent. */
  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(init);
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }
})();

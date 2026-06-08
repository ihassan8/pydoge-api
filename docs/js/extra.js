/**
 * PyDOGE API documentation — lightweight interactive enhancements.
 */

(function () {
  "use strict";

  /* Reveal feature cards as they scroll into view. */
  function initScrollReveal() {
    var cards = document.querySelectorAll(".md-typeset .grid.cards > ul > li");
    if (!cards.length || !("IntersectionObserver" in window)) {
      return;
    }

    cards.forEach(function (card, i) {
      card.style.opacity = "0";
      card.style.transform = "translateY(12px)";
      card.style.transition = "opacity 0.4s ease, transform 0.4s ease";
      card.style.transitionDelay = (i % 3) * 70 + "ms";
    });

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.style.opacity = "1";
            entry.target.style.transform = "translateY(0)";
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: "0px 0px -40px 0px" }
    );

    cards.forEach(function (card) { observer.observe(card); });
  }

  function init() {
    initScrollReveal();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Re-run after Material instant navigation, if available.
  try {
    document$.subscribe(init);
  } catch (e) {
    /* non-Material build — ignore */
  }
})();

(() => {
  "use strict";

  const bookRoute = window.location.pathname.match(/^\/books\/([^/]+)(?:\/(.*))?\/?$/);
  const homeResume = document.querySelector("[data-reading-latest]");
  const bookSlug = bookRoute?.[1];
  const isBookOpening = bookSlug && !bookRoute[2];
  const isBookPage = bookSlug && Boolean(bookRoute[2]);
  const positionKey = (slug) => `learning4comfort:reading:v1:${slug}`;
  const latestKey = "learning4comfort:reading:v1:latest";

  function readPosition(key) {
    try {
      const value = JSON.parse(window.localStorage.getItem(key));
      if (value && typeof value.url === "string" && Number.isFinite(value.scrollY)) {
        return value;
      }
    } catch {
      return null;
    }
    return null;
  }

  function makeResumeUrl(position) {
    const url = new URL(position.url, window.location.origin);
    url.searchParams.set("resume", "1");
    if (position.hash) {
      url.hash = position.hash;
    }
    return `${url.pathname}${url.search}${url.hash}`;
  }

  function showResume(container, position) {
    if (!container || !position) {
      return;
    }
    const link = container.querySelector("[data-reading-resume-link]");
    link.href = makeResumeUrl(position);
    link.textContent = `Continue at ${position.pageTitle || "your last place"}`;
    container.hidden = false;
  }

  if (homeResume) {
    const latest = readPosition(latestKey);
    if (latest) {
      const saved = readPosition(positionKey(latest.bookSlug));
      if (saved && saved.url === latest.url) {
        const link = homeResume.querySelector("[data-reading-resume-link]");
        link.href = makeResumeUrl(saved);
        link.textContent = `Continue ${saved.bookTitle}: ${saved.pageTitle || "your last place"}`;
        homeResume.hidden = false;
      }
    }
  }

  if (isBookOpening) {
    const container = document.querySelector(`[data-reading-book="${CSS.escape(bookSlug)}"]`);
    const saved = readPosition(positionKey(bookSlug));
    showResume(container, saved);
    container?.querySelector("[data-reading-start-over]")?.addEventListener("click", () => {
      try {
        window.localStorage.removeItem(positionKey(bookSlug));
        const latest = readPosition(latestKey);
        if (latest?.bookSlug === bookSlug) {
          window.localStorage.removeItem(latestKey);
        }
      } catch {
        return;
      }
      container.hidden = true;
    });
  }

  if (!isBookPage) {
    return;
  }

  const savedPosition = readPosition(positionKey(bookSlug));
  const url = new URL(window.location.href);
  if (url.searchParams.get("resume") === "1" && savedPosition?.url === url.pathname) {
    url.searchParams.delete("resume");
    window.history.replaceState(null, "", `${url.pathname}${url.search}${url.hash}`);
    window.addEventListener(
      "load",
      () => window.requestAnimationFrame(() => window.scrollTo(0, savedPosition.scrollY)),
      { once: true },
    );
  }

  let saveTimer;
  function persistPosition() {
    const position = {
      bookSlug,
      bookTitle: document.querySelector(".crumb a")?.textContent.trim() || bookSlug,
      pageTitle: document.querySelector("h1.article-title")?.textContent.trim() || document.title,
      url: window.location.pathname,
      hash: window.location.hash,
      scrollY: Math.max(0, Math.round(window.scrollY)),
      updatedAt: Date.now(),
    };
    try {
      window.localStorage.setItem(positionKey(bookSlug), JSON.stringify(position));
      window.localStorage.setItem(latestKey, JSON.stringify(position));
    } catch {
      // Keep reading usable when browser storage is disabled or full.
    }
  }

  function scheduleSave() {
    window.clearTimeout(saveTimer);
    saveTimer = window.setTimeout(persistPosition, 250);
  }

  function saveOnPageHide() {
    window.clearTimeout(saveTimer);
    persistPosition();
  }

  window.addEventListener("scroll", scheduleSave, { passive: true });
  window.addEventListener("pagehide", saveOnPageHide);
})();
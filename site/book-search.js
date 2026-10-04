(() => {
  "use strict";

  const maximumResults = 50;
  const indexes = new Map();

  function normalize(value) {
    return value
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLocaleLowerCase();
  }

  function termsFor(query) {
    return normalize(query).match(/[\p{L}\p{N}]+/gu) || [];
  }

  function loadIndex(url) {
    if (!indexes.has(url)) {
      indexes.set(
        url,
        fetch(url).then((response) => {
          if (!response.ok) {
            throw new Error(`Search index request failed: ${response.status}`);
          }
          return response.json();
        }),
      );
    }
    return indexes.get(url).catch((error) => {
      indexes.delete(url);
      throw error;
    });
  }

  function excerpt(text, terms) {
    const folded = normalize(text);
    const matchAt = Math.min(
      ...terms.map((term) => {
        const position = folded.indexOf(term);
        return position < 0 ? Number.MAX_SAFE_INTEGER : position;
      }),
    );
    const start =
      matchAt === Number.MAX_SAFE_INTEGER ? 0 : Math.max(0, matchAt - 70);
    const end = Math.min(text.length, start + 220);
    return `${start > 0 ? "…" : ""}${text.slice(start, end)}${end < text.length ? "…" : ""}`;
  }

  function makeResult(result) {
    const item = document.createElement("li");
    item.className = "book-search-result";

    const link = document.createElement("a");
    link.href = result.url;

    const title = document.createElement("strong");
    title.textContent = result.title;
    link.append(title);

    if (result.heading) {
      const section = document.createElement("span");
      section.className = "book-search-section";
      section.textContent = result.heading;
      link.append(section);
    }
    item.append(link);

    const snippet = document.createElement("p");
    snippet.textContent = result.snippet;
    item.append(snippet);
    return item;
  }

  async function search(form, results, query) {
    const terms = [...new Set(termsFor(query))];
    if (!terms.length) {
      results.textContent = "Enter a word or phrase to search this book.";
      return;
    }

    results.textContent = "Searching this book…";
    try {
      const index = await loadIndex(form.closest("[data-index-url]").dataset.indexUrl);
      const matches = [];

      for (const page of index.documents) {
        for (const section of page.sections) {
          const text = `${page.title} ${section.heading} ${section.text}`;
          const folded = normalize(text);
          if (!terms.every((term) => folded.includes(term))) {
            continue;
          }
          const fragment = section.id ? `#${encodeURIComponent(section.id)}` : "";
          matches.push({
            title: page.title,
            heading: section.heading,
            url: `${page.url}${fragment}`,
            snippet: excerpt(section.text || text, terms),
            order: matches.length,
          });
        }
      }

      matches.sort((left, right) => {
        const leftScore = terms.reduce(
          (score, term) => score + (normalize(left.snippet).includes(term) ? 1 : 0),
          0,
        );
        const rightScore = terms.reduce(
          (score, term) => score + (normalize(right.snippet).includes(term) ? 1 : 0),
          0,
        );
        return rightScore - leftScore || left.order - right.order;
      });

      results.replaceChildren();
      const summary = document.createElement("p");
      summary.textContent = matches.length
        ? `${matches.length} ${matches.length === 1 ? "result" : "results"} in this book.`
        : "No matches found in this book.";
      results.append(summary);

      if (matches.length) {
        const list = document.createElement("ol");
        list.className = "book-search-result-list";
        matches.slice(0, maximumResults).forEach((match) => {
          list.append(makeResult(match));
        });
        results.append(list);
        if (matches.length > maximumResults) {
          const limit = document.createElement("p");
          limit.textContent = `Showing the first ${maximumResults} results.`;
          results.append(limit);
        }
      }
    } catch {
      results.textContent = "Search is unavailable right now. Please try again.";
    }
  }

  document.querySelectorAll(".book-search form").forEach((form) => {
    const input = form.querySelector('input[name="q"]');
    const results = form.parentElement.querySelector(".book-search-results");
    const query = new URLSearchParams(window.location.search).get("q");
    if (query !== null) {
      input.value = query;
      search(form, results, query);
    }

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const query = input.value.trim();
      const url = new URL(form.action, window.location.href);
      if (query) {
        url.searchParams.set("q", query);
      } else {
        url.searchParams.delete("q");
      }
      window.history.replaceState(null, "", url);
      search(form, results, query);
    });
  });
})();

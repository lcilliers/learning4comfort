(() => {
  "use strict";

  const maximumResults = 100;
  const { parse, find, excerpt } = window.L4CSearch;

  function makeResult(result) {
    const item = document.createElement("li");
    item.className = "global-search-result";

    const link = document.createElement("a");
    link.href = `${result.url}${result.section_id ? `#${encodeURIComponent(result.section_id)}` : ""}`;
    link.textContent = `${result.book_title} · ${result.title}`;
    item.append(link);

    if (result.heading) {
      const section = document.createElement("p");
      section.className = "global-search-section";
      section.textContent = result.heading;
      item.append(section);
    }

    const snippet = document.createElement("p");
    snippet.textContent = result.snippet;
    item.append(snippet);
    return item;
  }

  async function search(form, results, query) {
    const parsed = parse(query);
    if (parsed.kind === "empty") {
      results.textContent = "Enter a word, phrase or Bible reference to search all books.";
      return;
    }
    if (parsed.kind === "invalid") {
      results.textContent = `No matches found. ${parsed.message}`;
      return;
    }

    results.textContent = "Searching all books…";
    try {
      const response = await fetch(form.dataset.indexUrl);
      if (!response.ok) {
        throw new Error(`Search index request failed: ${response.status}`);
      }
      const index = await response.json();
      const matches = [];

      for (const page of index.documents) {
        for (const section of page.sections) {
          const text = `${page.book_title} ${page.title} ${section.heading} ${section.text}`;
          if (find(text, parsed) < 0) {
            continue;
          }
          const body = section.text || text;
          matches.push({
            book_title: page.book_title,
            title: page.title,
            url: page.url,
            section_id: section.id,
            heading: section.heading,
            snippet: excerpt(body, find(body, parsed)),
            order: matches.length,
          });
        }
      }

      results.replaceChildren();
      const summary = document.createElement("p");
      const scope = parsed.kind === "reference" ? ` citing ${parsed.label}` : "";
      summary.textContent = matches.length
        ? `${matches.length} ${matches.length === 1 ? "result" : "results"}${scope} across ${new Set(matches.map((match) => match.book_title)).size} ${new Set(matches.map((match) => match.book_title)).size === 1 ? "book" : "books"}.`
        : `No matches found${scope} across the published books.`;
      results.append(summary);

      if (matches.length) {
        const list = document.createElement("ol");
        list.className = "global-search-result-list";
        matches.slice(0, maximumResults).forEach((match) => list.append(makeResult(match)));
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

  document.querySelectorAll(".global-search").forEach((form) => {
    const input = form.querySelector('input[name="q"]');
    const results = form.parentElement.querySelector(".global-search-results");
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
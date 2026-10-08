// Shared query parsing and matching for the site-wide and book search boxes.
//
// A query that reads as a Bible reference ("Rom 8:27", "Romans 8:26-27",
// "Psalm 23") is matched only against references written in the text, never
// broken into loose letter and number fragments. Any other query is matched
// word by word from the start of a word, and "quoted phrases" as a whole.
(() => {
  "use strict";

  // Canonical name first, then the abbreviations accepted for it.
  const books = [
    ["Genesis", "Gen", "Ge", "Gn"],
    ["Exodus", "Exod", "Exo", "Ex"],
    ["Leviticus", "Lev", "Le", "Lv"],
    ["Numbers", "Num", "Nu", "Nm"],
    ["Deuteronomy", "Deut", "Deu", "Dt"],
    ["Joshua", "Josh", "Jos"],
    ["Judges", "Judg", "Jdg", "Jg"],
    ["Ruth", "Rut", "Ru"],
    ["1 Samuel", "1 Sam", "1 Sa"],
    ["2 Samuel", "2 Sam", "2 Sa"],
    ["1 Kings", "1 Kgs", "1 Ki", "1 Kin"],
    ["2 Kings", "2 Kgs", "2 Ki", "2 Kin"],
    ["1 Chronicles", "1 Chron", "1 Chr", "1 Ch"],
    ["2 Chronicles", "2 Chron", "2 Chr", "2 Ch"],
    ["Ezra", "Ezr"],
    ["Nehemiah", "Neh", "Ne"],
    ["Esther", "Esth", "Est"],
    ["Job", "Jb"],
    ["Psalms", "Psalm", "Psa", "Pss", "Ps"],
    ["Proverbs", "Prov", "Pro", "Prv", "Pr"],
    ["Ecclesiastes", "Eccl", "Ecc", "Ec", "Qoheleth"],
    ["Song of Songs", "Song of Solomon", "Song", "Sng", "SoS", "Canticles"],
    ["Isaiah", "Isa", "Is"],
    ["Jeremiah", "Jer", "Je"],
    ["Lamentations", "Lam", "La"],
    ["Ezekiel", "Ezek", "Eze", "Ezk"],
    ["Daniel", "Dan", "Da", "Dn"],
    ["Hosea", "Hos", "Ho"],
    ["Joel", "Jl"],
    ["Amos", "Am"],
    ["Obadiah", "Obad", "Oba", "Ob"],
    ["Jonah", "Jon", "Jnh"],
    ["Micah", "Mic", "Mi"],
    ["Nahum", "Nah", "Na"],
    ["Habakkuk", "Hab"],
    ["Zephaniah", "Zeph", "Zep"],
    ["Haggai", "Hag"],
    ["Zechariah", "Zech", "Zec"],
    ["Malachi", "Mal"],
    ["Matthew", "Matt", "Mat", "Mt"],
    ["Mark", "Mrk", "Mar", "Mk"],
    ["Luke", "Luk", "Lk"],
    ["John", "Joh", "Jn"],
    ["Acts", "Act", "Ac"],
    ["Romans", "Rom", "Ro", "Rm"],
    ["1 Corinthians", "1 Cor", "1 Co"],
    ["2 Corinthians", "2 Cor", "2 Co"],
    ["Galatians", "Gal", "Ga"],
    ["Ephesians", "Ephes", "Eph"],
    ["Philippians", "Phili", "Phil", "Php"],
    ["Colossians", "Col"],
    ["1 Thessalonians", "1 Thess", "1 Thes", "1 Th"],
    ["2 Thessalonians", "2 Thess", "2 Thes", "2 Th"],
    ["1 Timothy", "1 Tim", "1 Ti"],
    ["2 Timothy", "2 Tim", "2 Ti"],
    ["Titus", "Tit"],
    ["Philemon", "Philem", "Phlm", "Phm"],
    ["Hebrews", "Heb"],
    ["James", "Jas", "Jam", "Jm"],
    ["1 Peter", "1 Pet", "1 Pe", "1 Pt"],
    ["2 Peter", "2 Pet", "2 Pe", "2 Pt"],
    ["1 John", "1 Joh", "1 Jn", "1 Jo"],
    ["2 John", "2 Joh", "2 Jn", "2 Jo"],
    ["3 John", "3 Joh", "3 Jn", "3 Jo"],
    ["Jude", "Jud"],
    ["Revelation", "Rev", "Re", "Rv"],
  ];

  const squash = (value) => value.toLocaleLowerCase().replace(/[\s.]/g, "");
  const escape = (value) => value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

  // Squashed spelling ("1sam", "songofsongs") -> canonical name.
  const bookFor = new Map();
  // Every written spelling, with whether it is the full name.
  const spellings = [];
  for (const [name, ...abbreviations] of books) {
    for (const spelling of [name, ...abbreviations]) {
      const full = spelling === name || spelling === "Psalm";
      bookFor.set(squash(spelling), name);
      spellings.push({ spelling, name, full });
      if (/^\d /.test(spelling)) {
        bookFor.set(squash(spelling.replace(" ", "")), name);
        spellings.push({ spelling: spelling.replace(" ", ""), name, full: false });
      }
    }
  }
  spellings.sort((left, right) => right.spelling.length - left.spelling.length);
  const spellingFor = new Map(spellings.map((entry) => [entry.spelling, entry]));

  // A book name in running text: proper-noun case only, not inside another word.
  // A colon after the name allows lists such as "Matthew: 1:18, 12:18".
  const bookAlternatives = spellings.map((entry) => escape(entry.spelling)).join("|");
  const bookInText = new RegExp(`(?<![\\p{L}\\p{N}])(${bookAlternatives})\\.?:?\\s+(?=\\d)`, "gu");
  // A book name starting exactly here, so "8:28, 1 Corinthians 2:9" is not read as verse 1.
  const bookHere = new RegExp(`(?:${bookAlternatives})\\.?:?\\s+\\d`, "uy");
  const dash = "\\s*[-\u2010-\u2015]\\s*";
  const item = new RegExp(
    `(\\d+)(?:\\s*:\\s*(\\d+)(?:${dash}(\\d+)(?:\\s*:\\s*(\\d+))?)?)?(?![\\p{L}\\p{N}:])`,
    "uy",
  );
  const chapterVerseItem = new RegExp(
    `(\\d+)\\s*:\\s*(\\d+)(?:${dash}(\\d+)(?:\\s*:\\s*(\\d+))?)?(?![\\p{L}\\p{N}:])`,
    "uy",
  );
  const verseItem = new RegExp(`(\\d+)(?:${dash}(\\d+))?(?![\\p{L}\\p{N}:])`, "uy");
  const separator = /\s*([;,])\s*/y;
  // A follow-on reference with no book, such as "(8:27)" or "(see 14:2)".
  const bareInText = /\((?:\s*(?:see|cf\.?)\s+)?(?=\d+\s*:\s*\d)/giu;

  const position = (chapter, verse) => chapter * 1000 + verse;

  function rangeOf(match, allowChapterOnly) {
    const chapter = Number(match[1]);
    if (match[2] === undefined) {
      return allowChapterOnly
        ? { start: position(chapter, 0), end: position(chapter, 999), chapter }
        : null;
    }
    const verse = Number(match[2]);
    let end = position(chapter, verse);
    if (match[4] !== undefined) {
      end = position(Number(match[3]), Number(match[4]));
    } else if (match[3] !== undefined) {
      end = position(chapter, Number(match[3]));
    }
    return { start: position(chapter, verse), end: Math.max(end, position(chapter, verse)), chapter };
  }

  // Reads "8:26-27; 10:22", "3:16, 20" and so on from `at`, for one book.
  function readList(text, at, book, allowChapterOnly, found) {
    item.lastIndex = at;
    const first = item.exec(text);
    if (!first) {
      return at;
    }
    let range = rangeOf(first, allowChapterOnly);
    if (!range) {
      return at;
    }
    found.push({ book, start: range.start, end: range.end });
    let end = item.lastIndex;
    let chapter = range.chapter;
    let hasVerse = first[2] !== undefined;

    for (;;) {
      separator.lastIndex = end;
      const gap = separator.exec(text);
      if (!gap) {
        return end;
      }
      bookHere.lastIndex = separator.lastIndex;
      if (bookHere.test(text)) {
        return end;
      }
      chapterVerseItem.lastIndex = separator.lastIndex;
      const next = chapterVerseItem.exec(text);
      if (next) {
        range = rangeOf(next, false);
        found.push({ book, start: range.start, end: range.end });
        end = chapterVerseItem.lastIndex;
        chapter = range.chapter;
        hasVerse = true;
        continue;
      }
      if (gap[1] !== "," || !hasVerse) {
        return end;
      }
      verseItem.lastIndex = separator.lastIndex;
      const verse = verseItem.exec(text);
      if (!verse) {
        return end;
      }
      const from = Number(verse[1]);
      const to = verse[2] === undefined ? from : Number(verse[2]);
      found.push({ book, start: position(chapter, from), end: position(chapter, Math.max(from, to)) });
      end = verseItem.lastIndex;
    }
  }

  const referenceCache = new Map();

  // Every reference written in `text`, as { book, start, end, index }.
  function referencesIn(text) {
    if (referenceCache.has(text)) {
      return referenceCache.get(text);
    }
    const references = [];
    const covered = [];

    bookInText.lastIndex = 0;
    for (let match; (match = bookInText.exec(text)); ) {
      const entry = spellingFor.get(match[1]);
      if (!entry || !/^\d?\s?\p{Lu}/u.test(match[1])) {
        continue;
      }
      const found = [];
      const start = match.index + match[0].length;
      const end = readList(text, start, entry.name, entry.full, found);
      if (!found.length) {
        continue;
      }
      found.forEach((reference) => references.push({ ...reference, index: match.index }));
      covered.push([match.index, end]);
      bookInText.lastIndex = end;
    }

    bareInText.lastIndex = 0;
    for (let match; (match = bareInText.exec(text)); ) {
      const at = match.index + match[0].length;
      const book = covered
        .filter(([start]) => start < match.index)
        .map(([start]) => references.find((reference) => reference.index === start).book)
        .pop();
      if (!book) {
        continue;
      }
      const found = [];
      readList(text, at, book, false, found);
      found.forEach((reference) => references.push({ ...reference, index: match.index }));
    }

    references.sort((left, right) => left.index - right.index);
    referenceCache.set(text, references);
    return references;
  }

  const normalize = (value) =>
    value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase();

  function parseReference(query) {
    const cleaned = query.trim().replace(/^[(\[]+|[)\].,;]+$/g, "").trim();
    const shape = cleaned.match(
      new RegExp(
        `^((?:[1-3]\\s*)?\\p{L}[\\p{L}\\s.]*?)?\\s*(\\d+)(?:\\s*:\\s*(\\d+)(?:${dash}(?:(\\d+)\\s*:\\s*)?(\\d+))?)?$`,
        "u",
      ),
    );
    if (!shape) {
      return null;
    }
    const [, bookText, chapterText, verseText, endChapterText, endVerseText] = shape;
    if (!bookText && verseText === undefined) {
      return null;
    }
    const book = bookText ? bookFor.get(squash(bookText)) : null;
    if (bookText && !book) {
      return verseText === undefined
        ? null
        : { kind: "invalid", message: `"${bookText.trim()}" is not a book of the Bible this search recognises.` };
    }
    const chapter = Number(chapterText);
    let start = position(chapter, 0);
    let end = position(chapter, 999);
    if (verseText !== undefined) {
      start = position(chapter, Number(verseText));
      end = start;
      if (endVerseText !== undefined) {
        end = position(endChapterText === undefined ? chapter : Number(endChapterText), Number(endVerseText));
      }
    }
    const label = `${book ? `${book} ` : ""}${chapter}${verseText === undefined ? "" : `:${verseText}`}${
      endVerseText === undefined ? "" : `-${endChapterText === undefined ? "" : `${endChapterText}:`}${endVerseText}`
    }`;
    return { kind: "reference", book, start, end: Math.max(start, end), label };
  }

  // Returns { kind: "empty" | "invalid" | "reference" | "words", ... }.
  function parse(query) {
    if (!query.trim()) {
      return { kind: "empty" };
    }
    const reference = parseReference(query);
    if (reference) {
      return reference;
    }
    if (/\d\s*:\s*\d/.test(query)) {
      return { kind: "invalid", message: "This looks like a Bible reference, but it could not be read. Try a form such as Romans 8:27." };
    }
    const phrases = [];
    const rest = normalize(query).replace(/"([^"]+)"/g, (_, phrase) => {
      const words = phrase.match(/[\p{L}\p{N}]+/gu);
      if (words) {
        phrases.push(words);
      }
      return " ";
    });
    const terms = [...new Set(rest.match(/[\p{L}\p{N}]+/gu) || [])];
    if (!terms.length && !phrases.length) {
      return { kind: "empty" };
    }
    const patterns = [...terms.map((term) => [term]), ...phrases].map(
      (words) => new RegExp(`(?<![\\p{L}\\p{N}])${words.map(escape).join("[^\\p{L}\\p{N}]+")}`, "u"),
    );
    return { kind: "words", terms, patterns };
  }

  // Position of the match in `text`, or -1 when the text does not match.
  function find(text, parsed) {
    if (parsed.kind === "reference") {
      const hit = referencesIn(text).find(
        (reference) =>
          (!parsed.book || reference.book === parsed.book) &&
          reference.start <= parsed.end &&
          parsed.start <= reference.end,
      );
      return hit ? hit.index : -1;
    }
    if (parsed.kind === "words") {
      const folded = normalize(text);
      let first = -1;
      for (const pattern of parsed.patterns) {
        const match = pattern.exec(folded);
        if (!match) {
          return -1;
        }
        first = first < 0 ? match.index : Math.min(first, match.index);
      }
      return first;
    }
    return -1;
  }

  // How many of the query's words or phrases appear in `text`.
  function score(text, parsed) {
    if (parsed.kind !== "words") {
      return 0;
    }
    const folded = normalize(text);
    return parsed.patterns.filter((pattern) => pattern.test(folded)).length;
  }

  function excerpt(text, at) {
    const start = at < 0 ? 0 : Math.max(0, at - 70);
    const end = Math.min(text.length, start + 220);
    return `${start > 0 ? "…" : ""}${text.slice(start, end)}${end < text.length ? "…" : ""}`;
  }

  window.L4CSearch = { parse, find, score, excerpt, referencesIn };
})();

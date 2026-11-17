// Shared helpers for the flagship templates. Loaded with a plain <script src>.
const Q = new URLSearchParams(location.search);
const P = (k, d) => (Q.get(k) === null || Q.get(k) === "" ? d : Q.get(k));
const N = (k, d) => parseFloat(P(k, d));

// Put a query value into an element, or hide the element when the value is missing.
function fill(id, key, fallback) {
  const el = document.getElementById(id); const v = P(key || id, fallback);
  if (!el) return null;
  if (v === undefined || v === null) { el.style.display = "none"; return null; }
  el.innerHTML = v; return el;
}

// Split "Line one|Line two" into rising lines; each line gets its own delay.
function lines(el, text, start, step) {
  el.innerHTML = "";
  text.split("|").forEach((t, i) => {
    const l = document.createElement("span"); l.className = "line a-rise"; l.style.setProperty("--d", (start + i * step).toFixed(2) + "s");
    const s = document.createElement("span"); s.innerHTML = t; l.appendChild(s); el.appendChild(l);
  });
}

// The four-part progress ticks. n = current part (1-based), 0 = none lit.
function ticks(el, n, of) {
  el.innerHTML = "";
  for (let i = 1; i <= of; i++) { const t = document.createElement("i"); if (i < n) t.className = "done"; if (i === n) t.className = "on"; el.appendChild(t); }
}

// Fade up from / down to black, as card.html does. inS / outS of 0 switch a side off.
function blackout(len, inS, outS) {
  const b = document.getElementById("black"); if (!b) return;
  const k = [];
  k.push({ opacity: inS > 0 ? 1 : 0, offset: 0 });
  if (inS > 0) k.push({ opacity: 0, offset: inS / len });
  if (outS > 0) k.push({ opacity: 0, offset: (len - outS) / len });
  k.push({ opacity: outS > 0 ? 1 : 0, offset: 1 });
  b.animate(k, { duration: len * 1000, fill: "both" });
}

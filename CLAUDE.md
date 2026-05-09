# CLAUDE.md — Engineering Standards

Project: HealthWatch — TPA Claims (single-file web app, `index.html`).
Stack: Vanilla HTML/CSS/JS + CDN libs (Chart.js, mammoth, xlsx, jszip).
This document defines the bar for any code written or modified in this repo. Apply it by default; deviate only with a stated reason.

---

## 1. Performance — non-negotiables

**Rendering / DOM**
- Batch DOM writes; read layout (`offsetWidth`, `getBoundingClientRect`) and write styles in separate phases to avoid forced reflow.
- Build subtrees off-DOM (`DocumentFragment` or detached node), then insert once. Never append in a loop to a live node.
- Prefer `textContent` over `innerHTML` for strings (faster + XSS-safe). Use `innerHTML` only with trusted, pre-escaped templates.
- Use `class` toggles over inline style writes. Animate `transform` / `opacity` only — never `top`/`left`/`width`/`height`.
- Long lists: virtualize (render only visible rows) once > 200 rows. Use `content-visibility: auto` for offscreen panels.

**JavaScript**
- O(n²) is a bug above n=100. Use `Map`/`Set` for lookups, never `array.find` in a loop.
- Cache repeated work: memoize pure functions, hoist invariants out of loops, precompute keys.
- Defer non-critical work: `requestIdleCallback` for analytics/precomputation, `requestAnimationFrame` for visual updates.
- Debounce input handlers (250ms typical), throttle scroll/resize (rAF). Use `{passive: true}` on scroll/touch listeners.
- Avoid `JSON.parse(JSON.stringify(...))` for clones — use `structuredClone`.

**Network / loading**
- Scripts: `defer` for ordered, `async` for independent. Never block parsing with sync `<script>` in `<head>`.
- Pin CDN versions (already done) and add `integrity` + `crossorigin="anonymous"` SRI hashes when adding new ones.
- Lazy-load heavy libs (xlsx, mammoth, jszip) on first use, not at page load.
- Add `loading="lazy"` and `decoding="async"` to images; specify `width`/`height` to prevent CLS.
- `<link rel="preconnect">` for any third-party origin used during initial render.

**Memory**
- Remove event listeners when their owning DOM is destroyed. Prefer event delegation on a stable parent.
- Detach Chart.js instances with `chart.destroy()` before re-rendering — they leak otherwise.
- Don't retain large parsed workbooks/docs in globals after they're consumed.

---

## 2. Code quality

- **Naming over comments.** A good name removes the need to explain. Comment only non-obvious *why*: hidden constraints, workarounds, invariants.
- **Pure functions by default.** Side effects live at the edges (DOM writes, network, storage). Pure cores are testable and cacheable.
- **Small functions, single responsibility.** If you need "and" to describe what it does, split it.
- **No dead code.** Delete unused branches, params, imports, CSS classes. Don't comment-out — `git` remembers.
- **No premature abstraction.** Three similar lines beats a wrong abstraction. Extract on the third real duplication, not the second.
- **Fail loudly in dev, gracefully in prod.** Validate at boundaries (user input, file uploads, parsed JSON). Trust internal calls.
- **Consistency with existing code wins** over personal preference. Match the existing terse-class / single-file style of `index.html` unless refactoring it intentionally.

---

## 3. Security

- **Never `innerHTML` user/file-derived data.** Use `textContent`, or sanitize with a whitelist if HTML is required.
- **Escape on output, not input.** Store raw, render escaped.
- **No `eval`, no `Function(string)`, no `setTimeout(string, ...)`** — ever.
- **CSP-friendly:** no inline event handlers (`onclick="..."`); attach via `addEventListener`. Inline `<style>`/`<script>` are acceptable in this project's single-file model but avoid `style="..."` on user-derived values.
- **File uploads** (xlsx, docx, zip): cap size, validate MIME + magic bytes, parse in a `try/catch`, never auto-execute.
- **Storage:** no PHI/PII in `localStorage`/`sessionStorage` without explicit need. TPA data is sensitive — assume HIPAA-relevant by default.
- **Dependencies:** pin versions, add SRI, prefer fewer deps over more.

---

## 4. Accessibility (WCAG 2.2 AA minimum)

- Every interactive element is reachable by `Tab` and operable by `Enter`/`Space`. If it's a `<div>` with a click handler, fix it — use `<button>`.
- Visible focus ring on all focusable elements. Don't `outline: none` without a replacement.
- Color contrast ≥ 4.5:1 for text, 3:1 for UI components and large text.
- Form fields have `<label for>` or `aria-label`. Errors are programmatically associated (`aria-describedby`).
- Tables have `<th scope>`. Charts have a text alternative (summary + data table fallback).
- Respect `prefers-reduced-motion`: disable non-essential animation.
- Modal/dialog: trap focus, restore on close, `Escape` dismisses, `aria-modal="true"`.

---

## 5. CSS

- Use the existing CSS variables (`--navy`, `--red`, `--bg`, `--r`, etc.) — don't hardcode values that have a token.
- Layout: `flex`/`grid` only. No floats. No absolute positioning unless overlaying.
- Avoid deep selectors (`>3` levels) and `!important` — both signal a structural problem.
- Prefer logical properties (`margin-inline`, `padding-block`) for future i18n.
- Mobile-first media queries, but the existing app is desktop-primary — match its breakpoints.

---

## 6. Modern JS patterns to prefer

- `const` by default, `let` when reassigned, never `var`.
- Optional chaining `?.` and nullish coalescing `??` over `&&`/`||` chains.
- `for...of` over `forEach` when you need `await`/`break`/`continue`.
- `Array.from({length: n}, (_, i) => ...)` over manual `for` for short generators.
- Top-level `async` IIFE for entrypoint async work.
- Native `fetch` + `AbortController` for cancellable requests.
- `Intl.NumberFormat` / `Intl.DateTimeFormat` for currency/dates — never hand-roll.

---

## 7. Innovation — what "better" looks like here

When extending the dashboard, raise the bar with:
- **Web Workers** for parsing (`xlsx`, `mammoth`, `jszip`) so the main thread stays responsive.
- **IndexedDB** (via a thin wrapper) for any dataset > a few hundred rows, instead of in-memory arrays.
- **`<dialog>` element** for modals — native, accessible, focus-managed for free.
- **View Transitions API** for route/panel changes when supported (progressive enhancement).
- **CSS `@container` queries** for cards that should adapt to their slot, not the viewport.
- **`Intl.Segmenter`** for any text-splitting work (search highlighting, etc.).
- **OffscreenCanvas** for heavy Chart.js redraws if they appear in profiling.

Adopt these only when they solve a real problem in the diff — not as decoration.

---

## 8. Definition of done

Before declaring a task complete:
1. **Manually exercise the change** in the browser (golden path + 1 edge case). Type-checking ≠ feature-checking.
2. **Open DevTools Performance** for any change touching rendering or large data — confirm no >50ms long tasks introduced.
3. **Tab through** any UI you added. Keyboard works, focus is visible.
4. **Check the console** — zero new warnings or errors.
5. **Diff review:** no debug logs, no dead code, no commented-out blocks, no unrelated reformatting.
6. **Commit message** explains the *why*, not the *what*.

If you cannot verify something (e.g. no browser available), say so explicitly. Don't claim success on unverified work.

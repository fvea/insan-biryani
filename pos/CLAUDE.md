# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-file, offline point-of-sale app for a night-market food stall (Insan Biryani, Gapan City). The **entire app is one file**: `Insan-Biryani-POS.html` — all HTML, CSS (inline `<style>`), and JS (inline `<script>`) in ~1870 lines. Vanilla JS, no framework, no dependencies, no build step, no backend.

## Run / develop / "deploy"

- **Run:** open `Insan-Biryani-POS.html` in any modern browser (double-click). There is no dev server, no `npm install`, no build.
- **Deploy:** copy the updated HTML file onto the tablet. That's the whole release process.
- **No test or lint tooling exists** — no `package.json`, no test runner. Verify changes by opening the file in a browser and exercising the UI. localStorage data persists between reloads, so use DevTools → Application → Local Storage to inspect/clear `ib_menu`, `ib_log`, and `ib_supplies` while testing.

Because everything is inline in one file, edit the relevant `<style>`, HTML, or `<script>` block in place — there are no modules to import or files to wire up.

## Architecture (the parts that span the file)

State lives in three module-level JS variables, each backed by a `localStorage` key, loaded once in the `init()` IIFE and re-persisted on every mutation:

| Variable   | localStorage key | Holds                         | Save via            |
|------------|------------------|-------------------------------|---------------------|
| `menuData` | `ib_menu`        | categories + items (each item's `supplies` array is its container/cutlery recipe) | `saveMenuData()`    |
| `log`      | `ib_log`         | all sales records (each entry's `suppliesUsed` snapshots what it consumed) | `localStorage.setItem('ib_log', ...)` |
| `supplies` | `ib_supplies`    | container/cutlery stock pools, matched by name across all dishes | `saveSupplies()`    |

There is **no reactive framework**. The pattern is: mutate the in-memory array → call the matching `localStorage.setItem` → call the relevant re-render function (`buildUI()`, `renderCart()`, `rebuildLog()`, `refreshStats()`/`refreshBadges()`). When changing state, you must also trigger the corresponding re-render yourself; nothing observes the data.

Key cross-cutting rules to preserve when editing:

- **`normalizeEntry()` is the load-time migration boundary.** Every `ib_log` entry passes through it on load, so legacy/partial records are upgraded to the full shape (e.g. entries with no `status` become `done`). When you add a field to a sales record, give it a default in `normalizeEntry()` so old saved data stays valid.
- **"Completed sale" has a specific definition** in `isCompletedSale()`: `status === 'done'` **AND** `payMode !== 'Unpaid'`. All stats (header total, transactions, items sold, best seller in `refreshStats()`) count only completed sales. The UI also blocks marking an order Done while it's still Unpaid. Don't conflate "done" with "counts toward stats."
- **All user-entered text is escaped at render time** via `esc()` (HTML) and `csvCell()` (CSV export). Any new place that renders names/notes/menu text into HTML or CSV must route through these — they're the XSS / CSV-injection guard.
- **Cart and menu match items by `name`.** Two items sharing a name (even across categories) collide. Keep this in mind for any item-identity logic. Supply types (`supplies`) follow the same by-name matching between a menu item's recipe and the `supplies` stock list.
- **Supply stock decrements at `logSale()` time, not when an order is marked Done.** Containers/cutlery are consumed physically when the order is packed, which happens at order time, not when payment is later collected. Each log entry snapshots what it consumed into `suppliesUsed` so `delLog()`/`saveOrderEdit()` can restore/re-apply the *original* consumption even if the recipe changes afterward — don't recompute from the live recipe when reversing an entry's effect.
- **Receipts** are built as a 58mm thermal-roll HTML template inside `printReceipt()` and printed through a hidden iframe + `window.print()`. Store header info lives in that template's `receiptContent` string, not in shared config.

The full per-function code map, exact record shape, and step-by-step recipes for common changes (add a payment mode, change "Ready In" presets, edit the default menu, etc.) are documented in **`README.md`** — consult it rather than re-deriving from the source. The default menu in the `menuData` initializer only seeds devices where `ib_menu` is unset; once saved, the stored menu wins.

## Constraints to respect

- **Keep it single-file and dependency-free.** Don't introduce a framework, bundler, npm dependency, or external script/CSS URL — offline operation on a tablet with no internet is the core requirement.
- Data is per-device, per-browser localStorage with no sync/backend. CSV export (`exportCSV()`) is the only off-device copy; "Reset Log" wipes everything irreversibly.

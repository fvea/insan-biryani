# Insan Biryani — POS

A single-file, offline point-of-sale app for a night-market food stall (Insan
Biryani, Gapan City). Built to run in a browser on a tablet with no internet,
no install, and no backend.

- **One file:** `Insan-Biryani-POS.html` — all HTML, CSS, and JS inline.
- **No dependencies, no build step, no framework.** Vanilla JS.
- **Offline-first:** all data lives in the browser's `localStorage`.

## Run it

Open `Insan-Biryani-POS.html` in any modern browser (double-click, or
load it on the tablet). That's it. To "deploy" a new version, just put the
updated HTML file on the device.

> Now under **git** — change history is tracked here, so the filename no longer
> carries a version number. On the tablet, all data lives in `localStorage`; if
> that browser keys storage per filename, verify the menu + sales still appear
> after swapping in a renamed file before deleting the old one.

## What it does

- **Menu** — items grouped by category as tabs. Tap an item to add it to the
  current order. A **Menu Manager** modal does full CRUD on categories and items.
- **Current order (cart)** — adjust quantities, see live subtotal/total.
- **Order details** — customer name, "Ready In" (5/10/20/25 min → shows the
  ready-at clock time), payment mode, optional cash tendered with change
  calculation, and notes. Tap **Log Order** to save.
- **Sales log** — table of all orders with Print, Edit, Mark Done, and Delete.
- **Receipt printing** — 58mm thermal-roll layout, printed via a hidden iframe
  + `window.print()`.
- **Export CSV** — downloads `InsanBiryani_Sales_YYYY-MM-DD.csv` (all log rows).
- **Reset Log** — clears the whole log (guarded by a confirm that reminds you to
  export first).
- **Stats** — header shows tonight's sales; cards show transactions, items sold,
  and best seller. **These only count *completed* sales** (see below).

## Data & persistence

Everything is in `localStorage` on that one device/browser. Three keys:

| Key           | Holds                                        |
|---------------|-----------------------------------------------|
| `ib_menu`     | the menu (categories + items, incl. recipes) |
| `ib_log`      | all sales records                            |
| `ib_supplies` | container/cutlery supply types + stock counts|

There is **no sync and no backend** — data is per-device, per-browser. A
different device, a different browser, or cleared site data = different/empty
data.

### Menu shape (`ib_menu`)

```js
[
  { name: "🍚 Biryani", items: [
      { name: "Chicken Biryani", price: 210, supplies: [
          { supplyName: "Large Tub", qty: 1 },
          { supplyName: "Cutlery", qty: 1 }
        ] },
      ...
  ] },
  ...
]
```

A default menu is hardcoded in `menuData` and used only when `ib_menu` is empty;
once edited, the saved version wins. Each item's `supplies` array is its
container/cutlery recipe — see **Supply tracking** below.
`normalizeMenuData()` defaults `supplies` to `[]` on load for items saved
before this field existed.

### Sales record shape (`ib_log` entries)

```js
{
  id: 1,                       // auto-increment (max existing id + 1)
  orderNo: undefined,          // optional display number; falls back to id
  customerName: "Juan",
  createdAtIso: "2026-06-13T...",
  ts: "6/13 7:42 PM",          // display stamp
  etaMinutes: 10,
  readyAtIso: "2026-06-13T...",
  items: [ { name, price, qty } ],
  total: 420,
  payMode: "Cash",             // "Unpaid" | "Cash" | "GCash" | "Maya"
  tendered: 500,               // cash only, else 0
  notes: "extra spicy",
  status: "pending",           // "pending" | "done"
  suppliesUsed: [ { supplyName: "Large Tub", qty: 1 }, ... ]
}
```

`normalizeEntry()` migrates older/partial records on load (e.g. legacy entries
with no `status` are treated as `done`, entries with no `suppliesUsed` default
to `[]`), so the shape above is always guaranteed at runtime.

### Supply tracking (`ib_supplies`) — containers & cutlery inventory

`supplies` is a flat list of stock pools, independent of the menu:
`[{ name: "Large Tub", stock: 120 }, ...]`. Each menu item's `supplies` array
(above) is its recipe — which supply types + quantities one order of that
item consumes. Supply types are shared across dishes and matched **by
name**, same convention as menu items (see "match by name" note below).

**Stock decrements at `logSale()` time, not when an order is later marked
Done.** Containers/cutlery are physically used to pack the order right when
it's placed, before payment is collected — "Done" only tracks
payment/completion (`isCompletedSale()`), not packing. To keep stock
consistent through edits and deletes, each log entry snapshots exactly what
it consumed into `suppliesUsed` (computed from the recipe *at log time*):

- `logSale()` → `consumeSupplies(suppliesUsed)`
- `delLog()` → `restoreSupplies(entry.suppliesUsed)`
- `saveOrderEdit()` → `restoreSupplies(oldSuppliesUsed)` then
  `consumeSupplies(newSuppliesUsed)` (recomputed from the current recipe)

Using the entry's own snapshot (rather than recomputing from the live
recipe) means editing a dish's recipe later doesn't retroactively change
what a past order is credited/debited for on delete.

A banner (`renderLowStockBanner()`, `#lowStockBanner`) shows whenever any
supply's stock drops below `LOW_STOCK_THRESHOLD` (50), naming every low
supply. It's outside any modal so it's visible on the main screen without
opening Supplies.

### "Completed" sale = `done` **and** paid

Stats (header total, transactions, items sold, best seller) count an order only
when `status === 'done'` **and** `payMode !== 'Unpaid'` (`isCompletedSale()`).
Pending or unpaid orders show in the log but don't move the numbers. You also
can't mark an order **Done** while it's still `Unpaid`.

## Code map (inside the `<script>`)

| Area              | Key functions                                                        |
|-------------------|----------------------------------------------------------------------|
| Init / migration  | `init()` (IIFE), `normalizeEntry()`, `normalizeMenuData()`, `normalizeSupply()` |
| Menu render       | `buildUI()`, `refreshBadges()`                                        |
| Menu CRUD         | `openMenuModal()`, `addCategory()`, `deleteCategory()`, `updateItem()`, `addNewItem()`, `deleteItem()`, `saveMenuData()` |
| Item recipes      | `renderItemRecipeChips()`, `addItemSupply()`, `removeItemSupply()` (rendered inline inside `renderMenuEditorItems()`) |
| Supply inventory  | `openSupplyModal()`, `renderSupplyList()`, `addSupply()`, `updateSupply()`, `deleteSupply()`, `adjustSupplyStock()`, `saveSupplies()`, `renderLowStockBanner()` |
| Supply consumption| `computeSuppliesUsed()`, `consumeSupplies()`, `restoreSupplies()`, `findMenuItem()`     |
| Cart              | `addItem()`, `changeQty()`, `renderCart()`, `clearCart()`            |
| Order entry       | `setReadyMinutes()`, `setMode()`, `calcChange()`, `logSale()`        |
| Log render        | `rebuildLog()`, `markDone()`, `delLog()`, `clearSalesLog()`          |
| Edit order modal  | `openOrderEditModal()`, `renderEditItems()`, `saveOrderEdit()`, `setEditMode()`, `setEditStatus()` |
| Receipt           | `printReceipt()` (builds a 58mm receipt in a hidden iframe)          |
| Export / stats    | `exportCSV()`, `refreshStats()`                                       |
| Helpers           | `esc()` (HTML-escape), `csvCell()` (CSV-escape), `orderTotal()`, time helpers (`formatClock`, `formatStamp`, `addMinutes`) |

Rendered values pass through `esc()` / `csvCell()`, so user-entered text
(names, notes, menu) is escaped — safe against broken markup / CSV injection.

## Making common changes

- **Change the starting menu:** edit the `menuData` default array. Note: it only
  applies on devices where `ib_menu` isn't set yet. To force it on a device that
  already has data, clear `ib_menu` (or use Menu Manager).
- **Add a payment mode:** add a `.pm-btn` button in both pay-mode rows (order +
  edit modal), add a `.b-<mode>` badge style, and the rest flows through
  `setMode()` / `payMode`.
- **Change "Ready In" presets:** edit the `.ready-btn` buttons (order + edit
  modal) and the `setReadyMinutes()` calls.
- **Receipt store info:** edit the header block inside `printReceipt()`'s
  `receiptContent` template.

## Known limitations / ideas

- Single device only — no multi-device sync or cloud backup. CSV export is the
  only off-device copy.
- The log never auto-resets; "tonight's sales" is just the current unreset log.
  Reset is manual and wipes everything — **export first**.
- No daily/date filtering or historical reporting inside the app (CSV is dated
  per-export, but the in-app log isn't grouped by day).
- Receipt printing depends on the browser/tablet having a working print path to
  a 58mm thermal printer.
- Cart/menu match items **by name**, so two items with the same name (even in
  different categories) would collide. Supply types are matched by name too —
  renaming a supply in the Supplies modal cascades into every item recipe
  that references it, but deleting one does not strip dangling references
  from recipes (they just stop tracking stock for that line).

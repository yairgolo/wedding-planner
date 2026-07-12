# Changelog

## 0.8.2 — Mobile navigation polish

- Removed the crowded mobile bottom navigation.
- Added a centered, independent floating Quick Add button.
- Fixed mobile sidebar scrolling on iPhone and Android.
- Added safe-area support for notched iPhones.
- Improved quick-add sheet scrolling on small screens.
- Prevented the page behind the drawer from scrolling.

## 0.6.0 — Sprint 6 Vendors & Tasks

- Added complete vendor management with contacts, contracts, payments and arrival times.
- Added vendor Excel and WhatsApp exports.
- Added task management with Kanban view, priorities, assignees and vendor links.
- Added task Excel and WhatsApp exports.
- Added vendor and task dashboard metrics.
- Added audit logs and mobile-first layouts.


## 0.5.0 — Sprint 5: Shopping & Budget

- Added full shopping management for wedding, home, clothing, gifts and general purchases.
- Added wishlist, priorities, due dates, store/product links and purchase completion flow.
- Added styled Excel exports and WhatsApp-ready text exports for shopping.
- Added budget target, expense commitments, paid amounts, balances and payment deadlines.
- Added automatic partial/paid status normalization and overdue indicators.
- Added styled Excel exports and WhatsApp-ready budget summaries.
- Connected purchased shopping items to the budget overview.
- Updated the dashboard and mobile navigation.
- Added automated tests for shopping and budget flows.

## 0.4.0 — Sprint 4: Seating

- Added visual seating management and event-day search.

## 0.3.0 — Sprint 3: Invitations

- Added invitation image, WhatsApp sharing and invitation tracking.

## 0.2.0 — Sprint 2: Guests & RSVP

- Added guests, families, RSVP and guest Excel export.

## 0.1.0 — Sprint 1: Foundation

- Added the modular Flask foundation, authentication, Docker and responsive RTL UI.

## 0.7.0 — Sprint 7

- Added gifts management, thank-you tracking and Excel/WhatsApp exports.
- Added secure document center for contracts, receipts, quotes and images.
- Added Activity Center based on the shared audit log.
- Added a recycle bin with restore support for core modules.
- Fixed invisible text on save/submit buttons, including iOS Safari.

## 0.7.1 — Vendor/Budget Sync Hotfix

- Fixed invisible labels on primary submit buttons caused by a more specific form input background rule.
- Signed vendor contracts now create and synchronize a linked budget expense automatically.
- Vendor payment, amount, due date, category, cancellation and deletion stay synchronized with budget.
- Linked budget expenses are edited from the vendor card to avoid conflicting values.

## 0.8.0 — Sprint 8 Wedding Core

- Added a central Wedding Profile used as the system source of truth.
- Added Dashboard 2.0 with readiness score, attention items and quick actions.
- Added universal search across guests, vendors, tasks, shopping, gifts and documents.
- Added a computed notification center.
- Added guest import from Excel and CSV with duplicate handling.
- Added a central export center and CSV export endpoints.
- Added new Wedding profile fields and safe SQLite upgrade logic.
- Unified form controls and submit-button styling across desktop and mobile.

## 0.8.1 — Dashboard & Profile Polish

- Added a persistent desktop command bar with global search, notifications and quick add.
- Added a reusable quick-add sheet for desktop and mobile.
- Rebuilt the dashboard cards with richer context and clickable navigation.
- Added detailed Wedding Health checks and per-module completion progress.
- Added recent activity directly to the dashboard.
- Added paid, committed and remaining budget figures.
- Improved empty states, mobile spacing, hover feedback and dashboard responsiveness.

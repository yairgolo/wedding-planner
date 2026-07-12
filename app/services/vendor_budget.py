from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from app.extensions import db
from app.models import BudgetItem, Vendor

CATEGORY_MAP = {
    "venue": "venue",
    "music": "music",
    "photography": "photography",
    "video": "photography",
    "dress": "clothing",
    "suit": "clothing",
    "beauty": "beauty",
    "rabbi": "other",
    "attraction": "attractions",
    "decor": "design",
    "transport": "transport",
    "other": "other",
}


def vendor_budget_status(vendor: Vendor) -> str:
    agreed = vendor.agreed_amount or Decimal("0")
    paid = vendor.paid_amount or Decimal("0")
    if agreed > 0 and paid >= agreed:
        return "paid"
    if paid > 0:
        return "partial"
    return "agreed"


def sync_vendor_to_budget(vendor: Vendor) -> BudgetItem | None:
    """Keep a signed vendor contract synchronized with the budget.

    Vendor is the source of truth. Unsigned, cancelled or zero-value vendors do
    not appear as active budget commitments.
    """
    item = db.session.scalar(
        db.select(BudgetItem).where(
            BudgetItem.wedding_id == vendor.wedding_id,
            BudgetItem.vendor_id == vendor.id,
        )
    )

    active_contract = bool(
        vendor.contract_signed
        and vendor.status != "cancelled"
        and (vendor.agreed_amount or Decimal("0")) > 0
        and vendor.deleted_at is None
    )

    if not active_contract:
        if item and item.deleted_at is None:
            item.deleted_at = datetime.now(UTC)
            item.status = "cancelled"
        return item

    if item is None:
        item = BudgetItem(wedding_id=vendor.wedding_id, vendor_id=vendor.id)
        db.session.add(item)

    item.deleted_at = None
    item.name = vendor.name
    item.supplier_name = vendor.name
    item.category = CATEGORY_MAP.get(vendor.category, "other")
    item.planned_amount = vendor.agreed_amount or Decimal("0")
    item.actual_amount = vendor.agreed_amount or Decimal("0")
    item.paid_amount = vendor.paid_amount or Decimal("0")
    item.status = vendor_budget_status(vendor)
    item.due_date = vendor.next_payment_date
    item.notes = "מסונכרן אוטומטית מכרטיס הספק"
    return item

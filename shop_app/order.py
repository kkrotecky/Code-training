"""Order domain objects and persistence."""

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from models import Item


# ── Paths ──────────────────────────────────────────────────────────────
ORDERS_DIR = Path(__file__).parent / "orders"


# ── Value objects ──────────────────────────────────────────────────────

@dataclass
class Customer:
    name: str
    email: str


@dataclass
class OrderItem:
    name: str
    quantity: int
    unit_cost: float
    unit_weight: float


@dataclass
class Totals:
    subtotal: float
    total_weight: float
    shipping_cost: float
    grand_total: float


@dataclass
class Order:
    order_id: str
    created_at: str
    customer: Customer
    items: List[OrderItem]
    totals: Totals

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "Order":
        """Reconstruct an Order from a dictionary (e.g. loaded from JSON)."""
        return Order(
            order_id=data["order_id"],
            created_at=data["created_at"],
            customer=Customer(**data["customer"]),
            items=[OrderItem(**i) for i in data["items"]],
            totals=Totals(**data["totals"]),
        )

    @staticmethod
    def from_basket(
        customer_name: str,
        customer_email: str,
        basket: List[str],
        items_dict: Dict[str, Item],
        total_cost: float,
        total_weight: float,
        shipping_cost: float,
    ) -> "Order":
        now = datetime.now()
        order_id = now.strftime("%Y%m%d_%H%M%S")
        created_at = now.isoformat()

        # Count item quantities
        counts: Dict[str, int] = {}
        for name in basket:
            counts[name] = counts.get(name, 0) + 1

        order_items = []
        for name, qty in counts.items():
            item = items_dict[name]
            order_items.append(
                OrderItem(
                    name=name,
                    quantity=qty,
                    unit_cost=item.cost,
                    unit_weight=item.weight,
                )
            )

        customer = Customer(name=customer_name, email=customer_email)
        totals = Totals(
            subtotal=total_cost,
            total_weight=total_weight,
            shipping_cost=shipping_cost,
            grand_total=total_cost + shipping_cost,
        )

        return Order(
            order_id=order_id,
            created_at=created_at,
            customer=customer,
            items=order_items,
            totals=totals,
        )


# ── Repository ─────────────────────────────────────────────────────────

class OrderRepository:
    """Thin persistence layer for reading/writing Order JSON files."""

    def __init__(self, directory: Path = ORDERS_DIR):
        self.directory = directory

    # ── Write ──────────────────────────────────────────────────────

    def save(self, order: Order) -> Path:
        """Serialize an Order to JSON and write it to the orders directory."""
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self.directory / f"order_{order.order_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(order.to_dict(), f, indent=2, ensure_ascii=False)
        return path

    # ── Read ───────────────────────────────────────────────────────

    def load(self, order_id: str) -> Optional[Order]:
        """Load a single order by its ID (e.g. '20260625_203726')."""
        path = self.directory / f"order_{order_id}.json"
        if not path.exists():
            return None
        return self._load_path(path)

    def load_by_path(self, path: Path) -> Order:
        """Load an order from an explicit file path."""
        return self._load_path(path)

    def list_all(self) -> List[Order]:
        """Return all orders sorted chronologically."""
        paths = sorted(self.directory.glob("order_*.json"))
        return [self._load_path(p) for p in paths]

    def find_uninvoiced(self, invoices_dir: Path) -> List[Order]:
        """Return orders that have no matching invoice PDF."""
        if not self.directory.exists():
            return []
        invoiced_ids = {
            p.stem.replace("invoice_", "")
            for p in invoices_dir.glob("invoice_*.pdf")
        } if invoices_dir.exists() else set()

        return [
            o for o in self.list_all()
            if o.order_id not in invoiced_ids
        ]

    # ── Internal ───────────────────────────────────────────────────

    def _load_path(self, path: Path) -> Order:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Order.from_dict(data)

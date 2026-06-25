import csv
from pathlib import Path
from typing import Dict

from .config import ITEMS_CSV
from .models import Item

def load_items() -> Dict[str, Item]:
    if not ITEMS_CSV.exists():
        raise FileNotFoundError(f"{ITEMS_CSV} not found – run export_items() first.")
    items = {}
    with ITEMS_CSV.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            items[row["item"]] = Item(
                name=row["item"],
                weight=float(row["weight"]),
                cost=float(row["cost"])
            )
    return items

def export_items(items: Dict[str, Item], path: Path = None) -> None:
    path = path or ITEMS_CSV
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=("item", "weight", "cost"))
        writer.writeheader()
        for item in items.values():
            writer.writerow({"item": item.name, "weight": item.weight, "cost": item.cost})
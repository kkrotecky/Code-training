from dataclasses import dataclass, field
from typing import List, Dict

@dataclass(frozen=True)
class Item:
    name: str
    weight: float
    cost: float

@dataclass
class ShoppingCart:
    items: List[Item] = field(default_factory=list)

    def add(self, item: Item) -> None:
        self.items.append(item)

    def remove(self, item: Item, all_of_them: bool = True) -> None:
        if all_of_them:
            self.items = [i for i in self.items if i.name != item.name]
        else:
            self.items.remove(item)

    @property
    def total_cost(self) -> float:
        return sum(i.cost for i in self.items)

    @property
    def total_weight(self) -> float:
        return sum(i.weight for i in self.items)

    def item_counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for i in self.items:
            counts[i.name] = counts.get(i.name, 0) + 1
        return counts

    @property
    def is_empty(self) -> bool:
        return not self.items
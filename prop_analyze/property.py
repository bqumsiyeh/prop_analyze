import json
from enum import Enum


class Utilities(Enum):
    WATER = 1
    ELECTRIC = 2
    GAS = 3
    SEWER = 4
    GARBAGE = 5

    @staticmethod
    def all() -> [Enum]:
        return [u for u in Utilities]


class Property:
    url: str = None
    street_address: str = None
    city: str = None
    state: str = None
    price: float = 0.0
    num_units: int = 0
    total_rent: float = 0.0
    annual_taxes: float = 0.0
    tax_year: str = None
    utilities_paid_by_unit: [[Utilities]] = None

    @property
    def display_name(self) -> str:
        return f'{self.street_address}, {self.city}, {self.state}'

    def to_json(self) -> str:
        return json.dumps(self, indent=4, default=lambda o: o.name if isinstance(o, Enum) else o.__dict__)


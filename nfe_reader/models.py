from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import AnyHttpUrl, BaseModel


class Config(BaseModel):
    nfe_endpoint: AnyHttpUrl
    nfe_codes: set[str]


class MetricUnit(Enum):
    KG = "Kg"
    UNIT = "un"


class NfeItem(BaseModel):
    code: str
    description: str
    quantity: Decimal
    metric_unit: MetricUnit
    unitary_price: Decimal
    total_amount: Decimal

    class Config:
        frozen = True

    def __str__(self) -> str:
        return f"{self.description} ({self.quantity} {self.metric_unit.value} * {self.unitary_price} = R${self.total_amount})"


class Nfe(BaseModel):
    title: str
    issued_date: datetime
    items: list[NfeItem] = []
    total_amount: Decimal

    def __lt__(self, other: "Nfe"):
        return self.issued_date < other.issued_date

    def __gt__(self, other: "Nfe"):
        return self.issued_date > other.issued_date

    def __str__(self):
        content = [
            f"Title: {self.title}\n" f"Date: {self.issued_date}\n",
            f"Total Amount: {self.total_amount}\n",
        ]
        for item in self.items:
            content.append(str(item))

        return "\n".join(content)

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel


class MetricUnit(Enum):
    KG = "KG"
    UNIT = "UNIT"

    def __str__(self):
        return self.value


class Address(BaseModel):
    line1: str | None
    line2: str | None
    city: str | None
    state: str | None
    country: str | None
    zip_code: str | None


class NfeItem(BaseModel):
    barcode: str
    description: str
    quantity: Decimal
    metric_unit: MetricUnit
    unitary_price: Decimal
    total_price: Decimal

    def __str__(self) -> str:
        return f"{self.description} ({self.quantity} {self.metric_unit.value} * {self.unitary_price} = R${self.total_price})"


class NfeIssuer(BaseModel):
    name: str
    national_registration_code: str
    state_registration_code: str
    address: Address


class NfeConsumer(BaseModel):
    identification: str


class PaymentType(str, Enum):
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    MONEY = "MONEY"
    STORE_CARD = "STORE_CARD"
    FOOD_VOUCHER = "FOOD_VOUCHER"


class Nfe(BaseModel):
    issuer: NfeIssuer
    consumer: NfeConsumer
    issued_date: datetime
    access_key: str
    total_amount: Decimal
    total_discounts: Decimal
    payment_type: PaymentType
    raw_html: str
    items: list[NfeItem] = []

    def __lt__(self, other: "Nfe"):
        return self.issued_date < other.issued_date

    def __gt__(self, other: "Nfe"):
        return self.issued_date > other.issued_date

    def __str__(self):
        content = [
            f"Access Key: {self.access_key}\n"
            f"Issuer: {self.issuer.name}\n"
            f"Date: {self.issued_date}\n",
            f"Consumer: {self.consumer}\n" f"Total Amount: {self.total_amount}\n",
            f"Total Discounts: {self.total_discounts}\n",
            f"Payment Type: {self.payment_type}\n",
        ]
        for item in self.items:
            content.append(str(item))

        return "\n".join(content)

    class Config:
        arbitrary_types_allowed = True

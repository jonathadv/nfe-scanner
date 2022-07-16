import re
from datetime import datetime
from decimal import Decimal

from bs4 import BeautifulSoup

from nfe_reader.models import MetricUnit, Nfe, NfeItem


def _parse_decimal(value: str) -> Decimal:
    decimal_separator = ","
    sanitized = re.sub(rf"[^\d{decimal_separator}]", "", value).replace(decimal_separator, ".")

    return Decimal(sanitized)


def _parse_unit_type(unit: str) -> MetricUnit:
    if unit == "KG":
        return MetricUnit.KG
    if unit == "UN":
        return MetricUnit.UNIT
    raise ValueError(f"value f'{unit}' is not valid unit.")


def _parse_item_description(description: str) -> str:
    return re.sub(" +", " ", description)


def _parse_issued_date(nfe_date: str) -> datetime:
    return datetime.strptime(nfe_date.strip(), "%d/%m/%Y %H:%M:%S")


def parse_nfe_items(html: BeautifulSoup) -> list[NfeItem]:
    nfe_items: list[NfeItem] = []
    items = html.select("tr[id^=Item]")

    for item in items:
        columns = item.find_all("td")
        code = columns[0].text
        description = _parse_item_description(columns[1].text)
        quantity = _parse_decimal(columns[2].text)
        metric_unit = _parse_unit_type(columns[3].text)
        unitary_price = _parse_decimal(columns[4].text)
        total_amount = _parse_decimal(columns[5].text)

        nfe_items.append(
            NfeItem(
                code=code,
                description=description,
                quantity=quantity,
                metric_unit=metric_unit,
                unitary_price=unitary_price,
                total_amount=total_amount,
            )
        )
    return nfe_items


def parse_nfe(html: BeautifulSoup) -> Nfe:
    items: list[NfeItem] = parse_nfe_items(html)

    title = html.select_one(".NFCCabecalho_SubTitulo").text
    issued_date = _parse_issued_date(
        html.select_one('td:-soup-contains("Data de Emissão:")')
        .text.split("Data de Emissão:")[1]
        .split("\n")[0]
    )
    total_amount = _parse_decimal(
        html.select('td:-soup-contains("Valor total R$")')[-1].parent.select("td")[1].text
    )

    items_total_amount = sum(item.total_amount for item in items)
    access_key = (
        html.select('td:-soup-contains("CHAVE DE ACESSO")')[-1].find_next("td").text.strip()
    )

    assert (
        total_amount == items_total_amount
    ), f"NFe total: {total_amount} != items total: {items_total_amount}"

    return Nfe(
        access_key=access_key,
        title=title,
        issued_date=issued_date,
        items=items,
        total_amount=total_amount,
    )

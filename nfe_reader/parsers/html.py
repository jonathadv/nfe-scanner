import re
from datetime import datetime
from decimal import Decimal

from bs4 import BeautifulSoup

from nfe_reader.models import Address, Nfe, NfeConsumer, NfeIssuer, NfeItem, PaymentType
from nfe_reader.parsers.base import NfeParser
from nfe_reader.parsers.common import Value


def to_bs(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


class NfeHtmlParser(NfeParser):
    def parse(self) -> Nfe:
        html = to_bs(self.nfe_response.text)
        issuer = self._parse_issuer(html)
        consumer = self._parse_consumer(html)
        issued_date = self._parse_issued_date(html)
        access_key = self._parse_access_key(html)
        total_amount = self._parse_total_amount(html)
        total_discounts = self._parse_total_discounts(html)
        payment_type = self.parse_payment_type(html)
        items = self._parse_nfe_items(html)

        return Nfe(
            issuer=issuer,
            consumer=consumer,
            issued_date=issued_date,
            access_key=Value(access_key).text,
            total_amount=total_amount,
            total_discounts=total_discounts,
            payment_type=payment_type,
            items=items,
            raw_html=str(html),
        )

    @staticmethod
    def assert_values(total_amount: Decimal, items: list[NfeItem]):
        items_total_amount = sum(item.total_amount for item in items)
        assert (
            total_amount == items_total_amount
        ), f"NFe total: {total_amount} != items total: {items_total_amount}"

    def _parse_issuer(self, html: BeautifulSoup) -> NfeIssuer:
        name = html.select_one(".NFCCabecalho_SubTitulo").text
        _, national_registration_code, _, _, state_registration_code = html.select_one(
            ".NFCCabecalho_SubTitulo1"
        ).text.split()
        address = self._parse_issuer_address(html)

        national_registration_code_patter = r"^\d\d\.\d{3}\.\d{3}\/\d{4}-\d{2}$"
        state_registration_code_pattern = r"^\d+$"

        assert re.match(
            national_registration_code_patter, national_registration_code
        ), f"National registration code '{national_registration_code}' does not match the pattern {national_registration_code_patter}"
        assert re.match(
            state_registration_code_pattern, state_registration_code
        ), f"State registration code '{state_registration_code}' does not match the pattern {state_registration_code_pattern}"

        return NfeIssuer(
            name=Value(name).text,
            national_registration_code=Value(national_registration_code).text,
            state_registration_code=Value(state_registration_code).text,
            address=address,
        )

    @staticmethod
    def _parse_consumer(html: BeautifulSoup) -> NfeConsumer:
        consumer = (
            html.select('td:-soup-contains("CONSUMIDOR")')[-1]
            .parent.parent.find_all("td")[-1]
            .text.strip()
            .replace("CPF:", "")
            .replace("\n", "")
            .strip()
        )
        return NfeConsumer(identification=Value(consumer).text)

    @staticmethod
    def _parse_issuer_address(html: BeautifulSoup) -> Address:
        street, number, neighborhood, city, state = (
            html.select(".NFCCabecalho_SubTitulo1")[-1].text.replace("\n", "").split(",")
        )
        line1 = f"{street} {number} {neighborhood}"
        line2 = None
        country = "BR"
        zip_code = None

        return Address(
            line1=Value(line1).text,
            line2=line2,
            city=Value(city).text,
            state=Value(state).text,
            country=country,
            zip_code=zip_code,
        )

    @staticmethod
    def _parse_issued_date(html: BeautifulSoup) -> datetime:
        issued_date_text = (
            html.select_one('td:-soup-contains("Data de Emissão:")')
            .text.split("Data de Emissão:")[1]
            .split("\n")[0]
        )
        return Value(issued_date_text).date

    @staticmethod
    def _parse_total_amount(html: BeautifulSoup) -> Decimal:
        text_value = (
            html.select('td:-soup-contains("Valor total R$")')[-1].parent.select("td")[1].text
        )
        return Value(text_value).decimal

    @staticmethod
    def _parse_total_discounts(html: BeautifulSoup) -> Decimal:
        text_value = (
            html.select('td:-soup-contains("Valor descontos R$")')[-1].parent.select("td")[1].text
        )
        return Value(text_value).decimal

    @staticmethod
    def parse_payment_type(html: BeautifulSoup) -> PaymentType:
        payment_type_text = Value(
            html.select('td:-soup-contains("FORMA PAGAMENTO")')[-1]
            .parent.parent.find_all("td")[-2]
            .text
        ).text

        if re.match(".*cart.o de cr.dito.*", payment_type_text, re.I):
            payment_type = PaymentType.CREDIT_CARD
        elif re.match(".*cart.o de d.bito.*", payment_type_text, re.I):
            payment_type = PaymentType.DEBIT_CARD
        elif re.match(".*dinheiro.*", payment_type_text, re.I):
            payment_type = PaymentType.MONEY
        else:
            raise ValueError(f"'{payment_type_text}' is not a valid payment type")

        return payment_type

    @staticmethod
    def _parse_access_key(html: BeautifulSoup) -> str:
        return html.select('td:-soup-contains("CHAVE DE ACESSO")')[-1].find_next("td").text

    @staticmethod
    def _parse_nfe_items(html: BeautifulSoup) -> list[NfeItem]:
        nfe_items: list[NfeItem] = []
        items = html.select("tr[id^=Item]")

        for item in items:
            columns = item.find_all("td")
            barcode = columns[0].text
            description = columns[1].text
            quantity = columns[2].text
            metric_unit = columns[3].text
            unitary_price = columns[4].text
            total_amount = columns[5].text

            nfe_items.append(
                NfeItem(
                    barcode=Value(barcode).text,
                    description=Value(description).text,
                    quantity=Value(quantity).decimal,
                    metric_unit=Value(metric_unit).metric_unit,
                    unitary_price=Value(unitary_price).decimal,
                    total_price=Value(total_amount).decimal,
                )
            )

        return nfe_items

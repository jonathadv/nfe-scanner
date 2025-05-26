import re
from datetime import datetime
from decimal import Decimal

from bs4 import BeautifulSoup

from nfe_scanner.models import (
    Address,
    Nfe,
    NfeConsumer,
    NfeIssuer,
    NfeItem,
    PaymentType,
)
from nfe_scanner.parsers.base import NfeParser
from nfe_scanner.parsers.common import Value


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
        address_text = html.select(".NFCCabecalho_SubTitulo1")[-1].text.replace("\n", "")
        # remove ", 0," from address
        address_text = re.sub(",[ ]+0,", ",", address_text)
        street, number, neighborhood, city, state = address_text.split(",")

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
        elif re.match(".*Vale Alimenta..o.*", payment_type_text, re.I):
            payment_type = PaymentType.FOOD_VOUCHER
        elif re.match("outros", payment_type_text, re.I):
            payment_type = PaymentType.OTHER
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


class NfeHtmlParser2(NfeParser):
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
        issuer_data = [i for i in html.find(class_="txtCenter").children if i.text != "\n"]
        name = issuer_data[0].text
        national_registration_code = (
            issuer_data[1].text.replace("CNPJ:", "").replace("\t", "").replace("\n", "").strip()
        )
        address = self._parse_issuer_address(issuer_data[2].text)

        national_registration_code_patter = r"^\d\d\.\d{3}\.\d{3}\/\d{4}-\d{2}$"

        assert re.match(
            national_registration_code_patter, national_registration_code
        ), f"National registration code '{national_registration_code}' does not match the pattern {national_registration_code_patter}"

        return NfeIssuer(
            name=Value(name).text,
            national_registration_code=Value(national_registration_code).text,
            state_registration_code=None,
            address=address,
        )

    @staticmethod
    def _parse_consumer(html: BeautifulSoup) -> NfeConsumer:
        consumer = (
            [i for i in html.find_all("h4") if i.text == "Consumidor"][0]
            .parent.find("strong")
            .text.strip()
            .replace("CPF:", "")
            .replace("\n", "")
            .strip()
        )
        return NfeConsumer(identification=Value(consumer).text)

    @staticmethod
    def _parse_issuer_address(address_text: str) -> Address:
        address_text = re.sub(r"[\n\t]+", " ", address_text)
        address_text = re.sub(r",\s+,", ",", address_text)
        address_values = address_text.split(",")
        if len(address_values) == 5:
            street, number, neighborhood, city, state = address_values
        elif len(address_values) == 6:
            street, number, _, neighborhood, city, state = address_values
        else:
            raise ValueError("Too much values to unpack")

        line1 = f"{street.strip()} {number.strip()} {neighborhood.strip()}"
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
        issued_date_text = [i for i in html.find_all("strong") if "Emissão:" in i.text][
            0
        ].parent.text
        match = re.search(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}", issued_date_text)
        # DD/MM/YYYY HH:mm:ss
        return Value(match[0]).date

    @staticmethod
    def _parse_total_amount(html: BeautifulSoup) -> Decimal:
        text_value = [i.text for i in html.find_all(id="linhaTotal") if "Valor a pagar" in i.text][
            0
        ]
        return Value(text_value.split(":")[1]).decimal

    @staticmethod
    def _parse_total_discounts(html: BeautifulSoup) -> Decimal:
        if match := [i.text for i in html.find_all(id="linhaTotal") if "Descontos R$" in i.text]:
            return Value(match[0].split(":")[1]).decimal
        return Value("0,00").decimal

    @staticmethod
    def parse_payment_type(html: BeautifulSoup) -> PaymentType:
        payment_type_text = re.sub(
            "\t|\n",
            " ",
            [i for i in html.find_all(id="linhaForma")[0].next_siblings if i.text != "\n"][0].text,
        ).strip()

        if re.match(".*cart.o de cr.dito.*", payment_type_text, re.I):
            payment_type = PaymentType.CREDIT_CARD
        elif re.match(".*cart.o de d.bito.*", payment_type_text, re.I):
            payment_type = PaymentType.DEBIT_CARD
        elif re.match(".*dinheiro.*", payment_type_text, re.I):
            payment_type = PaymentType.MONEY
        elif re.match(".*Vale Alimenta..o.*", payment_type_text, re.I):
            payment_type = PaymentType.FOOD_VOUCHER
        elif re.match("outros", payment_type_text, re.I):
            payment_type = PaymentType.OTHER
        else:
            raise ValueError(f"'{payment_type_text}' is not a valid payment type")

        return payment_type

    @staticmethod
    def _parse_access_key(html: BeautifulSoup) -> str:
        return html.find(class_="chave").text

    @staticmethod
    def _parse_nfe_items(html: BeautifulSoup) -> list[NfeItem]:
        nfe_items: list[NfeItem] = []
        items = html.select("tr[id^=Item]")

        for item in items:
            columns = item.find_all("td")
            description_lines = columns[0].find_all("span")

            description = description_lines[0].text.strip()
            barcode = re.search(r"\d+", description_lines[1].text.strip())[0]
            quantity = re.search(r"(\d+\.)?(\d+,)?\d+", description_lines[2].text)[0]
            metric_unit = re.search(r"</strong>\s*(.+)\s*</span>", str(description_lines[3]))[1]
            unitary_price = re.search(r"(\d+\.)?(\d+,)?\d+", description_lines[4].text)[0]
            total_amount = re.search(r"(\d+\.)?(\d+,)?\d+", columns[1].text)[0]

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

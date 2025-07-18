import logging
import re
from datetime import datetime
from decimal import Decimal

import arrow

from nfe_scanner.models import MetricUnit

LOGGER = logging.getLogger(__name__)


def parse_decimal(value: str, decimal_separator: str = ",") -> Decimal:
    sanitized = re.sub(rf"[^\d{decimal_separator}]", "", value).replace(decimal_separator, ".")
    return Decimal(sanitized)


def parse_metric_unit(unit: str) -> MetricUnit:
    normalized_unit = unit.upper()
    if normalized_unit in ("KG", "KG0001"):
        return MetricUnit.KG
    if normalized_unit not in ("UN", "UNID", "EX", "AVULSO", "POTE", "CAIXA", "FRASCO"):
        LOGGER.info(
            "Unit '%s' not recognized. Falling back to '%s'", normalized_unit, MetricUnit.UNIT
        )
    return MetricUnit.UNIT


def parse_date(value: str) -> datetime:
    return (
        arrow.get(value.strip(), "DD/MM/YYYY HH:mm:ss", tzinfo="America/Sao_Paulo")
        .to("UTC")
        .datetime
    )


def remove_extra_spaces(value: str) -> str:
    return re.sub(" +", " ", value).strip()


def remove_all_spaces(value: str) -> str:
    return re.sub(" +", "", value).strip()


class Value:
    def __init__(self, raw_value: str):
        self._raw_value = raw_value
        self._latest_version = remove_extra_spaces(raw_value)

    @property
    def date(self) -> datetime:
        return parse_date(self._latest_version)

    @property
    def decimal(self) -> Decimal:
        return parse_decimal(self._latest_version)

    @property
    def metric_unit(self) -> MetricUnit:
        return parse_metric_unit(self._latest_version)

    @property
    def no_spaces_text(self) -> str:
        return remove_all_spaces(self._latest_version)

    @property
    def text(self) -> str:
        return self._latest_version

    @property
    def raw(self):
        return self._raw_value

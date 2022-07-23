import logging
import sqlite3
from decimal import Decimal

from arrow import Arrow

from nfe_scanner.models import Nfe
from nfe_scanner.reports.sqlite import add_nfe, add_nfe_item, connect, create_tables

LOGGER = logging.getLogger(__name__)


def sqlite_report(nfes: list[Nfe]):
    conn = connect()
    create_tables(conn)
    for nfe in nfes:
        add_nfe(conn, **nfe.dict())
        for item in nfe.items:
            add_nfe_item(conn, **item.dict(), nfe_access_key=nfe.access_key)


def connect(filename: str = "nfe-reader.db"):
    connection = sqlite3.connect(filename)
    return connection


def create_tables(connection):
    cursor = connection.cursor()

    cursor.execute(
        """
    CREATE TABLE "nfe" (
        "access_key"   TEXT,
        "title"        TEXT,
        "issued_date"  TIMESTAMP,
        "total_amount" REAL,
        "raw_html"     TEXT,
        PRIMARY KEY("access_key")
    )
    """
    )

    cursor.execute(
        """
    CREATE TABLE "nfe_item" (
        "barcode"        TEXT,
        "description"    TEXT,
        "quantity"       REAL,
        "metric_unit"    TEXT,
        "unitary_price"  REAL,
        "total_amount"   REAL,
        "nfe"    TEXT,
        FOREIGN KEY("nfe") REFERENCES "nfe_item"
        UNIQUE(barcode, nfe)
    )
    """
    )


def add_nfe(
    connection,
    *,
    access_key: str,
    title: str,
    issued_date: Arrow,
    total_amount: Decimal,
    raw_html: str,
    **_,
):
    cursor = connection.cursor()
    cursor.execute(
        f"INSERT INTO nfe (access_key, title, issued_date, total_amount, raw_html) VALUES (?, ?, ?, ?, ?)",
        (access_key, title, str(issued_date), float(total_amount), raw_html),
    )
    connection.commit()


def add_nfe_item(
    connection,
    *,
    barcode: str,
    description: str,
    quantity: Decimal,
    metric_unit: str,
    unitary_price: Decimal,
    total_amount: Decimal,
    nfe_access_key,
    **_,
):
    cursor = connection.cursor()
    cursor.execute(
        f"INSERT INTO nfe_item (barcode, description, quantity, metric_unit, unitary_price, total_amount, nfe) VALUES (?, ?, ?, ?, ?, ? , ?)",
        (
            barcode,
            description,
            float(quantity),
            str(metric_unit),
            float(unitary_price),
            float(total_amount),
            nfe_access_key,
        ),
    )
    connection.commit()

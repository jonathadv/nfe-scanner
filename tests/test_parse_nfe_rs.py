import pathlib
from unittest import mock

import pytest
from bs4 import BeautifulSoup

from nfe_scanner.exceptions import NfeFetcherException
from nfe_scanner.fetchers.factory import NfeFetcherFactory
from nfe_scanner.models import Nfe
from nfe_scanner.nfe import scan_nfe


def read_html(filename: str) -> BeautifulSoup:
    parent = pathlib.Path(__file__).parent.resolve()
    with open(f"{parent}/html/{filename}", encoding="utf-8") as f:
        html = f.read()
    return html


@mock.patch(
    "requests_html.HTMLSession.get",
    return_value=mock.MagicMock(text=read_html("nfe_rs.html"), ok=True),
)
def test_parse_one_nfe(_requests_get, snapshot):
    nfe: Nfe = scan_nfe("http://" + NfeFetcherFactory.SEFAZ_RS_HOSTNAME + "/?p=1")
    snapshot.assert_match(nfe.json())


def test_access_key_missing_in_url(snapshot):

    with pytest.raises(ValueError) as exc_info:
        scan_nfe("http://" + NfeFetcherFactory.SEFAZ_RS_HOSTNAME)

    snapshot.assert_match(exc_info.value)


def test_url_not_associated_to_any_available_fetcher():
    expected_error_message = "URL is not associated to any available fetcher"

    with pytest.raises(NfeFetcherException) as exc_info:
        scan_nfe("http://host/?p=1")

    assert expected_error_message in str(exc_info.value)

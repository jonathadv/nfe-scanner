from unittest import mock

from bs4 import BeautifulSoup

from nfe_reader.models import Config, Nfe
from nfe_reader.nfe import parse_nfes


def read_html(filename: str) -> BeautifulSoup:
    with open(f"html/{filename}", encoding="utf-8") as f:
        html = f.read()
    return BeautifulSoup(html)


@mock.patch("nfe_reader.nfe.fetch_nfe_html", return_value=read_html("nfe_rs.html"))
@mock.patch(
    "nfe_reader.nfe.read_config", return_value=Config(nfe_endpoint="http://host", nfe_codes=["123"])
)
def test_parse_one_nfe(_read_config, _fetch_nfe_html, snapshot):
    nfes: list[Nfe] = parse_nfes()
    snapshot.assert_match(nfes[0].json())

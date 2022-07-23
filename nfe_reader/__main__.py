import logging
from urllib.parse import urlparse

import click

from nfe_reader.models import Nfe
from nfe_reader.nfe import scan_multiple_nfe
from nfe_reader.reports.console import console_report

LOGGER = logging.getLogger(__name__)


def validate_urls(_ctx, _param, urls: tuple[str]):
    errors: list[str] = []
    for url in urls:
        try:
            result = urlparse(url)
            assert result.scheme
            assert result.netloc
        except AssertionError:
            errors.append(f"- '{url}'")

    if errors:
        message = "\n\t" + "\n\t".join(errors)
        raise click.BadParameter(message)
    return urls


@click.command()
@click.argument("urls", nargs=-1, type=str, callback=validate_urls, required=True)
def scan(urls: tuple[str]):
    """Scan and Parse NFes"""
    nfes: list[Nfe] = scan_multiple_nfe(list(urls))
    console_report(nfes)


if __name__ == "__main__":
    scan()

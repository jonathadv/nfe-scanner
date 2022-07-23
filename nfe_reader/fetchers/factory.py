import logging

from nfe_reader.exceptions import NfeFetcherException
from nfe_reader.fetchers.base import NfeFetcher, NfeUrl
from nfe_reader.fetchers.html import NfeHtmlFetcher

LOGGER = logging.getLogger(__name__)


class NfeFetcherFactory:
    SEFAZ_RS_HOSTNAME = "www.sefaz.rs.gov.br"

    def __init__(self, nfe_url: NfeUrl):
        self.nfe_url = nfe_url

    def create(self) -> NfeFetcher:
        if self.SEFAZ_RS_HOSTNAME == self.nfe_url.host:
            return NfeHtmlFetcher(self.nfe_url)

        raise NfeFetcherException(
            f"URL is not associated to any available fetcher. url='{self.nfe_url.full}'"
        )

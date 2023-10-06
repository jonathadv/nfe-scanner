import logging

from nfe_scanner.exceptions import NfeFetcherException
from nfe_scanner.fetchers.base import NfeFetcher, NfeUrl
from nfe_scanner.fetchers.html import NfeHtmlFetcher

LOGGER = logging.getLogger(__name__)


class NfeFetcherFactory:
    SEFAZ_RS_HOSTNAME = "www.sefaz.rs.gov.br"
    SEFAZ_RS_V2_HOSTNAME = "dfe-portal.svrs.rs.gov.br"

    def __init__(self, nfe_url: NfeUrl):
        self.nfe_url = nfe_url

    def create(self) -> NfeFetcher:
        if self.nfe_url.host in (self.SEFAZ_RS_HOSTNAME, self.SEFAZ_RS_V2_HOSTNAME):
            return NfeHtmlFetcher(self.nfe_url)

        raise NfeFetcherException(
            f"URL is not associated to any available fetcher. url='{self.nfe_url.full}'"
        )

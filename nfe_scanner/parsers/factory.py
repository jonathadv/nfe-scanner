import logging

from nfe_scanner.exceptions import NfeParserException
from nfe_scanner.fetchers.base import NfeFetcherResponse, NfeFetcherResponseType, NfeUrl
from nfe_scanner.parsers.base import NfeParser
from nfe_scanner.parsers.html import NfeHtmlParser, NfeHtmlParser2

LOGGER = logging.getLogger(__name__)


class NfeParserFactory:
    nfe_response: NfeFetcherResponse
    SEFAZ_RS_HOSTNAME = "www.sefaz.rs.gov.br"
    SEFAZ_RS_V2_HOSTNAME = "dfe-portal.svrs.rs.gov.br"

    def __init__(self, url: NfeUrl, nfe_response: NfeFetcherResponse):
        self.url = url
        self.nfe_response = nfe_response

    def create(self) -> NfeParser:
        if self.nfe_response.type == NfeFetcherResponseType.HTML:
            if self.SEFAZ_RS_HOSTNAME == self.url.host:
                return NfeHtmlParser(self.nfe_response)

            if self.SEFAZ_RS_V2_HOSTNAME == self.url.host:
                return NfeHtmlParser2(self.nfe_response)

        raise NfeParserException(
            f"No parser associated with response of type {self.nfe_response.type}"
        )

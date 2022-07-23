import logging

from nfe_scanner.exceptions import NfeParserException
from nfe_scanner.fetchers.base import NfeFetcherResponse, NfeFetcherResponseType
from nfe_scanner.parsers.base import NfeParser
from nfe_scanner.parsers.html import NfeHtmlParser

LOGGER = logging.getLogger(__name__)


class NfeParserFactory:
    def __init__(self, nfe_response: NfeFetcherResponse):
        self.nfe_response = nfe_response

    def create(self) -> NfeParser:
        if self.nfe_response.type == NfeFetcherResponseType.HTML:
            return NfeHtmlParser(self.nfe_response)

        raise NfeParserException(
            f"No parser associated with response of type {self.nfe_response.type}"
        )

from nfe_reader.fetchers.base import NfeFetcher, NfeFetcherResponse, NfeUrl
from nfe_reader.fetchers.factory import NfeFetcherFactory
from nfe_reader.models import Nfe
from nfe_reader.parsers.base import NfeParser
from nfe_reader.parsers.factory import NfeParserFactory


def scan_nfe(url: str) -> Nfe:
    nfe_url = NfeUrl(url)
    fetcher: NfeFetcher = NfeFetcherFactory(nfe_url).create()
    response: NfeFetcherResponse = fetcher.fetch()
    parser: NfeParser = NfeParserFactory(response).create()

    return parser.parse()


def scan_multiple_nfe(urls: list[str]) -> list[Nfe]:
    nfes: list[Nfe] = []

    for url in urls:
        nfes.append(scan_nfe(url))

    return nfes

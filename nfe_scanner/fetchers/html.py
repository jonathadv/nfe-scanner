import logging

from requests_html import HTMLResponse, HTMLSession

from nfe_scanner.fetchers.base import (
    NfeFetcher,
    NfeFetcherResponse,
    NfeFetcherResponseType,
)

LOGGER = logging.getLogger(__name__)


class NfeHtmlParser:
    def __init__(self, raw_content: str):
        self.raw_content = raw_content


class NfeHtmlFetcher(NfeFetcher):
    def fetch(self) -> NfeFetcherResponse:
        LOGGER.info("Fetching NFe %s.", self.url)
        session = HTMLSession()
        resp: HTMLResponse = session.get(self.url.full)
        resp = self.maybe_process_iframe(session, resp)
        return NfeFetcherResponse(resp.text, NfeFetcherResponseType.HTML, resp.ok)

    @staticmethod
    def maybe_process_iframe(session: HTMLSession, resp: HTMLResponse) -> HTMLResponse:
        if iframe := resp.html.find("iframe", first=True):
            iframe_source = iframe.attrs.get("src")
            LOGGER.debug("Fetching URL from iframe '%s'", iframe_source)
            return session.get(iframe_source)
        return resp

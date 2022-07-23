import logging
from abc import ABC, abstractmethod

from nfe_reader.fetchers.base import NfeFetcherResponse
from nfe_reader.models import Nfe

LOGGER = logging.getLogger(__name__)


class NfeParser(ABC):
    def __init__(self, nfe_response: NfeFetcherResponse):
        self.nfe_response: NfeFetcherResponse = nfe_response

    @abstractmethod
    def parse(self) -> Nfe:
        pass

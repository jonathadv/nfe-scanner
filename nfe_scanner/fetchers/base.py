import logging
from abc import ABC, abstractmethod
from enum import Enum
from pydash import py_
from furl import furl

LOGGER = logging.getLogger(__name__)


class NfeUrl:
    access_key_param_names = ("p", "chNFe")

    def __init__(self, url: str):
        host, access_key = self.validate_url(url)
        self.full = url
        self.host = host
        self.access_key = access_key

    def validate_url(self, url: str) -> tuple[str, str]:
        furl_url = furl(url)
        host = furl_url.host
        access_key = (
            py_(self.access_key_param_names)
            .map(lambda key: furl_url.args.get(key))
            .filter(lambda x: x is not None)
            .find()
            .value()
        )

        try:
            assert host, f"Host {host} is invalid"
            assert access_key, (
                f"URL '{url}' is missing access key parameter. "
                f"Allowed access key parameters are {self.access_key_param_names}"
            )

        except AssertionError as err:
            raise ValueError(err) from err

        return host, access_key

    def __repr__(self):
        return f"{self.__class__.__name__}(access_key='{self.access_key}', host='{self.host}')"


class NfeFetcherResponseType(Enum):
    HTML = "html"
    JSON = "json"


class NfeFetcherResponse:
    def __init__(
        self,
        raw: str,
        response_type: NfeFetcherResponseType,
        is_success: bool = False,
        error_msg: str = None,
    ):
        self._raw = raw
        self._is_success = is_success
        self._error_msg = error_msg
        self._type = response_type

    @property
    def text(self) -> str:
        return self._raw

    @property
    def success(self) -> bool:
        return self._is_success

    @property
    def error_message(self) -> str:
        return self._error_msg

    @property
    def type(self) -> NfeFetcherResponseType:
        return self._type


class NfeFetcher(ABC):
    def __init__(self, url: NfeUrl):
        self.url: NfeUrl = url
        self.raw_content: str | None = None

    @abstractmethod
    def fetch(self) -> NfeFetcherResponse:
        pass

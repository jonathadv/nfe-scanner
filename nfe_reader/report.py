import logging

from nfe_reader.models import Nfe

LOGGER = logging.getLogger(__name__)


def print_report(nfes: list[Nfe]):
    LOGGER.info("=" * 25 + "RESULT" + "=" * 25)
    for nfe in nfes:
        LOGGER.info(nfe)
        LOGGER.info("-" * 50)

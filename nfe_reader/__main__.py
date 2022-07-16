import logging

from nfe_reader.models import Nfe
from nfe_reader.nfe import parse_nfes
from nfe_reader.report import console_report, csv_report

LOGGER = logging.getLogger(__name__)


def main():
    nfes: list[Nfe] = parse_nfes()
    console_report(nfes)
    csv_report(nfes)


if __name__ == "__main__":
    main()

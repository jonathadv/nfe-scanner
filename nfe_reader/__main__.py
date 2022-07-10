from nfe_reader.models import Nfe
from nfe_reader.nfe import parse_nfes
from nfe_reader.report import print_report

import logging
LOGGER = logging.getLogger(__name__)


def main():
    nfes: list[Nfe] = parse_nfes()
    print_report(nfes)


if __name__ == "__main__":
    main()

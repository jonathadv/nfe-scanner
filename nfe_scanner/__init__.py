import logging

CLI_FORMAT = "%(message)s"
DEBUG_FORMAT = "%(process)d-%(levelname)s-%(message)s"

logging.basicConfig(format=CLI_FORMAT, level=logging.DEBUG)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARN)

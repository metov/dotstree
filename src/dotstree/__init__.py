import logging
import coloredlogs

# Set up logging
log = logging.getLogger(__name__)
LOGFMT = "%(name)s %(filename)s:%(lineno)d %(message)s"

# Seems like coloredlogs allows ajusting level up, but not down -- so we start at DEBUG
coloredlogs.install(fmt=LOGFMT, datefmt="%H:%M:%S", level="DEBUG", logger=log)

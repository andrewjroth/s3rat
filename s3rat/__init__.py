import logging

try:
    from datetime import timezone  # Requires Python 3.2
    UTC = timezone.utc
except ImportError:
    from dateutil import tz  # Requires dateutil
    UTC = tz.tzutc()

from .comms import get_result_name, S3Comm
from . import client, server

log = logging.getLogger(__name__)

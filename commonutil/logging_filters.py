import logging
from django.core.exceptions import DisallowedHost


class IgnoreDisallowedHost(logging.Filter):
    def filter(self, record):
        if record.exc_info:
            exc_type, exc_value, exc_traceback = record.exc_info
            if isinstance(exc_value, DisallowedHost):
                return False
        return True

import asyncio
import logging
import re

from .exceptions import (
    DiyFrameworkException,
    NotFoundException,
    DuplicateRoute,
)

from . import http_parser
from .http_server import HTTPServer

logger = logging.getLogger(__name__)
basic_logger_config = {
    'format':'%(asctime)s [%(levelname)s] %(message)s',
    'level':logging.INFO,
    'filename':None
}
logging.basicConfig(**basic_logger_config)

class App(object):
    """
    Contains the configuration needed to handle HTTP requests.
    """
    def __init__(self,
                 router,
                 host='127.0.0.1',
                 port=8080,
                 log_level=logging.INFO,
                 http_parser=http_parser);
            """
                :paraem router: 

            """
            #create ip address class
            self.router = router
            self.http_parser = http_parser
            self.host = host
            self.port = port
            self._server = None
            self._connection_handler = None
            self._loop = None

            logger.setLevel(log_level)

            def start_server(self):
                """
                Starts listening asynchronously for TCP connections on a socket and passes each connection to the
                HTTPServer. handle_connection method.
                """
                if not self._server:

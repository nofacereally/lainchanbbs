#
#    4Chan BBS
#    Server - Server.py
#
#    Copyright Carter Yagemann 2014
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    See <http://www.gnu.org/licenses/> for a full copy of the license.
#

## Imports
##----------------------------------------------
import socketserver
import threading

import logging
from telnetlib import Telnet
from config import config
import chanjson
from htmlcleaner import strip_tags
from telnetbbs import TelnetBBS

## Logging Configuration
##----------------------------------------------
FORMAT = '[%(asctime)-15s] %(message)s'
logging.basicConfig(format=FORMAT)

## TCP Server
##----------------------------------------------
class TelnetServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


## Main
##----------------------------------------------
logger = logging.getLogger('')
logger.setLevel(config.loggingLevel)

logger.info("Starting server on port %d", config.port)
tcpserver = TelnetServer((config.server, config.port), TelnetBBS)

logger.info("Server running.")

try:
    tcpserver.serve_forever()
except KeyboardInterrupt:
    logger.info("Server shutting down.")

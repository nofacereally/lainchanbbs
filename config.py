#
#    4Chan BBS
#    Configuration - config.py
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

import logging


class config:

    welcome_banner = None

    # Stock Messages
    welcome_message = '''\x1b[32;1m
d888888888888888PY88P         Y88Y' `YP"    Y"    "YP"88888888888888PY8
888888888888888P  Y8           `"`        _.ooo888oo. 8P88888888888'  "
888888888888"" _.oo88888oo.             `" ,--- __      `8888888888
88888888888P  "     __ ---.                 oP"88887o.   :Y88888P'8.
Y8888888888b     .od888"o.`                    Y88P  Y   :. '"Y'_88b
 ""88888888K    Y. Y88P                      -._____;    888Y _`"Y88.
   "88888l  l    `.___..-'                               88',d88:d88'
    Y8P"Y8.  l                                           : 88888:888p
     "   Y8b.                                            :d88888:8888.
          `8888b                                        ,8888888:88888b
           Y8888b                                      d88888888:888888"
           dbd888b.                ` '                d888888888:888P'
          d888888888o_             .--             _p88888888888;P'
         `YP"Y888888888b.                          Y8888P"Y8888
                ''"YP"""YP=p._             \x1b[31;1m 8""""8   8""""8   8""""8\x1b[32;1m
e     eeeee e  eeeee eeee e   e eeeee eeeee\x1b[31;1m 8    8   8    8   8     \x1b[32;1m
8     8   8 8  8   8 8  8 8   8 8   8 8   8\x1b[31;1m 8eeee8ee 8eeee8ee 8eeeee\x1b[32;1m
8e    8eee8 8e 8e  8 8e   8eee8 8eee8 8e  8\x1b[31;1m 88     8 88     8     88\x1b[32;1m
88    88  8 88 88  8 88   88  8 88  8 88  8\x1b[31;1m 88     8 88     8 e   88\x1b[32;1m
88eee 88  8 88 88  8 88e8 88  8 88  8 88  8\x1b[31;1m 88eeeee8 88eeeee8 8eee88\x1b[32;1m
                             "Partially works!"
\x1b[0m
'''

    welcome_help_text = '''
For help, type help. For additional help, try help <command>.
'''
    prompt = "lainchanbbs> "
    continue_prompt = "Press any key to continue..."

    # Server Configuration
    server = "0.0.0.0"
    port = 5000
    loggingLevel = logging.INFO

    # OFFLINE DEVELOPMENT MODE
    offline_mode = False

    # Board list
    board_list = './data/boards.json'

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

    welcome_banner = "https://lainchan.org/static/lain_banner1.png"

    # Stock Messages
    welcome_message = '''
                                                                      
  _               _____ _   _  _____ _    _          _   _ ____  ____   _____ 
 | |        /\   |_   _| \ | |/ ____| |  | |   /\   | \ | |  _ \|  _ \ / ____|
 | |       /  \    | | |  \| | |    | |__| |  /  \  |  \| | |_) | |_) | (___  
 | |      / /\ \   | | | . ` | |    |  __  | / /\ \ | . ` |  _ <|  _ < \___ \ 
 | |____ / ____ \ _| |_| |\  | |____| |  | |/ ____ \| |\  | |_) | |_) |____) |
 |______/_/    \_\_____|_| \_|\_____|_|  |_/_/    \_\_| \_|____/|____/|_____/ 
                                                                      
'''

    welcome_help_text = '''
New to the server? Here's a quick guide:
       lb                      - List all the available boards
       lt <boardID>            - List the threads for a board
       ei/di                   - Enable/Disable the showing of images

If you need additional help or examples, try help <command>.
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

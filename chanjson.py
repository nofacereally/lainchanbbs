#
#    4Chan BBS
#    Chan JSON - chanjson.py
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

import json
import requests
import ascii_image
import logging
from config import config


class ChanServer:
    def __init__(self):
        self.base_url = 'https://lainchan.org'
        self.logger = logging.getLogger('')
        self.boards = None
        self.cache = {}

    # Gets all the boards
    def getBoards(self):
        if self.boards is not None:
            return self.boards

        if len(config.board_list) > 0:
            logging.info(f"File {config.board_list} used for board list.")

            with open(config.board_list, 'r') as f:
                boards_list = json.loads(f.read())
        else:
            response = requests.get(url=f'{self.base_url}/boards.json')
            boards_list = json.loads(response.text)

        self.boards = boards_list

        return self.boards

    # Get a page of threads from a board
    def getThreads(self, board, page):
        data = ''

        try:
            api_url = f"{self.base_url}/{str(board)}/{str(page)}.json"

            data = self.queryApi(api_url)
        except Exception:
            self.logger.error('Error: Failed to process getThreads()')

        return data

    # Get posts for a particular thread
    def getReplies(self, board, thread):
        data = ''

        try:
            api_url = f"{self.base_url}/{str(board)}/res/{str(thread)}.json"

            data = self.queryApi(api_url)
        except Exception:
            self.logger.error('Error: Failed to process getReplies()')

        return data

    # Get thumbnail for a post
    def getThumbNail(self, board, imgID, ext):
        img = 'No Image'

        try:
            url = f"{self.base_url}/{str(board)}/thumb/{str(imgID)}{ext}"

            file = ascii_image.open_url(url)

            img = ascii_image.convert_image(file, 60, 40)
        except Exception:
            request = str(board) + ' => ' + str(imgID)
            self.logger.error('Error: Failed to get image for %s', request)

        return img

    def queryApi(self, api_url):
        """Query the given API URL and cache the results with no TTL

        :param str api_url
            The API URL to query. Responses are expected to be JSON.
        :returns
            The decoded JSON from the API call.
        :rtype
            dict
        """
        if api_url in self.cache.keys():
            return self.cache[api_url]

        response = requests.get(url=api_url)

        if response.status_code != 200:
            raise Exception(f'API query failed: {api_url}')

        data = json.loads(response.text)

        self.cache[api_url] = data

        return self.cache[api_url]

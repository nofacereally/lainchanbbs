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
from cachetools import cached, TTLCache, LRUCache


class ChanServer:
    def __init__(self):
        self.base_url = 'https://lainchan.org'
        self.logger = logging.getLogger('')

    @cached(cache=TTLCache(maxsize=1024, ttl=60))
    def getBoards(self):
        # Gets all the boards
        if len(config.board_list) > 0:
            logging.info(f"File {config.board_list} used for board list.")

            with open(config.board_list, 'r') as f:
                boards_list = json.loads(f.read())
        else:
            response = requests.get(url=f'{self.base_url}/boards.json')
            boards_list = json.loads(response.text)

        self.boards = boards_list

        return self.boards

    def getThreads(self, board, page):
        # Get a page of threads from a board
        data = ''

        try:
            api_url = f"{self.base_url}/{str(board)}/{str(page)}.json"

            data = self.queryApi(api_url)
        except Exception:
            self.logger.error('Error: Failed to process getThreads()')

        return data

    def getReplies(self, board, thread):
        # Get posts for a particular thread
        data = ''

        try:
            api_url = f"{self.base_url}/{str(board)}/res/{str(thread)}.json"

            data = self.queryApi(api_url)
        except Exception:
            self.logger.error('Error: Failed to process getReplies()')

        return data

    def getThumbNail(self, board, imgID, ext, tn_w, tn_h, w=80, h=24, ar=0.61):
        # Get thumbnail for a post
        url = self.getThumbNailURL(board, imgID, ext, tn_w, tn_h)

        if self.isSupportedExt(ext):
            return self.getAndConvertImage(url, w, h, ar)
        else:
            return url

    @cached(cache=LRUCache(maxsize=100))
    def getAndConvertImage(self, url, width=80, height=24, ar=0.61):
        img = 'No Image'

        try:
            file = ascii_image.open_url(url)

            img = ascii_image.convert_image(file, width, height, ar)
        except Exception as e:
            print(e)
            self.logger.error(f'Error: Failed to get image {url}')

        return img

    def getThumbNailURL(self, board, imgID, ext, tn_w, tn_h):

        # Could be a spoiler, link to a different image.
        if tn_h == 128 and tn_w == 128:
            return f"{self.base_url}/{str(board)}/src/{str(imgID)}{ext}"
        else:
            return f"{self.base_url}/{str(board)}/thumb/{str(imgID)}{ext}"

    @cached(cache=TTLCache(maxsize=1024, ttl=120))
    def queryApi(self, api_url):
        """Query the given API URL and cache the results with TTL

        :param str api_url
            The API URL to query. Responses are expected to be JSON.
        :returns
            The decoded JSON from the API call.
        :rtype
            dict
        """
        response = requests.get(url=api_url)

        if response.status_code != 200:
            raise Exception(f'API query failed: {api_url}')

        data = json.loads(response.text)

        return data

    def isSupportedExt(self, ext):
        extensions = [
            '.png',
            '.jpg',
            '.jpeg',
            '.gif',
        ]

        return ext.lower() in extensions

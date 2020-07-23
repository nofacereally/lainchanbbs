import socketserver
# import threading

import logging
from config import config
import chanjson
from htmlcleaner import strip_tags

from colors import *
from formatter import PostFormatter

from enum import Enum
import time


class BBSState(Enum):
    WELCOME = 1
    BASE = 2
    THREADS = 3
    REPLIES = 4
    BYE = 5


class TelnetBBS(socketserver.BaseRequestHandler):
    chan_server = chanjson.ChanServer()

    def setup(self):
        self.state = BBSState.WELCOME

        self.current_board = ""
        self.current_page = 0
        self.current_thread = 0
        self.current_post = 0
        self.current_prompt = config.prompt

        self.showImages = False

        self.session_start()
        self.writeln(config.welcome_message)
        self.current_prompt = config.continue_prompt
        self.prompt()

    def handle(self):
        while True:
            if self.state == BBSState.WELCOME:
                self.state = BBSState.BASE
                self.current_prompt = config.prompt
                continue

            command = str(self.request.recv(1024).strip(), 'utf-8').lower()

            splitted = command.split(" ")
            params = []

            if len(splitted) > 1:
                params = splitted[1:]

            if self.state == BBSState.BASE:
                if command == 'lb':
                    self.command_listboards()
                elif command.startswith('lt '):
                    self.command_listthreads(params)
                elif command == 'ei':
                    self.showImages = True
                    self.writeln("Images enabled.")
                    self.writeln("")
                elif command == 'di':
                    self.showImages = False
                    self.writeln("Images disabled.")
                    self.writeln("")
                elif command == 'bye':
                    return
                elif command == '':
                    pass
                else:
                    self.writeln("Command not recognized.")
            elif self.state == BBSState.THREADS:
                if (command == 'q'):
                    self.writeln('Exiting thread viewer.')
                    self.writeln('')

                    self.state = BBSState.BASE
                    self.current_prompt = config.prompt
                elif (command == ''):
                    self.current_page = self.current_page + 1
                    self.print_current_page()
                elif (command == 'p'):
                    self.current_page = self.current_page - 1
                    self.print_current_page()
                else:
                    self.current_thread = int(command)
                    self.state = BBSState.REPLIES
                    self.print_current_reply()

            elif self.state == BBSState.REPLIES:
                if command == 'q':
                    self.state = BBSState.THREADS
                    self.current_post = 0
                    self.print_current_page()
                elif (command == ''):
                    self.current_post = self.current_post + 1
                    self.print_current_reply()

            self.prompt()

    def finish(self):
        self.writeln("Disconnecting from BBS...")
        self.session_end()

    def writeresponse(self, s):
        byted = bytes(s, 'utf-8')
        self.request.sendall(byted)

    def writeln(self, s):
        self.writeresponse(f"{s}\n\r")

    def writeerror(self, s):
        self.writeln(color(f"{s}", fg="red", style="bold"))

    def prompt(self):
        self.readline(self.current_prompt)

    def readline(self, prompt=config.prompt):
        self.writeresponse(prompt)

    def session_start(self):
        logger = logging.getLogger('')
        logger.info('Connections: A user has connected.')
        if (config.offline_mode):
            self.writeln(red('\n** OFFLINE MODE IS CURRENTLY ENABLED! **\n'))

    def session_end(self):
        logger = logging.getLogger('')
        logger.info('Connections: A user has disconnected.')

    def command_listboards(self):
        '''
        Lists available boards.
        '''
        data = self.chan_server.getBoards()

        self.writeln(blue('*--------------------------------*'))

        for board in data['boards']:
            self.writeresponse(color(board['board'], fg='white', style='bold'))
            self.writeresponse(' - ')
            self.writeresponse(color(board['title'], fg='green'))
            self.writeln('')

        self.writeln(blue('*--------------------------------*'))

    def command_listthreads(self, params):
        '''<boardID>
        Lists the threads in a given board.
        Lists the threads in a given board.
        Use listboards command to get the board's ID.
        Example: 'lt a' will list all the treads on /a/.
        '''
        if (len(params) == 0):
            self.writeerror('Missing argument.')
            return


        try:
            boards = self.chan_server.getBoards()['boards']

            for board in boards:
                if (params[0] == board['board']):
                    board_info = board

            pages = board_info['pages']
        except:
            logger = logging.getLogger('')
            logger.error('Error: Failed to get board info: %s', str(params[0]))
            self.writeerror('Communication error or invalid board ID...')
            return

        self.current_board = params[0]
        self.print_current_page()

    def command_getreplies(self):
        '''<boardID> <threadID>
        Lists the replies for a thread.
        Lists the replies for a thread.
        Use listboards and listthreads to get the IDs.
        Example: 'gr a 1' will list the replies for the thread on /a/ with ID 1
        '''

    def command_enableimages(self, params):
        '''
        Enables showing images in posts.

        '''
        self.writeln("Images have been enabled.")
        self.showImages = True

    def command_disableimages(self, params):
        '''
        Disables showing images in posts.

        '''
        self.writeln("Images have been disabled.")
        self.showImages = False

    def print_current_page(self):
        thread_result = self.chan_server.getThreads(self.current_board, self.current_page)

        if isinstance(thread_result, str):
            self.writeln('End of threads.')
            self.writeln('')
            return

        threads = thread_result['threads']

        self.writeln(' ')
        self.writeln(blue('*-------------------------------*'))

        for thread in threads:
            op = thread['posts'][0]

            header = str(op['no']) + ' - ' + red(str(op['name']))

            if 'sub' in op.keys():
                header = header + ' - ' + str(op['sub'])

            header = header + ', replies: ' + str(op['replies'])

            self.writeln(header)

#            if 'tim' in op.keys() and self.showImages:
#                self.writeln(' ')
#                img = self.chan_server.getThumbNail(board, op['tim'], ".png")
#
#                if img:
#                    self.writeln(img)
#                else:
#                    self.writeln('<<IMG ERROR>>')
#
#                self.writeln(' ')
#
#            if 'com' in op.keys():
#                try:
#                    self.writeln(strip_tags(op['com']))
#                except:
#                    pass

        self.writeln(blue('*-------------------------------*'))
        self.writeln(f'Page {self.current_page + 1}')
        self.writeln('')

        self.current_prompt = 'Enter - Next Page | p - Prev Page | Thread Number - Read Thread | q - Quit: '
        self.state = BBSState.THREADS

    def print_current_reply(self):
        pf = PostFormatter()

        try:
            posts = self.chan_server.getReplies(self.current_board, self.current_thread)['posts']
        except:
            self.writeerror('Communication error or invalid board ID...')
            return

        if self.current_post >= len(posts):
            self.writeln("End of posts.")
            self.writeln('')

            self.current_post = 0
            return

        post = posts[self.current_post]

        self.writeln(' ')
        self.writeln(blue('*-------------------------------*'))

        header = str(post['no']) + ' - ' + red(str(post['name']))

        if 'time' in post.keys():
            epoch_ts = time.gmtime(int(post['time']))
            formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", epoch_ts)

            header = header + " - " + formatted_time

        try:
            self.writeln(header)
        except:
            pass

        if 'tim' in post.keys() and self.showImages:
            self.writeln(' ')
            img = self.chan_server.getThumbNail(self.current_board, post['tim'], ".png")

            if img:
                self.writeln(img)
            else:
                self.writeln('<<IMAGE ERROR>>')

            self.writeln(' ')

        if 'com' in post.keys():
            self.writeln(pf.format_post(strip_tags(post['com'])))

        self.writeln(blue('*-------------------------------*'))

        self.current_prompt = 'Enter - Next Post | q - Quit: '

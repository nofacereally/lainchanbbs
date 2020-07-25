import threading
import time
import select

from config import config
import chanjson
from colors import color
from formatter import PostFormatter
from htmlcleaner import strip_tags

import logging

from telnetsrv.telnetsrvlib import TelnetHandlerBase, command

from enum import Enum


class BBSState(Enum):
    WELCOME = 1
    BASE = 2
    THREADS = 3
    REPLIES = 4
    BYE = 5


class TelnetBBS(TelnetHandlerBase):
    WELCOME = config.welcome_message
    PROMPT = config.prompt
    CONTINUE_PROMPT = config.continue_prompt

    chan_server = chanjson.ChanServer()
    formatter = PostFormatter()
    logger = logging.getLogger('')

    "A telnet server handler using Threading"
    def __init__(self, request, client_address, server):
        # BBS setup
        self.current_board = ""
        self.current_page = 0
        self.current_thread = 0
        self.current_post = 0
        self.showImages = False
        self.encoding = "latin-1"

        # This is the cooked input stream (list of charcodes)
        self.cookedq = []

        # Create the locks for handing the input/output queues
        self.IQUEUELOCK = threading.Lock()
        self.OQUEUELOCK = threading.Lock()

        # Call the base class init method
        TelnetHandlerBase.__init__(self, request, client_address, server)

    def setup(self):
        '''Called after instantiation'''
        TelnetHandlerBase.setup(self)
        # Spawn a thread to handle socket input
        self.thread_ic = threading.Thread(target=self.inputcooker)
        self.thread_ic.setDaemon(True)
        self.thread_ic.start()
        # Note that inputcooker exits on EOF

        # Sleep for 0.5 second to allow options negotiation
        time.sleep(0.5)

        self.encoding = "utf-8"

    def finish(self):
        '''Called as the session is ending'''
        TelnetHandlerBase.finish(self)
        # Might want to ensure the thread_ic is dead

    # -- Threaded input handling functions --
    def getc(self, block=True):
        """Return one character from the input queue"""
        if not block:
            if not len(self.cookedq):
                return ''
        while not len(self.cookedq):
            time.sleep(0.05)
        self.IQUEUELOCK.acquire()
        ret = self.cookedq[0]
        self.cookedq = self.cookedq[1:]
        self.IQUEUELOCK.release()
        return ret

    def inputcooker_socket_ready(self):
        """Indicate that the socket is ready to be read"""
        return select.select([self.sock.fileno()], [], [], 0) != ([], [], [])

    def inputcooker_store_queue(self, char):
        """Put the cooked data in the input queue (with locking)"""
        self.IQUEUELOCK.acquire()
        if type(char) in [type(()), type([]), type("")]:
            for v in char:
                self.cookedq.append(v)
        else:
            self.cookedq.append(char)
        self.IQUEUELOCK.release()

    # -- Threaded output handling functions --
    def writemessage(self, text):
        """Put data in output queue, rebuild the prompt and entered data"""
        # Need to grab the input queue lock to ensure the entered data doesn't change
        # before we're done rebuilding it.
        # Note that writemessage will eventually call writecooked
        self.IQUEUELOCK.acquire()
        TelnetHandlerBase.writemessage(self, text)
        self.IQUEUELOCK.release()

    def writecooked(self, text, encoding='latin-1'):
        """Put data directly into the output queue"""
        # Ensure this is the only thread writing
        self.OQUEUELOCK.acquire()
        TelnetHandlerBase.writecooked(self, text, self.encoding)
        self.OQUEUELOCK.release()

    def writehline(self):
        self.writeline(color('*-------------------------------*', fg='blue'))

    @command(['listboards', 'lb'])
    def command_listboards(self, params):
        data = self.chan_server.getBoards()

        self.writehline()

        for board in data['boards']:
            self.writeline(self.formatter.format_board_title(board))

        self.writehline()

    @command(['listthreads', 'lt'])
    def command_listthreads(self, params):
        self.current_thread = 0

        if (len(params) == 0):
            self.writeerror('Missing argument.')
            return

        self.current_board = params[0]

        print_page = True

        while True:
            if print_page:
                self.print_current_page()

            command = self.readline(prompt='Enter - Next Page | p - Prev Page | Thread Number - Read Thread | q - Quit: ')

            print_page = True

            if command.lower() == '':
                self.current_page = self.current_page + 1
            elif command.lower() == 'p':
                self.current_page = self.current_page - 1

                if self.current_page < 0:
                    self.writeerror("No more threads.")
                    self.writeerror("")
                    self.current_page = 0
                    print_page = False

            elif command.lower() == 'q':
                self.PROMPT = config.prompt
                break
            else:
                try:
                    self.current_thread = int(command)
                    self.read_replies()
                except ValueError:
                    self.writeerror("Invalid thead number.")
                    self.writeline("")
                    print_page = False

    def read_replies(self):
        self.current_post = 0

        try:
            posts = self.chan_server.getReplies(self.current_board, self.current_thread)['posts']
        except Exception:
            self.writeerror('Communication error or invalid board ID...')
            return

        show_post = True

        while True:
            error = False

            if self.current_post < 0:
                self.current_post = 0
                error = True

            if self.current_post >= len(posts):
                self.current_post = len(posts) - 1
                error = True

            if error:
                self.writeerror("No more posts.")
                self.writeerror("")
                continue

            if show_post:
                post = posts[self.current_post]

                self.writeline(' ')
                self.writehline()

                header = self.formatter.format_post_header(post)

                try:
                    self.writeline(header)
                except Exception:
                    pass

                if 'tim' in post.keys():
                    if self.showImages:
                        self.writeline(' ')
                        img = self.chan_server.getThumbNail(self.current_board, post['tim'], '.png')

                        if img:
                            self.writeline(img)
                        else:
                            self.writeline('<<IMAGE ERROR>>')
                    else:
                        self.writeline(self.chan_server.getThumbNailURL(self.current_board, post['tim'], '.png'))

                    self.writeline(' ')

                if 'com' in post.keys():
                    self.writeline(self.formatter.format_post(strip_tags(post['com'])))

                self.writehline()

            show_post = True

            command = self.readline(prompt='Enter - Next Post | p - Prev Post | q - Quit: ')

            if command.lower() == 'q':
                break
            elif command.lower() == '':
                self.current_post = self.current_post + 1

                if self.current_post >= len(posts):
                    show_post = False
            elif command.lower() == 'p':
                self.current_post = self.current_post - 1

                if self.current_post < 0:
                    show_post = False

    def print_current_page(self):
        thread_result = self.chan_server.getThreads(self.current_board, self.current_page)

        if isinstance(thread_result, str):
            self.writeline('End of threads.')
            self.writeline('')
            return

        threads = thread_result['threads']

        self.writeline(' ')
        self.writehline()

        for thread in threads:
            op = thread['posts'][0]

            header = self.formatter.format_post_header(op)

            header = header + ', replies: ' + str(op['replies'])

            self.writeline(header)

        self.writehline()
        self.writeline(f'Page {self.current_page + 1}')
        self.writeline('')

    @command(['enableimages', 'ei'])
    def command_enableimages(self, params):
        '''
        Enables showing images in posts.

        '''
        self.writeline("Images have been enabled.")
        self.writeline("")

        self.showImages = True

    @command(['disableimages', 'di'])
    def command_disableimages(self, params):
        '''
        Disables showing images in posts.

        '''
        self.writeline("Images have been disabled.")
        self.writeline("")

        self.showImages = False

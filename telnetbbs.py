import threading
import time
import select

from config import config
import chanjson
from formatter import PostFormatter
from colors import color

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
        self.aspect_ratio = 0.61

        self.WELCOME = self.WELCOME + config.welcome_help_text

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
        self.writeline(self.formatter.get_hline('blue'))

    @command('listboards')
    @command('lb')
    def command_listboards(self, params):
        '''
        List the boards on lainchan.
        This command lists all known boards on lainchan that have a compatible API.
        '''
        data = self.chan_server.getBoards()

        self.writehline()

        for board in data['boards']:
            self.writeline(self.formatter.format_board_title(board))

        self.writehline()

    @command('listthreads')
    @command('lt')
    def command_listthreads(self, params):
        '''<board name> <page>
        Lists the threads on a board.
        This command lists the page of threads on a board. Omitting page will start at page 1.
        '''
        self.current_thread = 0

        if (len(params) == 0):
            self.writeerror('Missing argument.')
            self.writeerror('')
            return

        board = params[0]

        if not self.is_valid_board(board):
            self.writeerror('That board is not known.')
            self.writeerror('')
            return

        self.current_board = params[0]

        if (len(params) > 1):
            try:
                self.current_page = int(params[1]) - 1
            except ValueError:
                self.writeerror("Invalid page number.")
                self.writeerror("")
                return

        print_page = True

        while True:
            if print_page:
                self.print_current_page()

            command = self.readline(prompt='(enter) next, (p)rev, # read, (q)uit: ')

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

    def read_replies(self, params=None):
        self.current_post = 0

        if params is not None:
            if len(params) < 2:
                self.writeerror("Board name and thread number are required.")
                self.writeerror("")
                return

            board = params[0]

            if not self.is_valid_board(board):
                self.writeerror("That board is not known.")
                self.writeerror("")
                return

            self.current_board = board

            try:
                self.current_thread = int(params[1])
            except ValueError:
                self.writeerror("Invalid thread number.")
                self.writeerror("")
                return

        try:
            posts = self.chan_server.getReplies(self.current_board, self.current_thread)['posts']
        except Exception:
            self.writeerror('Communication error or invalid board and/or thread number.')
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

                self.writeresponse(
                    self.formatter.format_post(
                        post,
                        self.current_board,
                        self.chan_server,
                        self.showImages,
                        'blue',
                        None,
                        self.WIDTH
                    )
                )

            show_post = True

            command = self.readline(prompt='(enter) next, (p)rev, (# #..) view threads, (f)irst, (l)ast, (i)mage, (q)uit: ')

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
            elif command.lower() == 'f':
                self.current_post = 0
            elif command.lower() == 'l':
                self.current_post = len(posts) - 1
            elif command.lower() == 'i':
                if 'tim' in post.keys():
                    self.writeresponse(
                        self.formatter.format_post_image(
                            post,
                            self.current_board,
                            self.chan_server,
                            self.WIDTH,
                            self.HEIGHT,
                            self.aspect_ratio
                        )
                    )
                else:
                    self.writeline("There is no image on this post.")

                self.writeresponse("")

                show_post = False
            else:
                try:
                    post_requests = command.split(' ')

                    for req in post_requests:
                        post_request = int(req)

                        try:
                            g = (i for i, e in enumerate(posts) if e['no'] == post_request)
                            post_index = next(g)

                            self.writeresponse(
                                self.formatter.format_post(
                                    posts[post_index],
                                    self.current_board,
                                    self.chan_server,
                                    self.showImages,
                                    'yellow',
                                    None,
                                    self.WIDTH
                                )
                            )
                        except Exception:
                            self.writeerror("Post number not found.")
                            self.writeerror("")
                            show_post = False
                            break

                except ValueError:
                    self.writeerror("Invalid post number.")
                    self.writeerror("")
                    show_post = False

    def print_current_page(self):
        try:
            thread_result = self.chan_server.getThreads(self.current_board, self.current_page)
        except Exception:
            self.writeerror('Communication error or invalid board and/or thread number.')
            self.writeerror("")
            return

        if isinstance(thread_result, str):
            self.writeline('No more threads or bad thread number.')
            self.writeline('')
            return

        threads = thread_result['threads']

        self.writeline(' ')
        self.writehline()

        for thread in threads:
            op = thread['posts'][0]

            header = self.formatter.format_post_header(op)

            header = header + ' {}{}{}{}'.format(
                color("r", fg='cyan'),
                color("[", fg='blue', style='bold'),
                color(op['replies'], fg='yellow', style='bold'),
                color("]", fg='blue', style='bold')
            )

            self.writeline(header)

        self.writehline()
        self.writeline(f'Page {self.current_page + 1}')
        self.writeline('')

    @command('enableimages')
    @command('ei')
    def command_enableimages(self, params):
        '''
        Enables showing images in posts globally.
        Turns on showing images in threads globally.

        '''
        self.writeline("Images have been enabled.")
        self.writeline("")

        self.showImages = True

    @command('disableimages')
    @command('di')
    def command_disableimages(self, params):
        '''
        Disables showing images in posts.
        Turns off showing images in threads globally. You can still see them with 'i'.

        '''
        self.writeline("Images have been disabled.")
        self.writeline("")

        self.showImages = False

    @command('ar')
    def command_aspectratio(self, params):
        '''<number>
        Displays or sets the font aspect ratio.
        Change this to match your font aspect ratio so image rendering looks better.
        '''
        if len(params) == 0:
            self.writeresponse(f"Current aspect ratio: {self.aspect_ratio}")
            self.writeresponse("")
            return

        if len(params) != 1:
            self.writeerror("Missing aspect ratio.")
            self.writeerror("")
            return

        try:
            ar = float(params[0])

            if ar < 0.0:
                raise ValueError

            if ar > 1.0:
                raise ValueError
        except ValueError:
            self.writeerror("Invalid aspect ratio. Expected a value between 0.0 and 1.0.")
            self.writeerror("")
            return

        self.aspect_ratio = ar

        self.writeresponse(f"Aspect ratio set to {ar}.")
        self.writeresponse("")

        return

    @command('banner')
    @command('b')
    def command_banner(self, params):
        '''<banner number>
        Displays the banner assigned to that number.
        Useful for sneaking up on your font aspect ratio.
        '''
        index = 0

        try:
            index = int(params[0])
        except Exception:
            self.writeline("Not a valid number.")
            self.writeline("")
            return

        try:
            banner_url = config.banners[index]
        except Exception:
            self.writeline("Banner number is not known.")
            self.writeline("")
            return

        self.writeline(self.chan_server.getAndConvertImage(banner_url, self.WIDTH, self.HEIGHT, self.aspect_ratio))
        self.writeline("")

    def is_valid_board(self, board):
        data = self.chan_server.getBoards()

        board_names = [b['board'] for b in data['boards']]

        board_names.append('lain')

        return board.lower() in board_names

    def cmdHELP(self, params):
        """[<command>]
        Display help
        Display either brief help on all commands, or detailed
        help on a single command passed as a parameter.
        """
        if params:
            cmd = params[0].upper()
            if cmd in self.COMMANDS:
                method = self.COMMANDS[cmd]
                doc = method.__doc__.split("\n")
                docp = doc[0].strip()
                docl = '\n'.join([l.strip() for l in doc[2:]])
                if not docl.strip():  # If there isn't anything here, use line 1
                    docl = doc[1].strip()
                self.writeline(
                    "%s %s\n\n%s" % (
                        cmd,
                        docp,
                        docl,
                    )
                )
                return
            else:
                self.writeline("Command '%s' not known" % cmd)
        else:
            self.writeline("Help on built in commands\n")
        keys = sorted(self.COMMANDS.keys())
        for cmd in keys:
            method = self.COMMANDS[cmd]
            if getattr(method, 'hidden', False):
                continue
            if method.__doc__ is None:
                self.writeline("no help for command %s" % method)
                return
            doc = method.__doc__.split("\n")
            docp = doc[0].strip()
            docs = doc[1].strip()
            if len(docp) > 0:
                docps = "%s - %s" % (docp, docs, )
            else:
                docps = "- %s" % (docs, )
            self.writeline(
                "%s %s" % (
                    cmd,
                    docps,
                )
            )
    cmdHELP.aliases = ['?']

    @command('minibanner')
    @command('mb')
    def command_minibanner(self, params):
        """
        Displays the mini banner as ASCII text.
        Call the random mini banner on lainchan and converts it to ASCII. It's random and cached so it won't refresh every call.
        """
        try:
            banner_url = config.mini_banner_url
        except Exception:
            self.writeline("Mini banner is not configured.")
            self.writeline("")
            return

        self.writeline(self.chan_server.getAndConvertImage(banner_url, self.WIDTH, self.HEIGHT, self.aspect_ratio))
        self.writeline("")

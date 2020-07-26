from threaded_telnet_handler import ThreadedTelnetHandler


class PagedTelnetHandler(ThreadedTelnetHandler):

    "A telnet server handler using Threading"
    def __init__(self, request, client_address, server):
        ThreadedTelnetHandler.__init__(self, request, client_address, server)

    def setup(self):
        ThreadedTelnetHandler.setup(self)

        self.output_queue = []
        self.page_size = 24
        self.paging = True

    # -- Threaded output handling functions --
    def writemessage(self, text):
        lines = text.split('\n')

        for line in lines:
            self.output_queue.append(line)

    def writeline(self, text):
        self.writemessage(text)

    def flush(self, skip_prompt=False):
        if len(self.output_queue) == 0:
            return

        if len(self.output_queue) > self.page_size and self.paging:
            output_lines = []

            output_lines = self.output_queue[0:self.page_size]
            self.output_queue = self.output_queue[self.page_size:]

            output = '\n'.join(output_lines)
        else:
            output = '\n'.join(self.output_queue)
            self.output_queue = []

        self.write(output + "\n")

        if len(self.output_queue) > 0:
            if not skip_prompt:
                pass
                self.readline(prompt=self.CONTINUE_PROMPT)

            self.flush(skip_prompt)

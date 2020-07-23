from colors import color
import time

class PostFormatter():

    def __init__(self):
        self.out = []

    def format_post(self, text):
        lines = text.split('\n')

        for line in lines:
            if line.startswith('>>'):
                self.out.append(color(line, style='bold', fg='white'))
            elif line.startswith('>'):
                self.out.append(color(line, style='bold', fg='green'))
            else:
                self.out.append(line)

        return '\n'.join(self.out)

    def format_post_header(self, post):
        header = str(post['no']) + ' - ' + color(str(post['name']), fg='red')

        if 'time' in post.keys():
            epoch_ts = time.gmtime(int(post['time']))
            formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", epoch_ts)

            header = header + " - " + formatted_time

        return header

    def format_board_title(self, board):
        return "{} - {}".format(
            color(board['board'], fg='white', style='bold'),
            color(board['title'], fg='green')
        )

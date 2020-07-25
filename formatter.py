from colors import color
import time


class PostFormatter():

    def format_post(self, text):
        out = []

        lines = text.split('\n')

        for line in lines:
            if line.startswith('>>'):
                out.append(color(line, style='bold', fg='white'))
            elif line.startswith('>'):
                out.append(color(line, style='bold', fg='green'))
            else:
                out.append(line)

        return '\n'.join(out)

    def format_post_header(self, post):
        header = str(post['no'])

        if 'sub' in post.keys():
            header = header + " - " + color(post['sub'], fg='cyan', style='bold')

        header = header + ' - ' + color(str(post['name']), fg='red')

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

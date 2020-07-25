from colors import color
import time
from htmlcleaner import strip_tags


class PostFormatter():

    def format_post_comment(self, text):
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

    def format_post(self, post, board, chan_server, images=False, hline_color='blue', hline_style=None):
        lines = []

        lines.append('')

        lines.append(self.get_hline(
            fg=hline_color,
            style=hline_style
        ))

        header = self.format_post_header(post)

        lines.append(header)

        if 'tim' in post.keys():
            if images:
                lines.append('')

                img = chan_server.getThumbNail(board, post['tim'], '.png')

                if img:
                    lines.append(img)
                else:
                    lines.append('<<IMAGE ERROR>>')
            else:
                lines.append(chan_server.getThumbNailURL(board, post['tim'], '.png'))

            lines.append('')

        if 'com' in post.keys():
            lines.append(self.format_post_comment(strip_tags(post['com'])))

        lines.append(self.get_hline(
            fg=hline_color,
            style=hline_style
        ))

        return '\n\r'.join(lines)

    def get_hline(self, fg='blue', style=None):
        return color('*-------------------------------*', fg=fg, style=style)

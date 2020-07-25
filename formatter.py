from colors import color
import time
from htmlcleaner import strip_tags
from textwrap import wrap


class PostFormatter():

    def format_post_comment(self, text, wrap_width=80):
        out = []

        lines = text.split('\n')

        for line in lines:
            if line.startswith('>>'):
                out_line = color(line, style='bold', fg='white')
            elif line.startswith('>'):
                out_line = color(line, style='bold', fg='green')
            else:
                out_line = line

            lines_to_add = wrap(out_line, width=wrap_width)

            final_l = '\n\r'.join(lines_to_add)

            out.append(final_l)

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

    def format_post(self, post, board, chan_server, images=False, hline_color='blue', hline_style=None, text_width=80):
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
                lines.append(self.format_post_image(post, board, chan_server))
            else:
                lines.append(chan_server.getThumbNailURL(board, post['tim'], '.png'))

        lines.append("")

        if 'com' in post.keys():
            lines.append(self.format_post_comment(strip_tags(post['com']), text_width))

        lines.append(self.get_hline(
            fg=hline_color,
            style=hline_style
        ))

        return '\n\r'.join(lines)

    def get_hline(self, fg='blue', style=None):
        return color('*-------------------------------*', fg=fg, style=style)

    def format_post_image(self, post, board, chan_server, w=80, h=24, ar=0.61):
        lines = []

        if 'tim' in post.keys():
            img = chan_server.getThumbNail(board, post['tim'], '.png', w, h, ar)

            if img:
                lines.append(img)
            else:
                lines.append('Unable to process image.')

        return '\n\r'.join(lines)

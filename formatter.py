from colors import *

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

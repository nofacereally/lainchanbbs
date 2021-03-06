#
#    4Chan BBS
#    ASCII Image - ascii_image.py
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

import aalib
import io
from PIL import Image
import urllib


def convert_image(img, x, y, ar=0.61):
    # account for prompt
    y = y - 2

    img_w = img.size[0]
    img_h = img.size[1]

    if img_w > img_h:
        ratio = img_h / img_w

        final_w = x
        final_h = min(y, ((y * ratio) + (y * ar)))
    else:
        ratio = img_w / img_h

        final_w = min(x, x * ratio)
        final_h = y

    screen = aalib.LinuxScreen(width=int(final_w), height=int(final_h))

    img = img.convert('L').resize(screen.virtual_size)

    screen.put_image((0, 0), img)

    return screen.render()


def open_url(URL):
    try:
        file = io.BytesIO(urllib.request.urlopen(URL).read())
        img = Image.open(file)
        return img
    except Exception as ex:
        print('Error: Failed to open image at %s: %s' % (URL, str(ex)))
        return

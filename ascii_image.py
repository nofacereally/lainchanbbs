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


def convert_image(img, x, y, scale_height=0.7):

    if img.size[0] > x:
        scaled_w = abs(int(1 - (x / img.size[0] - 0.2) * img.size[0]))
    else:
        scaled_w = int(img.size[0])

    if img.size[1] > y:
        scaled_h = abs(int(1 - (y / img.size[1]) * img.size[1]))
    else:
        scaled_h = int(img.size[1])

    scaled_h = int(scaled_h * scale_height)

    screen = aalib.LinuxScreen(width=scaled_w, height=scaled_h)

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

#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""DOCSTRING HERE"""

import gi
import random
from array import array
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf


class Color:
    """Holds color information"""

    def __init__(self, red=255, green=255, blue=255):
        self.red = red
        self.green = green
        self.blue = blue

    def __str__(self):
        return f'{self.red:02X}{self.green:02X}{self.blue:02X}'

    def __int__(self):
        return (self.red << 16) + (self.green << 8) + self.blue

    def __iter__(self):
        return (x for x in [self.red, self.green, self.blue])

    def invert(self):
        self.red = self.red ^ 0xFF
        self.green = self.green ^ 0xFF
        self.blue = self.blue ^ 0xFF



class VideoBuffer:
    """Video Buffer Class"""
    def __init__(self, width=256, height=240, scale=1):
        self.width = width
        self.height = height
        self.scale = scale
        self.header = bytes(f'P6 {self.overall_width:d} {self.overall_height:d} 255 ', 'utf-8')
        self.data = array('B', [0 for _ in range(3 * self.overall_size)])

    def output(self):
        return self.header + self.data

    def fill(self, color):
        self.data = array('B', self.overall_width * self.overall_height * list(color))

    def __getitem__(self, pos):
        x, y = pos
        assert(x < self.width)
        assert(y < self.height)
        index = self.scale * 3 * (y * self.overall_width + x)
        return Color(self.data[index], self.data[index+1], self.data[index+2])

    def __setitem__(self, pos, color):
        x, y = pos
        assert(x < self.width)
        assert(y < self.height)
        index = self.scale * 3 * (y * self.overall_width + x)
        for local_y in range(self.scale):
            for local_x in range(self.scale):
                for n, val in enumerate(color):
                    self.data[index + 3 * (local_y * self.overall_width + local_x) + n] = val

    @property
    def overall_width(self):
        return self.width * self.scale

    @property
    def overall_height(self):
        return self.height * self.scale

    @property
    def overall_size(self):
        return self.overall_width * self.overall_height


class Screen(Gtk.Window):
    """Class to produce window"""
    def __init__(self, width=256, height=240, scale=1, title=None, background=Color(0xAD, 0xD8, 0xE6)):
        Gtk.Window.__init__(self)
        self.connect("destroy", Gtk.main_quit)
        if title:
            self.set_title(title)
        self.scale = scale
        self.height = height
        self.width = width
        self.background = background
        self.grid = Gtk.Grid()
        self.add(self.grid)
        self.video_buffer = VideoBuffer(self.width, self.height, self.scale)
        self.video_buffer.fill(background)
        self.image = Gtk.Image()
        self.draw()
        self.grid.attach(self.image, 0, 0, 1, 10)
        self.button = Gtk.Button(label="Quit")
        self.button.connect("clicked", Gtk.main_quit)
        self.grid.attach_next_to(self.button, self.image, Gtk.PositionType.BOTTOM, 1, 1)
        self.show_all()

    def draw(self):
        loader = GdkPixbuf.PixbufLoader.new_with_type('pnm')
        loader.write(self.video_buffer.output())
        pixel_buffer = loader.get_pixbuf()
        loader.close()
        self.image.set_from_pixbuf(pixel_buffer)


if __name__ == "__main__":
    win = Screen(scale=2, title="Emulator")
    Gtk.main()

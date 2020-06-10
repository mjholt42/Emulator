#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""The main emulation code"""

import gi
from array import array
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GdkPixbuf


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
        self.header = array('B', bytes(f'P6 {self.overall_width:d} {self.overall_height:d} 255 ', 'utf-8'))
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


# noinspection PyArgumentList,PyUnresolvedReferences
class ProgramList:

    def __init__(self, cpu):
        self.cpu = cpu
        self.model = Gtk.ListStore(str, int)
        self.index = list()
        for index, text in self.cpu.list_commands().items():
            self.index.append(index)
            self.model.append((text, 0))
        self.renderer = Gtk.CellRendererText()
        self.column = Gtk.TreeViewColumn('Commands', self.renderer, text=0, weight_set=True)
        self.column.set_cell_data_func(self.renderer, self.current)
        self.tree = Gtk.TreeView.new_with_model(self.model)
        self.tree.append_column(self.column)
        self.view = Gtk.ScrolledWindow()
        self.view.set_vexpand(True)
        self.view.add(self.tree)
        self.current_index = 0

    def reset_data(self):
        self.model.clear()
        self.index = list()
        for index, text in self.cpu.list_commands().items():
            self.index.append(index)
            self.model.append((text, 0))
        self.current_index = 0

    @staticmethod
    def current(_, renderer, model, titer, __):
        val = model.get_value(titer, 1)
        if val:
            renderer.set_property("weight", 700)

    def set_index(self, address):
        try:
            new_index = self.index.index(address)
            if new_index == self.current_index:
                return None
        except ValueError:
            self.reset_data()
            new_index = self.current_index

        self.model[self.current_index][1] = 0
        self.current_index = new_index
        self.model[self.current_index][1] = 1
        self.tree.set_cursor(self.current_index)
        return self.model[self.current_index][0]


# noinspection PyArgumentList,PyUnresolvedReferences
class HistoryList:

    def __init__(self):
        self.model = Gtk.ListStore(str, str, str, str, str, str)
        self.renderer = Gtk.CellRendererText()
        self.column = Gtk.TreeViewColumn('History', self.renderer, text=0)
        self.tree = Gtk.TreeView.new_with_model(self.model)

        self.tree.append_column(Gtk.TreeViewColumn('History', self.renderer, text=0))
        self.tree.append_column(Gtk.TreeViewColumn('A', self.renderer, text=1))
        self.tree.append_column(Gtk.TreeViewColumn('X', self.renderer, text=2))
        self.tree.append_column(Gtk.TreeViewColumn('Y', self.renderer, text=3))
        self.tree.append_column(Gtk.TreeViewColumn('S', self.renderer, text=4))
        self.tree.append_column(Gtk.TreeViewColumn('P', self.renderer, text=5))

        self.view = Gtk.ScrolledWindow()
        self.view.set_vexpand(True)
        self.view.add(self.tree)

    def add_row(self, data, a, x, y, s, p):
        if data:
            self.model.append((data,
                               f'{a:02X} [{a:d}]',
                               f'{x:02X} [{x:d}]',
                               f'{y:02X} [{y:d}]',
                               f'{s:02X}',
                               f'{p:08b}'
                               ))
            # noinspection PyTypeChecker
            if len(self.model) > 100:
                del(self.model[0])


# noinspection PyArgumentList,PyUnresolvedReferences
class Registers(Gtk.Frame):

    def __init__(self, cpu, *args, **kwargs):
        self.cpu = cpu
        super().__init__(*args, **kwargs)
        self.set_label('Registers')
        self.status = cpu6502.Status
        self.grid = Gtk.Grid()
        self.add(self.grid)
        self.PC_label = Gtk.Label()
        self.PC_label.set_markup('<b>PC</b>   ')
        self.grid.attach(self.PC_label, 0, 0, 1, 1)
        self.A_label = Gtk.Label()
        self.A_label.set_markup('<b>A</b>    ')
        self.grid.attach_next_to(self.A_label, self.PC_label, Gtk.PositionType.BOTTOM, 1, 1)
        self.X_label = Gtk.Label()
        self.X_label.set_markup('<b>X</b>    ')
        self.grid.attach_next_to(self.X_label, self.A_label, Gtk.PositionType.BOTTOM, 1, 1)
        self.Y_label = Gtk.Label()
        self.Y_label.set_markup('<b>Y</b>    ')
        self.grid.attach_next_to(self.Y_label, self.X_label, Gtk.PositionType.BOTTOM, 1, 1)
        self.S_label = Gtk.Label()
        self.S_label.set_markup('<b>S</b>    ')
        self.grid.attach_next_to(self.S_label, self.Y_label, Gtk.PositionType.BOTTOM, 1, 1)
        self.P_label = Gtk.Label()
        self.P_label.set_markup('<b>P</b>    ')
        self.grid.attach_next_to(self.P_label, self.S_label, Gtk.PositionType.BOTTOM, 1, 1)
        self.PC = Gtk.Label()
        self.grid.attach_next_to(self.PC, self.PC_label, Gtk.PositionType.RIGHT, 1, 1)
        self.A = Gtk.Label()
        self.grid.attach_next_to(self.A, self.A_label, Gtk.PositionType.RIGHT, 1, 1)
        self.X = Gtk.Label()
        self.grid.attach_next_to(self.X, self.X_label, Gtk.PositionType.RIGHT, 1, 1)
        self.Y = Gtk.Label()
        self.grid.attach_next_to(self.Y, self.Y_label, Gtk.PositionType.RIGHT, 1, 1)
        self.S = Gtk.Label()
        self.grid.attach_next_to(self.S, self.S_label, Gtk.PositionType.RIGHT, 1, 1)
        self.P = Gtk.Label()
        self.grid.attach_next_to(self.P, self.P_label, Gtk.PositionType.RIGHT, 1, 1)
        self.update()

    def get_status(self):
        out = ''
        for flag in self.status.flags():
            if self.cpu.P & self.status[flag]:
                settings = 'foreground="green" weight="bold"'
            else:
                settings = 'foreground="red"'
            out += f'<span {settings}>{flag}</span> '
        return out

    def update(self):
        self.PC.set_markup(f'${self.cpu.PC:04X}')
        self.A.set_markup(f'${self.cpu.A:02X} [{self.cpu.A:d}]')
        self.X.set_markup(f'${self.cpu.X:02X} [{self.cpu.X:d}]')
        self.Y.set_markup(f'${self.cpu.Y:02X} [{self.cpu.Y:d}]')
        self.S.set_markup(f'$(01){self.cpu.S:02X}')
        self.P.set_markup(self.get_status())


# noinspection PyArgumentList,PyUnresolvedReferences
class Screen(Gtk.Window):
    """Class to produce window"""
    def __init__(self, cpu, width=256, height=240, scale=1, title=None, background=Color(0xAD, 0xD8, 0xE6)):
        Gtk.Window.__init__(self)
        self.cpu = cpu
        self.timer = 0
        self.connect("destroy", Gtk.main_quit)
        if title:
            self.set_title(title)
        self.scale = scale
        self.height = height
        self.width = width
        self.background = background
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.add(self.grid)
        self.video_buffer = VideoBuffer(self.width, self.height, self.scale)
        self.video_buffer.fill(background)
        self.image = Gtk.Image()
        self.grid.attach(self.image, 0, 0, 6, 6)
        self.reset_btn = Gtk.Button(label="Reset")
        self.reset_btn.connect("clicked", self.reset)
        self.irq_btn = Gtk.Button(label="IRQ")
        self.irq_btn.connect("clicked", self.irq)
        self.nmi_btn = Gtk.Button(label="NMI")
        self.nmi_btn.connect("clicked", self.nmi)
        self.start_btn = Gtk.Button(label="Start")
        self.start_btn.connect("clicked", self.start)
        self.command_btn = Gtk.Button(label="Command")
        self.command_btn.connect("clicked", self.command)
        self.grid.attach_next_to(self.reset_btn, self.image, Gtk.PositionType.BOTTOM, 2, 1)
        self.grid.attach_next_to(self.irq_btn, self.reset_btn, Gtk.PositionType.RIGHT, 2, 1)
        self.grid.attach_next_to(self.nmi_btn, self.irq_btn, Gtk.PositionType.RIGHT, 2, 1)
        self.grid.attach_next_to(self.start_btn, self.nmi_btn, Gtk.PositionType.RIGHT, 2, 1)
        self.grid.attach_next_to(self.command_btn, self.start_btn, Gtk.PositionType.RIGHT, 2, 1)
        self.registers = Registers(self.cpu)
        self.program_list = ProgramList(self.cpu)
        self.grid.attach_next_to(self.registers, self.image, Gtk.PositionType.RIGHT, 3, 1)
        self.grid.attach_next_to(self.program_list.view, self.registers, Gtk.PositionType.BOTTOM, 3, 5)
        self.history_list = HistoryList()
        self.grid.attach_next_to(self.history_list.view, self.registers, Gtk.PositionType.RIGHT, 6, 6)
        self.draw()
        self.show_all()

    def reset(self, _):
        self.cpu.reset()
        self.draw()

    def irq(self, _):
        self.cpu.irq()
        self.draw()

    def nmi(self, _):
        self.cpu.irq()
        self.draw()

    def command(self, _=None):
        while not self.cpu.clock():
            pass
        self.draw()
        return True

    def start(self, _):
        if self.start_btn.get_label() == 'Start':
            self.start_btn.set_label('Stop')
            self.timer = GLib.timeout_add(5, self.command)
        else:
            self.start_btn.set_label('Start')
            GLib.source_remove(self.timer)
            self.timer = 0

    def draw(self):
        loader = GdkPixbuf.PixbufLoader.new_with_type('pnm')
        loader.write(self.video_buffer.output())
        pixel_buffer = loader.get_pixbuf()
        loader.close()
        self.image.set_from_pixbuf(pixel_buffer)
        text = self.program_list.set_index(self.cpu.PC)
        self.history_list.add_row(text, self.cpu.A, self.cpu.X, self.cpu.Y, self.cpu.S, self.cpu.P)
        self.registers.update()


if __name__ == "__main__":
    import cpu6502
    import memory
    import bus

    b = bus.Bus()
    m = memory.RAM(b, 65536)
    b.register(m, 0)
    c = cpu6502.Cpu6502(b, False)
    win = Screen(c, scale=2, title="Emulator")
    Gtk.main()

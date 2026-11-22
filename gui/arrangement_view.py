import platform
import tkinter as tki
import ttkbootstrap as ttk
from tkinter import filedialog as fd

from gui import song
from gui import elements


class PatternGridButton(elements.GridButton):
    def _pressed(self):
        self._gd['song']['arrangement'][self._row][self._column] = self.on

    def load(self):
        self.on = self._gd['song']['arrangement'][self._row][self._column]
        self._update_view()


class PatternMenu(ttk.Frame):
    def __init__(self, row: int, gd: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__gd = gd
        self.__row = row
        self.grid_propagate(False)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.__button = ttk.Menubutton(master=self, text=f'Pattern {row}', bootstyle='neutral')
        button_menu = ttk.Menu(master=self)
        button_menu.add_command(label='Open', command=self.__open_pattern)
        button_menu.add_command(label='Rename')
        button_menu.add_separator()
        button_menu.add_command(label='Duplicate')
        button_menu.add_command(label='Delete', command=self.__delete_row)
        button_menu.add_separator()
        button_menu.add_command(label='Insert New', command=self.__insert_row)
        self.__button.configure(menu=button_menu)
        self.__button.grid(column=0, row=0, sticky='nwes')

    def set_row(self, row: int):
        self.__row = row
        self.__button.configure(text=f'Pattern {row}')

    def __open_pattern(self):
        self.__gd['app'].pattern_frame.select_pattern(self.__row)
        self.__gd['app'].notebook.select(1)

    def __delete_row(self):
        self.__gd['app'].arrangement_frame.patterns.remove_row(self.__row)

    def __insert_row(self):
        self.__gd['app'].arrangement_frame.patterns.insert_row(self.__row+1)


class PatternRow(ttk.Frame):
    def __init__(self, length_bars: int, row: int, gd: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__gd = gd
        self.__row = row
        self.__length_bars = length_bars
        self.rowconfigure(0, weight=0, minsize=40)
        self.columnconfigure(0, weight=0, minsize=150)
        self.__pattern_menu = PatternMenu(row, gd, master=self)
        self.__pattern_menu.grid(column=0, row=0, sticky='nwes')

        self.buttons: list[PatternGridButton] = []
        for column in range(self.__length_bars):
            self.columnconfigure(column+1, weight=1)
            button = PatternGridButton(row, column, gd, master=self)
            button.grid(column=column+1, row=0, sticky='nwes')
            self.buttons.append(button)

    def set_length_bars(self, new_length_bars: int):
        if new_length_bars >= self.__length_bars:
            for column in range(self.__length_bars, new_length_bars):
                self.columnconfigure(column+1, weight=1)
                button = PatternGridButton(self.__row, column, self.__gd, master=self)
                button.grid(column=column+1, row=0, sticky='nwes')
                self.buttons.append(button)
        else:
            for _ in range(new_length_bars, self.__length_bars):
                self.buttons.pop().destroy()

        self.__length_bars = new_length_bars

    def set_row(self, row: int):
        self.__row = row
        self.__pattern_menu.set_row(row)
        for button in self.buttons:
            button.set_row(row)

    def reload_view(self):
        for button in self.buttons:
            button.load()


class PatternsList(ttk.Canvas):
    def __init__(self, length_bars: int, gd: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__gd = gd
        self.__length_bars = length_bars
        self.columnconfigure(0, weight=1)

        self.__pattern_rows = elements.WindowWithRows(master=self)
        self.__pattern_rows.columnconfigure(0, weight=1)
        self.__pattern_rows.grid(column=0, row=0, sticky='nwes')

        window_id = self.create_window(
            (0, 0),
            window=self.__pattern_rows,
            anchor="nw"
        )

        self.__pattern_rows.bind('<Configure>', self.__update_scroll)
        self.bind('<Configure>',
                  lambda event: self.itemconfigure(
                      window_id,
                      width=event.width
                  ))

        if platform.system() == 'Linux':
            self.bind_all('<Button-4>', lambda _: self.yview_scroll(-1, 'units'))
            self.bind_all('<Button-5>', lambda _: self.yview_scroll( 1, 'units'))

        self.list: list[PatternRow] = []

    def __update_scroll(self, _=None):
        self.configure(scrollregion=self.bbox("all"))
    
    def __update_row_numbers(self, start: int):
        for i in range(start, len(self.list)):
            self.list[i].set_row(i)

    def __append_row_local(self):
        new_row = PatternRow(self.__length_bars, len(self.list), self.__gd, master=self)
        self.__pattern_rows.add(new_row)
        self.list.append(new_row)

    def append_row(self):
        self.__append_row_local()
        self.__gd['song']['patterns'] \
            .append(song.Pattern(song.START_PATTERN_LENGTH, len(self.__gd['song']['patterns'][0]['sequenced_samples'])))
        self.__gd['song']['arrangement'].append([False] * self.__gd['song']['length_bars'])

    def __insert_row_local(self, row: int):
        new_row = PatternRow(self.__length_bars, len(self.list), self.__gd, master=self)
        self.__pattern_rows.insert(new_row, pos=row)
        self.list.insert(row, new_row)
        self.__update_row_numbers(row)

    def insert_row(self, row: int):
        if row >= len(self.list):
            self.append_row()
            return

        self.__insert_row_local(row)
        self.__gd['song']['patterns'] \
            .insert(row, song.Pattern(song.START_PATTERN_LENGTH, len(self.__gd['song']['patterns'][0]['sequenced_samples'])))
        self.__gd['song']['arrangement'].insert(row, [False] * self.__gd['song']['length_bars'])

    def __remove_row_local(self, row: int):
        self.__pattern_rows.remove(row)
        self.list.pop(row)
        self.__update_row_numbers(row)

    def remove_row(self, row: int):
        self.__remove_row_local(row)
        self.__gd['song']['patterns'].pop(row)
        self.__gd['song']['arrangement'].pop(row)

    def init_rows(self, n: int):
        for _ in range(abs(n - len(self.list))):
            if n > len(self.list): self.__append_row_local()
            else: self.__remove_row_local(0)

    def set_length_bars(self, length_bars: int):
        self.__gd['song']['length_bars'] = length_bars

        for pattern in self.__gd['song']['arrangement']:
            for _ in range(abs(len(pattern) - length_bars)):
                if len(pattern) < length_bars: pattern.append(False)
                else: pattern.pop()

        self.__length_bars = length_bars

        for pattern_row in self.list:
            pattern_row.set_length_bars(length_bars)
            pattern_row.reload_view()

    def reload_view(self):
        self.set_length_bars(self.__gd['song']['length_bars'])


class ArrangementFrame(ttk.Frame):
    def __init__(self, gd: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__gd = gd

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.__root_frame = ttk.Frame(master=self)
        self.__root_frame.rowconfigure(0, weight=0)
        self.__root_frame.rowconfigure(1, weight=1)
        self.__root_frame.columnconfigure(0, weight=0)
        self.__root_frame.columnconfigure(1, weight=1)
        self.__root_frame.columnconfigure(2, weight=0)

        self.__length_select_var = tki.IntVar()
        self.__length_select_var.set(1)
        ttk.Label(master=self.__root_frame, text='Length (bars):').grid(column=0, row=0, sticky='nwes')
        length_select = ttk.Spinbox(master=self.__root_frame, from_=1, to=2**5, textvariable=self.__length_select_var,
                                    command=self.__song_length_changed, bootstyle='neutral')
        length_select.grid(column=1, row=0, sticky='nws')

        self.patterns = PatternsList(song.START_SONG_LENGTH, self.__gd, master=self.__root_frame)
        self.patterns.grid(column=0, row=1, columnspan=3, sticky='nwes')
        self.__scrollbar = ttk.Scrollbar(master=self.__root_frame, orient='vertical', command=self.patterns.yview)
        self.patterns.configure(yscrollcommand=self.__scrollbar.set)
        self.__scrollbar.grid(column=2, row=1, sticky='nwes')

        self.__root_frame.grid(sticky='nwes')

        self.patterns.init_rows(song.START_PATTERNS)

    def __song_length_changed(self):
        self.patterns.set_length_bars(self.__length_select_var.get())

    def set_length_bars(self, length_bars: int):
        self.__length_select_var.set(length_bars)
        self.__song_length_changed()

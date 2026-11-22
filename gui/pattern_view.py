import platform
import tkinter as tki
import ttkbootstrap as ttk
from tkinter import filedialog as fd

from gui import song
from gui import elements


class SampleGridButton(elements.GridButton):
    def _pressed(self):
        self._gd['song']['patterns'][self._gd['current_pattern_number']] \
                    ['sequenced_samples'][self._row] \
                        ['sequence'][self._column] = self.on


    def load(self):
        self.on = self._gd['song']['patterns'][self._gd['current_pattern_number']] \
            ['sequenced_samples'][self._row] \
                ['sequence'][self._column]
        self._update_view()


class SampleMenu(ttk.Frame):
    def __init__(self, row: int, gd: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__gd = gd
        self.__row = row
        self.grid_propagate(False)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.__button = ttk.Menubutton(master=self, text='[Empty]', bootstyle='neutral')
        button_menu = ttk.Menu(master=self)
        button_menu.add_command(label='Select Sample', command=self.__select_sample)
        button_menu.add_separator()
        button_menu.add_command(label='Duplicate')
        button_menu.add_command(label='Delete', command=self.__delete_row)
        button_menu.add_separator()
        button_menu.add_command(label='Insert New', command=self.__insert_row)
        self.__button.configure(menu=button_menu)
        self.__button.grid(column=0, row=0, sticky='nwes')

    def __select_sample(self):
        old_sample = self.__gd['song']['patterns'][0]['sequenced_samples'][self.__row]['name']
        new_sample = fd.askopenfilename()
        if not new_sample: new_sample = old_sample
        for pattern in self.__gd['song']['patterns']:
            pattern['sequenced_samples'][self.__row]['name'] = new_sample
        self.__button.configure(text=new_sample.split('/')[-1] if new_sample else '[Empty]')

    def set_row(self, row: int):
        self.__row = row

    def __delete_row(self):
        self.__gd['app'].pattern_frame.samples.remove_row(self.__row)

    def __insert_row(self):
        self.__gd['app'].pattern_frame.samples.insert_row(self.__row+1)

    def reload_view(self):
        sample_name = self.__gd['song']['patterns'][0]['sequenced_samples'][self.__row]['name']
        self.__button.configure(text=sample_name.split('/')[-1] if sample_name else '[Empty]')


class SampleRow(ttk.Frame):
    def __init__(self, length_16s: int, row: int, gd: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__gd = gd
        self.__row = row
        self.__length_16s = length_16s
        self.rowconfigure(0, weight=0, minsize=40)
        self.columnconfigure(0, weight=0, minsize=150)
        self.__sample_menu = SampleMenu(row, gd, master=self)
        self.__sample_menu.grid(column=0, row=0, sticky='nwes')

        self.buttons: list[SampleGridButton] = []
        for column in range(self.__length_16s):
            self.columnconfigure(column+1, weight=1)
            button = SampleGridButton(row, column, gd, master=self)
            button.grid(column=column+1, row=0, sticky='nwes')
            self.buttons.append(button)

    def set_length_16s(self, new_length_16s: int):
        if new_length_16s >= self.__length_16s:
            for column in range(self.__length_16s, new_length_16s):
                self.columnconfigure(column+1, weight=1)
                button = SampleGridButton(self.__row, column, self.__gd, master=self)
                button.grid(column=column+1, row=0, sticky='nwes')
                self.buttons.append(button)
        else:
            for _ in range(new_length_16s, self.__length_16s):
                self.buttons.pop().destroy()

        self.__length_16s = new_length_16s

    def set_row(self, row: int):
        self.__row = row
        self.__sample_menu.set_row(row)
        for button in self.buttons:
            button.set_row(row)

    def reload_view(self):
        self.__sample_menu.reload_view()
        for button in self.buttons:
            button.load()


class SamplesList(ttk.Canvas):
    def __init__(self, length_16s: int, gd: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__gd = gd
        self.__length_16s = length_16s
        self.columnconfigure(0, weight=1)

        self.__sample_rows = elements.WindowWithRows(master=self)
        self.__sample_rows.columnconfigure(0, weight=1)
        self.__sample_rows.grid(column=0, row=0, sticky='nwes')

        window_id = self.create_window(
            (0, 0),
            window=self.__sample_rows,
            anchor="nw"
        )

        self.__sample_rows.bind('<Configure>', self.__update_scroll)
        self.bind('<Configure>',
                  lambda event: self.itemconfigure(
                      window_id,
                      width=event.width
                  ))

        if platform.system() == 'Linux':
            self.bind_all('<Button-4>', lambda _: self.yview_scroll(-1, 'units'))
            self.bind_all('<Button-5>', lambda _: self.yview_scroll( 1, 'units'))

        self.list: list[SampleRow] = []

    def __update_scroll(self, _=None):
        self.configure(scrollregion=self.bbox("all"))

    def __update_row_numbers(self, start: int):
        for i in range(start, len(self.list)):
            self.list[i].set_row(i)

    def __append_row_local(self):
        new_row = SampleRow(self.__length_16s, len(self.list), self.__gd, master=self)
        self.__sample_rows.add(new_row)
        self.list.append(new_row)

    def append_row(self):
        self.__append_row_local()
        for pattern in self.__gd['song']['patterns']:
            pattern['sequenced_samples'].append(song.SequencedSample(pattern['length_bars']))

    def __insert_row_local(self, row: int):
        new_row = SampleRow(self.__length_16s, len(self.list), self.__gd, master=self)
        self.__sample_rows.insert(new_row, row)
        self.list.insert(row, new_row)
        self.__update_row_numbers(row)

    def insert_row(self, row: int):
        if row >= len(self.list):
            self.append_row()
            return

        self.__insert_row_local(row)

        for pattern in self.__gd['song']['patterns']:
            pattern['sequenced_samples'].insert(row, song.SequencedSample(pattern['length_bars']))

    def __remove_row_local(self, row: int):
        self.__sample_rows.remove(row)
        self.list.pop(row)
        self.__update_row_numbers(row)

    def remove_row(self, row: int):
        if len(self.list) == 1:
            return

        self.__remove_row_local(row)

        for pattern in self.__gd['song']['patterns']:
            pattern['sequenced_samples'].pop(row)

    def init_rows(self, n: int):
        for _ in range(n - len(self.list)):
            if n > len(self.list): self.__append_row_local()
            else: self.__remove_row_local(0)

    def set_length_16s(self, length_16s: int):
        pattern = self.__gd['song']['patterns'][self.__gd['current_pattern_number']]
        pattern['length_bars'] = length_16s//16

        for sample in pattern['sequenced_samples']:
            for _ in range(abs(len(sample['sequence']) - length_16s)):
                if len(sample['sequence']) < length_16s: sample['sequence'].append(False)
                else: sample['sequence'].pop()

        self.__length_16s = length_16s

        for sample_row in self.list:
            sample_row.set_length_16s(length_16s)
            sample_row.reload_view()

    def reload_view(self):
        pattern = self.__gd['song']['patterns'][self.__gd['current_pattern_number']]
        self.set_length_16s(16*pattern['length_bars'])


class PatternFrame(ttk.Frame):
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
        self.__root_frame.columnconfigure(3, weight=1)
        self.__root_frame.columnconfigure(4, weight=0)

        self.__pattern_select_var = tki.IntVar()
        self.__pattern_select_var.set(0)
        ttk.Label(master=self.__root_frame, text='Selected Pattern:').grid(column=0, row=0, sticky='nwes')
        pattern_select = ttk.Spinbox(master=self.__root_frame, from_=0, to=99, textvariable=self.__pattern_select_var,
                                     command=self.__current_pattern_number_changed, bootstyle='neutral')
        pattern_select.grid(column=1, row=0, sticky='nws')

        self.__length_select_var = tki.IntVar()
        self.__length_select_var.set(1)
        ttk.Label(master=self.__root_frame, text='Length (bars):').grid(column=2, row=0, sticky='nwes')
        length_select = ttk.Spinbox(master=self.__root_frame, from_=1, to=2**5, textvariable=self.__length_select_var,
                                    command=self.__current_pattern_length_changed, bootstyle='neutral')
        length_select.grid(column=3, row=0, sticky='nws')

        self.samples = SamplesList(16*song.START_PATTERN_LENGTH, self.__gd, master=self.__root_frame)
        self.samples.grid(column=0, row=1, columnspan=4, sticky='nwes')
        self.__scrollbar = ttk.Scrollbar(master=self.__root_frame, orient='vertical', command=self.samples.yview)
        self.samples.configure(yscrollcommand=self.__scrollbar.set)
        self.__scrollbar.grid(column=4, row=1, sticky='nwes')

        self.__root_frame.grid(sticky='nwes')

        self.samples.init_rows(song.START_SAMPLES)

    def __current_pattern_number_changed(self):
        num_patterns = len(self.__gd['song']['patterns'])

        if self.__pattern_select_var.get() >= num_patterns:
            self.__pattern_select_var.set(num_patterns - 1)
            return

        self.__gd['current_pattern_number'] = self.__pattern_select_var.get()
        self.__length_select_var.set(self.__gd['song']['patterns'][self.__gd['current_pattern_number']]['length_bars'])
        self.__current_pattern_length_changed()
        self.samples.reload_view()

    def __current_pattern_length_changed(self):
        self.samples.set_length_16s(16*self.__length_select_var.get())

    def current_set_length_bars(self, length_bars: int):
        self.__length_select_var.set(length_bars)
        self.__current_pattern_length_changed()

    def select_pattern(self, pattern: int):
        self.__pattern_select_var.set(pattern)
        self.__current_pattern_number_changed()

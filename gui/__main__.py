import tkinter as tki
import ttkbootstrap as ttk
from tkinter import filedialog as fd

from . import song
from . import pattern_view
from . import arrangement_view


class RootWindow(ttk.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__gd = {'app': self,
                     'song': song.Song(),
                     'current_pattern_number': 0}

        self.title('JULium Beat Editor')
        self.geometry('800x450')

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

        menubar = ttk.Frame(master=self)
        menubar.columnconfigure(0, weight=0)
        menubar.columnconfigure(1, weight=0)
        menubar.columnconfigure(2, weight=1)
        menubar.columnconfigure(3, weight=0)
        menubar.columnconfigure(4, weight=0)

        file_button = ttk.Menubutton(master=menubar, text='File', bootstyle='secondary outline')
        file_menu = ttk.Menu(master=menubar)
        file_menu.add_command(label='Open', command=self.__open)
        file_menu.add_command(label='Save As...', command=self.__save_as)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.destroy)
        file_button.configure(menu=file_menu)
        file_button.grid(column=0, row=0)

        edit_button = ttk.Menubutton(master=menubar, text='Edit', bootstyle='secondary outline')
        edit_menu = ttk.Menu(master=menubar)
        edit_button.configure(menu=edit_menu)
        edit_button.grid(column=1, row=0)

        self.__tempo_select_var = tki.DoubleVar(value=song.START_TEMPO)
        ttk.Label(master=menubar, text='Tempo (BPM):').grid(column=3, row=0)
        tempo_spinbox = ttk.Spinbox(master=menubar, textvariable=self.__tempo_select_var, from_=1, to=999, increment=0.1,
                                    command=self.__tempo_select_changed, bootstyle='secondary')
        tempo_spinbox.grid(column=4, row=0)

        menubar.grid(column=0, row=0, sticky='nwes')

        self.notebook = ttk.Notebook(master=self)
        self.notebook.rowconfigure(0, weight=1)
        self.notebook.columnconfigure(0, weight=1)

        self.arrangement_frame = arrangement_view.ArrangementFrame(self.__gd, master=self.notebook)
        self.pattern_frame = pattern_view.PatternFrame(self.__gd, master=self.notebook)
        self.notebook.add(self.arrangement_frame, text='Arrangement')
        self.notebook.add(self.pattern_frame, text='Pattern')
        self.notebook.grid(column=0, row=1, sticky='nwes')

    def __tempo_select_changed(self):
        self.__gd['song']['tempo'] = self.__tempo_select_var.get()

    def __open(self):
        fptr = fd.askopenfile()
        if fptr:
            with fptr:
                self.__gd['song'] = song.decode_json(fptr.read())

                self.arrangement_frame.patterns.init_rows(len(self.__gd['song']['patterns']))
                self.arrangement_frame.set_length_bars(self.__gd['song']['length_bars'])

                self.pattern_frame.samples.init_rows(len(self.__gd['song']['patterns'][0]['sequenced_samples']))
                self.pattern_frame.current_set_length_bars(len(self.__gd['song']['patterns'][0]['sequenced_samples'][0]['sequence'])//16)

    def __save_as(self):
        fptr = fd.asksaveasfile()
        if fptr:
            with fptr:
                fptr.write(song.encode_json(self.__gd['song']))


ttk.set_global_family("Calibri")
app = RootWindow(themename='bootstrap-dark')
app.mainloop()

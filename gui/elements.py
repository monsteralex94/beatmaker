import ttkbootstrap as ttk


class GridButton(ttk.Button):
    def __init__(self, row: int, column: int, gd: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._gd = gd
        self._row = row
        self._column = column
        self.on = False
        self.__even = self._column % 8 < 4
        self.configure(bootstyle=self.__get_bootstyle(self.on), width=3, command=self.__pressed_update)

    def __get_bootstyle(self, on: bool):
        if on:
            return 'secondary'
        else:
            if self.__even: return 'primary outline'
            else: return 'secondary outline'

    def _update_view(self):
        self.configure(bootstyle=self.__get_bootstyle(self.on))

    def set_row(self, row: int):
        self._row = row

    def _pressed(self):
        # something
        pass

    def __pressed_update(self):
        self.on = not self.on
        self._pressed()
        self._update_view()

    def load(self):
        # something
        pass


class WindowWithRows(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.columnconfigure(0, weight=1)
        self.__widgets = []

    def __update_grid(self, start: int):
        for i in range(start, len(self.__widgets)):
            self.__widgets[i].grid_forget()
            self.__widgets[i].grid(row=i, column=0, sticky='nwes')

    def insert(self, child, pos: int):
        self.__widgets.insert(pos, child)
        self.rowconfigure(pos, weight=1)
        self.__update_grid(pos)

    def add(self, child):
        self.insert(child, len(self.__widgets))

    def remove(self, pos: int):
        self.__widgets[pos].grid_remove()
        self.__widgets.pop(pos)
        self.__update_grid(pos)

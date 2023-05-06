# pyperclip for write to clipboard, pickle for saving dictionaries
import pyperclip
import pickle
import math
import colorsys
import pyautogui
from tkinter import *
from tkinter import font as tkFont
from tkinter import messagebox

# theme constants
primary_light_grey = "#DDDDDD"
secondary_dark_grey = "#5A5A5A"
primary_text_color = "black"
bright_text_color = "#FAFAFA"
settings_text_color = "#EEEE22"


# could theoretically store window size, num cols, etc
user_prefs = {}


def get_palette_row_col(curr_ind, desired_rows, desired_cols):
    # if there are more cols than rows, alternate filling left and right
    if desired_cols > desired_rows:
        curr_row = math.floor(curr_ind / desired_cols)
        if curr_row % 2 == 0:
            curr_col = curr_ind % desired_cols
        else:
            curr_col = desired_cols - (curr_ind % desired_cols) - 1
    # else, there are more rows than cols, so alternate filling down and up
    else:
        curr_col = math.floor(curr_ind / desired_rows)
        if curr_col % 2 == 0:
            curr_row = curr_ind % desired_rows
        else:
            curr_row = desired_rows - (curr_ind % desired_rows) - 1

    return curr_row, curr_col


def create_palette_button(
    master, key, font, bg, activebackground, fg, paste_dict=NONE, handler=NONE
):
    if handler == NONE:
        return Button(
            master=master,
            text=key,
            font=font,
            bg=bg,
            width=13,
            height=5,
            activebackground=activebackground,
            fg=fg,
            command=lambda key=key: pyperclip.copy(paste_dict[key]),
        )
    else:
        return Button(
            master=master,
            text=key,
            font=font,
            bg=bg,
            width=13,
            height=5,
            activebackground=activebackground,
            fg=fg,
            command=handler,
        )


def create_palette_window(title="Text Palette", topmost=True):
    window = Tk()
    window.title(title)
    if topmost:
        window.attributes("-topmost", True)
    return window


class RemoveEntryWindow:
    def retrieve_and_remove_selection(self):
        remove_entry(self.names_list.get(self.names_list.curselection()[0]))
        self.parent.tell_main_to_reload_buttons()
        self.on_close()

    def __init__(self, parent):
        self.remove_entry_window_master = Toplevel(parent.settings_window_master)
        self.remove_entry_window_master.title("Remove An Entry")
        self.remove_entry_window_master.attributes("-topmost", True)
        self.parent = parent
        self.paste_dict = parent.paste_dict

        def check_del_button_state(*args):
            try:
                if self.names_list.curselection()[
                    0
                ] >= 0 and self.names_list.curselection()[0] < len(self.paste_dict):
                    self.del_entry_button.config(state=NORMAL)
            except:
                # no selection or other problem
                self.del_entry_button.config(state=DISABLED)

        # the list part of the scroll list
        self.names_list = Listbox(self.remove_entry_window_master)
        self.names_list.grid(row=0, column=0, columnspan=2, sticky="WEN")

        # the scroll part
        self.scrollbar = Scrollbar(self.remove_entry_window_master)
        self.scrollbar.grid(row=0, column=1, sticky="SEN")

        # insert elems
        for key in self.paste_dict.keys():
            self.names_list.insert(END, key)

            # attach listbox to scrollbar
        self.names_list.config(yscrollcommand=self.scrollbar.set)

        # scrollbar command param
        self.scrollbar.config(command=self.names_list.yview)

        # bind for selection change to check if save should be greyed out
        self.names_list.bind("<ButtonRelease>", check_del_button_state)
        self.names_list.bind("<KeyRelease>", check_del_button_state)

        # create cancel button
        self.cancel_button = Button(
            master=self.remove_entry_window_master,
            text="Cancel",
            command=self.on_close,
        )
        self.cancel_button.grid(row=1, column=0)

        self.del_entry_button = Button(
            master=self.remove_entry_window_master,
            text="Delete Entry",
            state=DISABLED,
            command=self.retrieve_and_remove_selection,
        )
        self.del_entry_button.grid(row=1, column=1)

        self.remove_entry_window_master.protocol("WM_DELETE_WINDOW", self.on_close)

        self.remove_entry_window_master.mainloop()

    # important to handle close
    def on_close(self):
        self.parent.remove_entry_window = None
        self.remove_entry_window_master.destroy()


class AddEntryWindow:
    def __init__(self, parent):
        self.add_entry_window_master = Toplevel(parent.settings_window_master)
        self.add_entry_window_master.title("Add An Entry")
        self.add_entry_window_master.attributes("-topmost", True)
        self.parent = parent
        self.paste_dict = parent.paste_dict

        def check_save_button_state(*args):
            if len(name_entry.get()) > 0 and len(value_entry.get()) > 0:
                save_button.config(state=NORMAL)
            else:
                save_button.config(state=DISABLED)

        # region name
        name_label = Label(master=self.add_entry_window_master, text="Name:")
        name_label.grid(row=0, column=0, pady=10, padx=5, sticky="NESW")
        # Entry for name
        name_entry = Entry(master=self.add_entry_window_master)
        name_entry.grid(row=0, column=1, pady=10, padx=5, sticky="NESW")
        name_entry.bind("<KeyRelease>", check_save_button_state)
        # endregion

        # region value
        value_label = Label(master=self.add_entry_window_master, text="Entry:")
        value_label.grid(row=1, column=0, pady=10, padx=5, sticky="NESW")
        # Entry for value
        value_entry = Entry(master=self.add_entry_window_master)
        value_entry.grid(row=1, column=1, pady=10, padx=5, sticky="NESW")
        value_entry.bind("<KeyRelease>", check_save_button_state)
        # endregion

        # region save/cancel
        cancel_button = Button(
            master=self.add_entry_window_master,
            text="Cancel",
            command=self.on_close,
        )
        cancel_button.grid(row=3, column=0, sticky="NESW")
        # save button:

        def save_entry():
            if not name_entry.get() in self.paste_dict.keys():
                write_addition_to_file(name_entry.get(), value_entry.get())
                self.parent.tell_main_to_reload_buttons()
                self.on_close()
            else:
                messagebox.showerror(
                    "ENTRY REJECTED",
                    "Duplicate name entered! \nPlease enter a name that is not already in use!!",
                )

        save_button = Button(
            master=self.add_entry_window_master,
            text="Save Changes",
            command=save_entry,
            state=DISABLED,
        )
        save_button.grid(row=3, column=1, columnspan=1, sticky="NESW")
        # endregion

        self.add_entry_window_master.protocol("WM_DELETE_WINDOW", self.on_close)

        self.add_entry_window_master.mainloop()

    # important to handle close
    def on_close(self):
        self.parent.add_entry_window = None
        self.add_entry_window_master.destroy()


def write_addition_to_file(name, value):
    to_append = open("paste_dict.txt", "a")
    to_append.write("\n%s~%s" % (name, value))
    to_append.close()


def remove_entry(key):
    # read in paste_dict data
    with open("paste_dict.txt", "r") as file_rd:
        read_lines = file_rd.readlines()
    # write it back when it shouldn't be deleted
    with open("paste_dict.txt", "w") as file_wt:
        curr_ind = 0
        for line in read_lines:
            line = line.strip("\n")
            # check keys for desired
            if not key in line.split("~")[0]:
                if curr_ind != 0:
                    line = "\n" + line
                file_wt.write(line)
                curr_ind += 1


class SettingsWindow:
    def open_add_entry_window(self):
        self.add_entry_window = AddEntryWindow(self)

    def open_remove_entry_window(self):
        self.remove_entry_window = RemoveEntryWindow(self)

    def apply_changes(self):
        self.parent.update_display_info(self.num_cols_var.get())
        self.on_close()

    def tell_main_to_reload_buttons(self):
        self.parent.reload_palette_buttons(self)

    def update_paste_dict(self, paste_dict):
        self.paste_dict = paste_dict

    def update_rows_cols(self, rows=0, cols=0):
        # updates the rows and cols in the settings window
        # then updates the num cols in the main window
        self.num_rows_var.set(rows)
        if rows == 0:
            # cols was updated, adjust rows accordingly
            rows = math.ceil((len(self.paste_dict) + 1) / cols)
        else:
            # rows was updated, adjust cols accordingly
            cols = math.ceil((len(self.paste_dict) + 1) / rows)

        self.num_cols_var.set(cols)
        self.num_rows_var.set(rows)
        self.parent.update_display_info(cols)

    def __init__(self, parent):
        self.settings_window_master = Toplevel(parent.window)
        self.settings_window_master.title("Text Palette Settings")
        self.settings_window_master.attributes("-topmost", True)
        self.parent = parent

        self.add_entry_window = None
        self.remove_entry_window = None

        self.paste_dict = parent.paste_dict
        print(self.paste_dict)
        print("parent")
        print(parent.paste_dict)

        # create number of columns label and entry box
        self.num_cols_label = Label(master=self.settings_window_master, text="Columns:")
        self.num_cols_label.grid(row=0, column=0, pady=20, padx=5, sticky="NESW")
        self.num_cols_var = IntVar(value=parent.desired_cols)
        self.num_cols_entry = Spinbox(
            master=self.settings_window_master,
            from_=1,
            to=99,
            textvariable=self.num_cols_var,
        )
        self.num_cols_entry.grid(row=0, column=1, pady=20, padx=5, sticky="NESW")

        # create number of rows label and entry box
        self.num_rows_label = Label(master=self.settings_window_master, text="Rows:")
        self.num_rows_label.grid(row=1, column=0, pady=20, padx=5, sticky="NESW")
        self.num_rows_var = IntVar(value=parent.desired_rows)
        self.num_rows_entry = Spinbox(
            master=self.settings_window_master,
            from_=1,
            to=99,
            textvariable=self.num_rows_var,
        )
        self.num_rows_entry.grid(row=1, column=1, pady=20, padx=5, sticky="NESW")

        # whenever num_rows_entry is edited, call update_rows_cols with the new value
        self.num_rows_entry.bind(
            "<KeyRelease>",
            lambda event: self.update_rows_cols(rows=int(self.num_rows_var.get())),
        )
        # mouse release event
        self.num_rows_entry.bind(
            "<ButtonRelease>",
            lambda event: self.update_rows_cols(rows=int(self.num_rows_var.get())),
        )
        # whenever num_cols_entry is edited, call update_rows_cols with the new value
        self.num_cols_entry.bind(
            "<KeyRelease>",
            lambda event: self.update_rows_cols(cols=int(self.num_cols_var.get())),
        )
        # mouse release event
        self.num_cols_entry.bind(
            "<ButtonRelease>",
            lambda event: self.update_rows_cols(cols=int(self.num_cols_var.get())),
        )

        # create add entry button
        self.add_entry_button = Button(
            master=self.settings_window_master,
            text="+ Add entry",
            command=self.open_add_entry_window,
        )
        self.add_entry_button.grid(row=3, column=0, pady=10, padx=5, sticky="NESW")

        # create remove entry button
        self.remove_entry_button = Button(
            master=self.settings_window_master,
            text="- Remove entry",
            command=self.open_remove_entry_window,
        )
        self.remove_entry_button.grid(row=3, column=1, pady=10, padx=5, sticky="NESW")

        # create cancel button
        self.cancel_button = Button(
            master=self.settings_window_master,
            text="Cancel",
            command=self.on_close,
        )
        self.cancel_button.grid(row=4, column=0, sticky="NESW")

        # create apply button
        self.apply_button = Button(
            master=self.settings_window_master,
            text="Apply Changes",
            command=self.apply_changes,
        )
        self.apply_button.grid(row=4, column=1, sticky="NESW")

        self.settings_window_master.columnconfigure(0, weight=1)
        self.settings_window_master.columnconfigure(1, weight=1)
        for i in range(0, 5):
            self.settings_window_master.rowconfigure(i, weight=1)

        self.settings_window_master.protocol("WM_DELETE_WINDOW", self.on_close)

        self.settings_window_master.mainloop()

    # important to handle close
    def on_close(self):
        self.parent.reload_palette_buttons()
        self.parent.settings_window = None
        self.settings_window_master.destroy()


class TextPaletteWindow:
    def __init__(self):
        self.window = create_palette_window()

        self.paste_dict = load_paste_dict()
        self.prev_paste_dict_size = len(self.paste_dict)

        self.helv12 = tkFont.Font(family="Helvetica", size=12, weight="bold")

        self.desired_cols = 1
        self.prev_desired_cols = self.desired_cols

        self.settings_window = None

        self.button_arr = []
        self.reload_palette_buttons()

        self.window.mainloop()

    def open_settings_window(self):
        self.settings_window = SettingsWindow(self)

    def update_display_info(self, num_cols):
        # only update values if they have changed
        if num_cols != self.desired_cols:
            # store previous number of columns, update new
            self.prev_desired_cols = self.desired_cols
            self.desired_cols = num_cols

    def reload_palette_buttons(self, settings_window_caller=None):
        # reset the settings_window's grid
        prev_desired_rows = math.ceil(
            (self.prev_paste_dict_size + 1) / self.prev_desired_cols
        )
        for i in range(0, prev_desired_rows + 1):
            self.window.grid_rowconfigure(i, weight=0)
        for i in range(0, self.prev_desired_cols + 1):
            self.window.grid_columnconfigure(i, weight=0)

        # clear out the old buttons
        for button in self.button_arr:
            button.destroy()

        # re-read what's available
        self.paste_dict = load_paste_dict()
        self.prev_paste_dict_size = len(self.paste_dict)

        if settings_window_caller != None:
            settings_window_caller.update_paste_dict(paste_dict=self.paste_dict)

        # calc rows necessary based on num cols and size of paste_dict (+1 for settings button)
        self.desired_rows = math.ceil((len(self.paste_dict) + 1) / self.desired_cols)

        # region key-val buttons
        self.curr_ind = 0
        for key in self.paste_dict.keys():
            # handle positioning

            curr_row, curr_col = get_palette_row_col(
                self.curr_ind, self.desired_rows, self.desired_cols
            )

            # overwrite for color test
            primary_bg = select_rgb_color(self.curr_ind, len(self.paste_dict) - 1)

            # make button
            button = create_palette_button(
                self.window,
                key,
                self.helv12,
                primary_bg,
                secondary_dark_grey,
                "black",
                paste_dict=self.paste_dict,
            )

            button.grid(row=curr_row, column=curr_col, sticky="NESW")

            self.button_arr.append(button)

            self.window.columnconfigure(curr_col, weight=1)
            self.window.rowconfigure(curr_row, weight=1)

            self.curr_ind += 1
        # endregion

        # region settings button
        # if there are more columns than rows, alternate fill direction
        curr_row, curr_col = get_palette_row_col(
            self.curr_ind, self.desired_rows, self.desired_cols
        )

        self.settings_button = create_palette_button(
            self.window,
            "Settings",
            self.helv12,
            secondary_dark_grey,
            primary_light_grey,
            settings_text_color,
            # handler=self.reload_palette_buttons,
            handler=self.open_settings_window,
        )
        self.settings_button.grid(row=curr_row, column=curr_col, sticky="NESW")

        self.window.columnconfigure(curr_col, weight=1)
        self.window.rowconfigure(curr_row, weight=1)

        self.button_arr.append(self.settings_button)

        # endregion


def lerp(a, b, t):
    return (1 - t) * a + t * b


# pick a color on a lerp from part to whole
def select_rgb_color(ind, n_opt):
    hue = ind / n_opt
    sat = 0.55
    val = 1
    rgb = colorsys.hsv_to_rgb(hue, sat, val)
    red = int(rgb[0] * 0xFF)
    green = int(rgb[1] * 0xFF)
    blue = int(rgb[2] * 0xFF)
    return "#%02x%02x%02x" % (red, green, blue)


# loads on startup
def load_paste_dict():
    loading_dict = {}

    dict_file = open("paste_dict.txt", "r")
    lines = dict_file.readlines()

    lineno = 1

    for line in lines:
        dict_entry = line.split("~")

        if len(dict_entry) < 2:
            print("***Note: line %d contains no '~' and will be ignored!!***")
            continue

        entry_key = dict_entry[0]
        entry_val = dict_entry[1].replace("\n", "")

        if len(dict_entry) > 2:
            print("***WARNING: line %d contains more than one '~' !!***")
            print(
                "***The key %s and value %s will be used!***" % (entry_key, entry_val)
            )

        loading_dict[entry_key] = entry_val

        lineno += 1

    dict_file.close()

    return loading_dict


# save user_prefs to a pickle file
def save_user_prefs(user_prefs):
    with open("user_prefs.pkl", "wb") as f:
        pickle.dump(user_prefs, f, pickle.HIGHEST_PROTOCOL)


def load_user_prefs():
    try:
        with open("user_prefs.pkl", "rb") as f:
            user_prefs = pickle.load(f)
    except:
        user_prefs = {}
    return user_prefs


if __name__ == "__main__":
    main_widow = TextPaletteWindow()

# TODO:
# Integrate with pyautogui, so if you press the z key or somethign, the mouse will SNAP BACK AND FOCUS ON THE FORM REQUESTeD  EVEN COPY FOR YOUU!!!

# TODO: pickle user prefs!

# TODO: caught a problem in trying to save - 'SettingsWindow' object has no attribute 'tell_parent_to_reload_buttons'

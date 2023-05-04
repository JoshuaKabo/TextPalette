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
primary_color = "#DDDDDD"
secondary_color = "#5A5A5A"
bright_text_color = "#FAFAFA"
settings_text_color = "#EEEE22"


# could theoretically store window size, num cols, etc
user_prefs = {}

desired_cols = 9


# NOTE! IMPORTANT! USE LAMBDA EXPRESSIONS OFTEN WHEN USING BUTTONS
# ESPECIALLY BECAUSE THEY DON'T PROBE THE ACTIONS FIRST, RESULTING IN AN EARLY RELOAD OR OTHER BROKEN BEHAVIOR!!
# ALSO THEY HELP SO MUCH WHEN PASSING DATA AROUND!!


def select_alternating_colors(use_primary):
    used_primary_bg = primary_color if use_primary else secondary_color
    used_secondary_bg = secondary_color if use_primary else primary_color
    used_text_color = "black" if use_primary else bright_text_color
    return used_primary_bg, used_secondary_bg, used_text_color


def create_palette_button(master, key, font, bg, activebackground, fg, paste_dict=NONE, handler=NONE):
    if (handler == NONE):
        return Button(master=master, text=key, font=font, bg=bg, width=13, height=5, activebackground=activebackground, fg=fg,
                      command=lambda key=key: pyperclip.copy(paste_dict[key]))
    else:
        return Button(master=master, text=key, font=font, bg=bg, width=13, height=5, activebackground=activebackground, fg=fg,
                      command=handler)


def create_palette_window(title="Text Palette", topmost=True):
    window = Tk()
    window.title(title)
    if (topmost):
        window.attributes('-topmost', True)
    return window


def prompt_remove_entry(paste_dict):

    remove_entry_window = create_palette_window("Remove An Entry")

    def retrieve_and_remove_selection(*args):
        remove_entry(names_list.get(names_list.curselection()[0]))

    def check_del_button_state(*args):
        try:
            if (names_list.curselection()[0] >= 0 and names_list.curselection()[0] < len(paste_dict)):
                del_entry_button.config(state=NORMAL)
        except:
            # no selection or other problem
            del_entry_button.config(state=DISABLED)

    # the list part of the scroll list
    # name_selection = StringVar()
    names_list = Listbox(remove_entry_window)
    names_list.grid(row=0, column=0, columnspan=2, sticky="WEN")

    # the scroll part
    scrollbar = Scrollbar(remove_entry_window)
    scrollbar.grid(row=0, column=1, sticky="SEN")

    # insert elems
    for key in paste_dict.keys():
        names_list.insert(END, key)

        # attach listbox to scrollbar
    names_list.config(yscrollcommand=scrollbar.set)

    # scrollbar command param
    scrollbar.config(command=names_list.yview)

    # bind for selection change to check if save should be greyed out
    names_list.bind('<ButtonRelease>', check_del_button_state)
    names_list.bind('<KeyRelease>', check_del_button_state)

    # create cancel button
    cancel_button = Button(master=remove_entry_window,
                           text="Cancel", command=remove_entry_window.destroy)
    cancel_button.grid(row=1, column=0)

    # create save changes button
    # save needs to reload the main window
    # it also needs to update in every possible place
    del_entry_button = Button(master=remove_entry_window,
                              text="Delete Entry", state=DISABLED, command=retrieve_and_remove_selection)
    del_entry_button.grid(row=1, column=1)

    remove_entry_window.mainloop()

    # cancel and save at the bottom
    # make save grey out unless something is selected


def prompt_add_entry(paste_dict):
    add_entry_window = create_palette_window("Add An Entry")

    def check_save_button_state(*args):
        if (len(name_entry.get()) > 0 and len(value_entry.get()) > 0):
            save_button.config(state=NORMAL)
        else:
            save_button.config(state=DISABLED)

    # region name
    name_label = Label(master=add_entry_window, text="Name:")
    name_label.grid(row=0, column=0, pady=10, padx=5, sticky="NESW")
    # Entry for name
    name_entry = Entry(master=add_entry_window)
    name_entry.grid(row=0, column=1, pady=10, padx=5, sticky="NESW")
    name_entry.bind('<KeyRelease>', check_save_button_state)
    # endregion

    # region value
    value_label = Label(master=add_entry_window, text="Entry:")
    value_label.grid(row=1, column=0, pady=10, padx=5, sticky="NESW")
    # Entry for value
    value_entry = Entry(master=add_entry_window)
    value_entry.grid(row=1, column=1, pady=10, padx=5, sticky="NESW")
    value_entry.bind('<KeyRelease>', check_save_button_state)
    # endregion

    # region save/cancel
    cancel_button = Button(master=add_entry_window,
                           text="Cancel", command=add_entry_window.destroy)
    cancel_button.grid(row=3, column=0, sticky="NESW")
    # save button:

    def save_entry():
        if (not name_entry.get() in paste_dict.keys()):
            write_addition_to_file(name_entry.get(), value_entry.get())
            add_entry_window.destroy()
            # TODO: reload somewhere here????
        else:
            messagebox.showerror(
                "ENTRY REJECTED", "Duplicate name entered! \nPlease enter a name that is not already in use!!")
    save_button = Button(master=add_entry_window,
                         text="Save changes", command=save_entry, state=DISABLED)
    save_button.grid(row=3, column=1, columnspan=1, sticky="NESW")
    # endregion

    add_entry_window.mainloop()


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
            if (not key in line.split("~")[0]):
                if (curr_ind != 0):
                    line = "\n"+line
                file_wt.write(line)
                curr_ind += 1


def handle_settings_window(paste_dict):
    settings_window = create_palette_window(title="Text Palette Settings")

    # create number of columns label and entry box
    num_cols_label = Label(master=settings_window, text="Number of columns:")
    num_cols_label.grid(row=0, column=0, pady=20, padx=5, sticky="NESW")
    num_cols_var = IntVar(value=3)
    num_cols_entry = Spinbox(master=settings_window,
                             from_=1, to=10, textvariable=num_cols_var)
    num_cols_entry.grid(row=0, column=1, pady=20, padx=5, sticky="NESW")

    # create add entry button
    add_entry_button = Button(master=settings_window,
                              text="+ Add entry", command=lambda: prompt_add_entry(paste_dict))
    add_entry_button.grid(row=2, column=0, pady=10, padx=5, sticky="NESW")

    # create remove entry button
    remove_entry_button = Button(master=settings_window,
                                 text="- Remove entry", command=lambda: prompt_remove_entry(paste_dict))
    remove_entry_button.grid(row=2, column=1, pady=10, padx=5, sticky="NESW")

    # create cancel button
    cancel_button = Button(master=settings_window,
                           text="Cancel", command=settings_window.destroy)
    cancel_button.grid(row=3, column=0, sticky="NESW")

    # create save changes button
    # save needs to reload the main window
    # TODO: reload on save!!
    save_button = Button(master=settings_window,
                         text="Save changes", command=lambda: prompt_add_entry(paste_dict))
    save_button.grid(row=3, column=1, sticky="NESW")

    settings_window.columnconfigure(0, weight=1)
    settings_window.columnconfigure(1, weight=1)
    for i in range(0, 4):
        settings_window.rowconfigure(i, weight=1)

    settings_window.mainloop()


def reload_buttons(buttonarr, window, helv12):

    use_primary = True

    for button in buttonarr:
        button.destroy()

    paste_dict = load_paste_dict()

    curr_ind = 0

    for key in paste_dict.keys():

        # handle positioning
        curr_col = curr_ind % desired_cols
        curr_row = math.floor(curr_ind / desired_cols)

        used_primary_bg, used_secondary_bg, used_text_color = select_alternating_colors(
            use_primary)

        # overwrite for color test
        used_primary_bg = (select_rgb_color(curr_ind, len(paste_dict)-1))

        # make button
        button = create_palette_button(window, key, helv12, used_primary_bg,
                                       used_secondary_bg, used_text_color, paste_dict=paste_dict)

        button.grid(row=curr_row, column=curr_col, sticky="NESW")

        buttonarr.append(button)

        window.columnconfigure(curr_col, weight=1)
        window.rowconfigure(curr_row, weight=1)

        curr_ind += 1

    return buttonarr, curr_ind


def main():

    window = create_palette_window()

    paste_dict = load_paste_dict()

    helv12 = tkFont.Font(family='Helvetica', size=12, weight='bold')

    # NOTE: regen buttons after an update happens (that way all the callbacks will behave the way I want them to.)
    use_primary = True

    used_primary_bg, used_secondary_bg, used_text_color = select_alternating_colors(
        use_primary)

    desired_cols = 9

    button_arr = []
    clearret = reload_buttons(button_arr, window, helv12)

    button_arr = clearret[0]
    curr_ind = clearret[1]

    curr_col = curr_ind % desired_cols
    curr_row = math.floor(curr_ind / desired_cols)

    used_primary_bg, used_secondary_bg, used_text_color = select_alternating_colors(
        use_primary)

    # overwrite for color test
    used_primary_bg = secondary_color

    settings_button = create_palette_button(window, "Settings", helv12, used_primary_bg,
                                            used_secondary_bg, settings_text_color, handler=lambda: handle_settings_window(paste_dict))
    settings_button.grid(row=curr_row, column=curr_col, sticky="NESW")

    window.columnconfigure(curr_col, weight=1)
    window.rowconfigure(curr_row, weight=1)

    window.mainloop()


def lerp(a, b, t):
    return (1-t) * a + t * b


# pick a color on a lerp from part to whole
def select_rgb_color(ind, n_opt):
    hue = ind/n_opt
    sat = 0.55
    val = 1
    rgb = colorsys.hsv_to_rgb(hue, sat, val)
    red = int(rgb[0] * 0xff)
    green = int(rgb[1] * 0xff)
    blue = int(rgb[2] * 0xff)
    return "#%02x%02x%02x" % (red, green, blue)


# loads on startup
def load_paste_dict():

    loading_dict = {}

    dict_file = open("paste_dict.txt", 'r')
    lines = dict_file.readlines()

    lineno = 1

    for line in lines:
        dict_entry = line.split("~")

        if (len(dict_entry) < 2):
            print("***Note: line %d contains no \'~\' and will be ignored!!***")
            continue

        entry_key = dict_entry[0]
        entry_val = dict_entry[1].replace("\n", "")

        if (len(dict_entry) > 2):
            print("***WARNING: line %d contains more than one \'~\' !!***")
            print(
                "***The key %s and value %s will be used!***" % (entry_key, entry_val))

        loading_dict[entry_key] = entry_val

        lineno += 1

    dict_file.close()

    return loading_dict


if __name__ == "__main__":
    main()

# TODO: draw columns down, and do a continuous loop of build, rather than disconnected as it is

# TODO:
# Integrate with pyautogui, so if you press the z key or somethign, the mouse will SNAP BACK AND FOCUS ON THE FORM REQUESTeD (MAYBE EVEN COPY FOR YOUU!!!)

# Modification flow:
# a request for insert / delete is made
# the file is updated
# the main display reloads its paste_dict
# the buttons reload

# TODO: create a warning when user attempts to create a duplicate key
# TODO: refresh main ui when appropriate !! Start with column update, that should be the easiest!
# TODO: column logic, cannot be more than num elements

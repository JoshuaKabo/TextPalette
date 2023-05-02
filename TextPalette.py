# pyperclip for write to clipboard, pickle for saving dictionaries
import pyperclip
import pickle
import math
import colorsys
from tkinter import *
from tkinter import font as tkFont

# theme constants
primary_color = "#DDDDDD"
secondary_color = "#5A5A5A"
bright_text_color = "#FAFAFA"
settings_text_color = "#EEEE22"

# TODO: text color difference detect to account for text on rainbow buttons


def select_alternating_colors(use_primary):
    used_primary_bg = primary_color if use_primary else secondary_color
    used_secondary_bg = secondary_color if use_primary else primary_color
    used_text_color = "black" if use_primary else bright_text_color
    return used_primary_bg, used_secondary_bg, used_text_color


def create_palette_button(master, key, font, bg, activebackground, fg, paste_dict=NONE, handler=NONE):
    if (handler == NONE):
        return Button(master=master, text=key, font=font, bg=bg, width=10, height=5, activebackground=activebackground, fg=fg,
                      command=lambda key=key: pyperclip.copy(paste_dict[key]))
    else:
        return Button(master=master, text=key, font=font, bg=bg, width=10, height=5, activebackground=activebackground, fg=fg,
                      command=handler)


def create_palette_window(title="Text Palette", topmost=True):
    window = Tk()
    window.title(title)
    if (topmost):
        window.attributes('-topmost', True)
    return window


def add_entry():
    pass


def remove_entry():
    pass


def handle_settings_window():
    settings_window = create_palette_window(title="Text Palette Settings")

    # create number of columns label and entry box
    num_cols_label = Label(master=settings_window, text="Number of columns:")
    num_cols_label.grid(row=0, column=0, sticky="NESW")
    num_cols_var = IntVar(value=3)
    num_cols_entry = Spinbox(master=settings_window,
                             from_=1, to=10, textvariable=num_cols_var)
    num_cols_entry.grid(row=0, column=1, sticky="NESW")

    # create text size label and entry box
    text_size_label = Label(master=settings_window, text="Text size:")
    text_size_label.grid(row=1, column=0, sticky="NESW")
    text_size_var = IntVar(value=12)
    text_size_entry = Spinbox(master=settings_window,
                              from_=8, to=24, textvariable=text_size_var)
    text_size_entry.grid(row=1, column=1, sticky="NESW")

    # create add entry button
    add_entry_button = Button(master=settings_window,
                              text="Add entry", command=add_entry)
    add_entry_button.grid(row=2, column=0, sticky="NESW")

    # create remove entry button
    remove_entry_button = Button(master=settings_window,
                                 text="Remove entry", command=remove_entry)
    remove_entry_button.grid(row=2, column=1, sticky="NESW")

    # create draw on top toggle
    draw_on_top_var = BooleanVar(value=False)
    draw_on_top_toggle = Checkbutton(master=settings_window,
                                     text="Draw on top", variable=draw_on_top_var)
    draw_on_top_toggle.grid(row=3, column=0, columnspan=2, sticky="NESW")

    # create cancel button
    add_entry_button = Button(master=settings_window,
                              text="Cancel", command=add_entry)
    add_entry_button.grid(row=4, column=0, sticky="NESW")

    # create save changes button
    # save needs to reload the main window
    # it also
    add_entry_button = Button(master=settings_window,
                              text="Save changes", command=add_entry)
    add_entry_button.grid(row=4, column=1, sticky="NESW")

    settings_window.columnconfigure(0, weight=1)
    settings_window.columnconfigure(1, weight=1)
    for i in range(0, 5):
        print(i)
        settings_window.rowconfigure(i, weight=1)

    settings_window.mainloop()


def main():

    window = create_palette_window()

    paste_dict = load_paste_dict()

    helv12 = tkFont.Font(family='Helvetica', size=12, weight='bold')

    # NOTE: regen buttons after an update happens (that way all the callbacks will behave the way I want them to.)
    use_primary = True

    used_primary_bg, used_secondary_bg, used_text_color = select_alternating_colors(
        use_primary)

    desired_cols = 9

    curr_ind = 0

    for key in paste_dict.keys():

        # handle positioning
        curr_col = curr_ind % desired_cols
        curr_row = math.floor(curr_ind / desired_cols)

        used_primary_bg, used_secondary_bg, used_text_color = select_alternating_colors(
            use_primary)

        # overwrite for color test
        print(select_rgb_color(curr_ind, len(paste_dict)-1))
        used_primary_bg = (select_rgb_color(curr_ind, len(paste_dict)-1))

        # make button
        button = create_palette_button(window, key, helv12, used_primary_bg,
                                       used_secondary_bg, used_text_color, paste_dict=paste_dict)

        button.grid(row=curr_row, column=curr_col, sticky="NESW")

        window.columnconfigure(curr_col, weight=1)
        window.rowconfigure(curr_row, weight=1)

        curr_ind += 1

    curr_col = curr_ind % desired_cols
    curr_row = math.floor(curr_ind / desired_cols)

    used_primary_bg, used_secondary_bg, used_text_color = select_alternating_colors(
        use_primary)

    # overwrite for color test
    used_primary_bg = secondary_color

    settings_button = create_palette_button(window, "Settings", helv12, used_primary_bg,
                                            used_secondary_bg, settings_text_color, handler=handle_settings_window)
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

# TODO: draw columns down, and do a continuous loop of build, rather than

# NOTE: deprecated grey button code (not going to implement so scope can stay small):
    # handle colors
    # if (desired_cols % 2 == 0):
    #     if (curr_col % 2 == 0):
    #         use_primary = curr_row % 2 == 0
    #     else:
    #         use_primary = curr_row % 2 == 1
    # else:
    #     use_primary = not use_primary

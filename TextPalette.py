# pyperclip for write to clipboard, pickle for saving dictionaries
import pyperclip
import pickle
from tkinter import *
from tkinter import font as tkFont

# theme constants
primary_color = "#DDDDDD"
secondary_color = "#5A5A5A"
bright_text_color = "#FAFAFA"
settings_text_color = "#EDF263"


def select_alternating_colors(use_primary):
    used_primary_bg = primary_color if use_primary else secondary_color
    used_secondary_bg = secondary_color if use_primary else primary_color
    used_text_color = "black" if use_primary else bright_text_color
    return used_primary_bg, used_secondary_bg, used_text_color


def create_palette_button(master, key, font, bg, activebackground, fg, paste_dict=NONE, handler=NONE):
    if (handler == NONE):
        return Button(master=master, text=key, font=font, bg=bg, activebackground=activebackground, fg=fg,
                      command=lambda key=key: pyperclip.copy(paste_dict[key]))
    else:
        return Button(master=master, text=key, font=font, bg=bg, activebackground=activebackground, fg=fg,
                      command=handler)


def handle_settings_window():
    settings_window = Tk()
    label = Label(master=settings_window,
                  text="hello this is the settings window!")
    label.pack()
    settings_window.mainloop()


def main():

    paste_dict = load_paste_dict()

    window = Tk()

    helv12 = tkFont.Font(family='Helvetica', size=12, weight='bold')

    # this window will have high priority, draw on top
    window.attributes('-topmost', True)

    # NOTE: regen buttons after an update happens (that way all the callbacks will behave the way I want them to.)
    use_primary = True

    used_primary_bg, used_secondary_bg, used_text_color = select_alternating_colors(
        use_primary)

    for key in paste_dict.keys():

        # make button
        button = create_palette_button(window, key, helv12, used_primary_bg,
                                       used_secondary_bg, used_text_color, paste_dict=paste_dict)
        button.pack(expand=1, fill="both")

        # handle colors
        use_primary = not use_primary
        used_primary_bg, used_secondary_bg, used_text_color = select_alternating_colors(
            use_primary)

    settings_button = create_palette_button(window, "Settings", helv12, used_primary_bg,
                                            used_secondary_bg, settings_text_color, handler=handle_settings_window)

    settings_button.pack(expand=1, fill="both")

    window.mainloop()


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


# I could have numrows, numcols, textsize (extras: ) add a thing, remove a thing, save to board, colors used, draw on top

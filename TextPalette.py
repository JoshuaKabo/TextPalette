# pyperclip for write to clipboard, pickle for saving dictionaries
import pyperclip
import pickle
from tkinter import *
from tkinter import font as tkFont


def main():
    paste_dict = load_paste_dict()

    window = Tk()

    # this window will have high priority, draw on top
    window.attributes('-topmost', True)

    helv36 = tkFont.Font(family='Helvetica', size=12, weight='bold')

    primary_color = "#DDDDDD"
    secondary_color = "#5A5A5A"

    # NOTE: regen buttons after an update happens (that way all the callbacks will behave the way I want them to.)
    use_primary = True
    for key in paste_dict.keys():
        button = Button(master=window, text=key, font=helv36, bg=primary_color if use_primary else secondary_color, activebackground=secondary_color if use_primary else primary_color,
                        command=lambda key=key: pyperclip.copy(paste_dict[key]))

        button.pack(expand=1, fill="both")
        use_primary = not use_primary

    settings_button = Button(master=window, text="Settings", font=helv36, bg=primary_color if use_primary else secondary_color, activebackground=secondary_color if use_primary else primary_color,
                             command=lambda key=key: pyperclip.copy(paste_dict[key]))

    button.pack(expand=1, fill="both")

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

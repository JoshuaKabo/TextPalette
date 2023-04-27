# pyperclip for write to clipboard, pickle for saving dictionaries
import pyperclip
import pickle
import tkinter as tk

paste_dict = {}

# gives the key for c


def main():
    paste_dict = load_paste_dict()

    window = tk.Tk()

    # this window will have high priority, draw on top
    window.attributes('-topmost', True)

    greeting = tk.Label(text="Hello Tkinter")
    greeting.pack()
    # NOTE: regen buttons after an update happens (that way all the callbacks will behave the way I want them to.)
    for key in paste_dict.keys():
        button = tk.Button(master=window, text=key,
                           command=lambda key=key: pyperclip.copy(paste_dict[key]))
        button.pack()

    window.mainloop()

# write the dict out to a file


def save_paste_dict(to_save):
    with open("paste_dict.pkl", "wb") as pickled_dict_file:
        pickle.dump(to_save, pickled_dict_file)

# # read the dict from the file


def load_paste_dict():
    with open("paste_dict.pkl", "rb") as pickled_dict_file:
        return pickle.load(pickled_dict_file)


if __name__ == "__main__":
    main()

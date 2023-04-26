# pyperclip for write to clipboard, pickle for saving dictionaries
import pyperclip
import pickle
import tkinter as tk

paste_dict = {"Test": "This is a test"}

# gives the key for c


def copyCallback(key):
    print("copy callback called with %s as the key!" % key)
    pass


def main():
    # print("Hopefully the clipboard should now have copy thing in it in it")
    # pyperclip.copy("this is the copy thing")
    window = tk.Tk()
    greeting = tk.Label(text="Hello Tkinter")
    greeting.pack()
    # button = tk.Button(
    #     text=
    # )
    for i in range(0, 5):
        button = tk.Button(master=window, text='button %d' % i,
                           command=lambda i=i: copyCallback("press keeyy %d" % i))
        button.pack()

    window.mainloop()

# # write the dict out to a file
# def save_paste_dict():
#     with open("paste_dict.pkl", "wb") as pickled_dict_file:
#         pickle.dump(paste_dict, pickled_dict_file)

# # read the dict from the file
# def load_paste_dict():
#     with open("paste_dict.pkl", "rb") as pickled_dict_file:
#         paste_dict = pickle.load(pickled_dict_file)


if __name__ == "__main__":
    main()

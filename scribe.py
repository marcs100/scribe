# This is a sample Python script.
import tkinter
from tkinter.constants import *
from database import database
import tkinter as tk
from tkinter import font
import columns as COLUMN
from note_window import NoteWindow
import constants as CONSTANTS
from main_window import MainWindow

def get_curr_screen_geometry():
    """
    Workaround to get the size of the current screen in a multi-screen setup.
    """
    root = tk.Tk()
    root.update_idletasks()
    root.attributes('-fullscreen', True)
    root.state('iconic')
    #geometry = root.winfo_geometry()
    width = root.winfo_width()
    height = root.winfo_height()
    root.destroy()
    return (width,height)



def main():
    init_main_window()
    # root.mainloop()


def init_main_window():
    geometry = get_curr_screen_geometry()
    width = round(geometry[0] * 0.9)
    height = round(geometry[1] * 0.9)
    print ("Width = " + str(width))
    print("Height = " + str(height))
    print(geometry)
    root.geometry(f'{width}x{height}')
    # root.geometry('1400x800')
    root.title(CONSTANTS.APP_TITLE)

    main_win = MainWindow(root,db)
    
    # set default view (will read this from stored settings)
    main_win.get_view("pinned")

    root.mainloop()

    
    #view_button.grid(row=0,column=0, padx=5)
    #view_label.grid(row=0, column=1)


#Global variables
db = database("/home/marc/Documents/marcnotes_db")
root = tk.Tk()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

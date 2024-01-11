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
import configparser
import os.path
import config_file as conf

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

    path = CONSTANTS.CONFIG_FILE
    check_file = os.path.isfile(path)

    if check_file == False:
        print("Config file not ... Creating new config")
        conf.create_new_config_file()
        print("Wrote new config" + CONSTANTS.CONFIG_FILE)
    else:
        print("Found config file " + CONSTANTS.CONFIG_FILE)

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

    db_file = conf.read('main', 'database')
    db = database(db_file)

    root.title(CONSTANTS.APP_TITLE)
    main_win = MainWindow(root,db)
    
    # set default view (will read this from stored settings)
    main_win.get_view(conf.read('main_window','default_view'))

    root.mainloop()

    
    #view_button.grid(row=0,column=0, padx=5)
    #view_label.grid(row=0, column=1)


config = configparser.ConfigParser()
#Global variables
db = ""
root = tk.Tk()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

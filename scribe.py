# This is a sample Python script.
import tkinter
from tkinter.constants import *
from database import database
import tkinter as tk
from tkinter import font
import columns as COLUMN
from note_window import NoteWindow
from main_window import MainWindow
import configparser
import os.path
import config_file as conf

def window_closed():
    width = str(root.winfo_width())
    height = str(root.winfo_height())
    conf.write_section('main_window','width',width,False)
    conf.write_section('main_window', 'height', height, True)
    root.destroy()


def main():

    config_file = "./scribe.config"
    check_file = os.path.isfile(config_file)

    if check_file == False:
        print("Config file not ... Creating new config")
        conf.create_new_config_file()
        print("Wrote new config" + config_file)
    else:
        print("Found config file " + config_file)

    init_main_window()
    # root.mainloop()

def init_main_window():
    #geometry = get_curr_screen_geometry()
    #width = round(geometry[0] * 0.9)
    #height = round(geometry[1] * 0.9)
    #print ("Width = " + str(width))
    #print("Height = " + str(height))
    #print(geometry)
    width = conf.read_section('main_window','width')
    height = conf.read_section('main_window','height')
    root.geometry(f'{width}x{height}')

    db_file = conf.read_section('main', 'database')
    db = database(db_file)

    root.title(conf.read_section('main', 'app_title'))
    main_win = MainWindow(root,db)
    
    # set default view  - read this from stored settings
    main_win.get_view(conf.read_section('main_window','default_view'))
    root.protocol("WM_DELETE_WINDOW", window_closed)

    root.mainloop()

    
    #view_button.grid(row=0,column=0, padx=5)
    #view_label.grid(row=0, column=1)


# config = configparser.ConfigParser()
#Global variables
db = ""
root = tk.Tk()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

#!/usr/bin/env python3
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
from app_config import Config
import configuration_file
import platform
from pathlib import Path
import version_info
import configuration_file
import track_open_notes as tracker
from tkinter import messagebox
import version_info


def window_closed():
    if len(tracker.get_opened_notes()) != 0 or tracker.get_new_note_count() > 0:
        #print("There are notes open, please close them first")
        messagebox.showwarning("Warning","There are still notes open, please close them first",parent=root)
        return
    width = str(root.winfo_width())
    height = str(root.winfo_height())
    conf.write_section('main window','width',width,False)
    conf.write_section('main window', 'height', height, True)
    root.destroy()

conf = None

def main():

    global config_file
    if(version_info.release==True):
        if platform.system() == 'Linux':
            config_file = str(Path.home())+"/.config/scribe/scribe.config"
        else:
            config_file = str(Path.home())+"/scribe.config"
    else:
        if platform.system() == 'Linux':
            print("**Warning** this is the development version")
            config_file = '/home/marc/source/scribe/scribe.config'
        else:
            print("**Warning** this is the development version")
            config_file = './scribe.config'
    #save the config file a setting (so it can be passed to scripts)
    configuration_file.set_config_file(config_file)

    global conf
    conf = Config(config_file)

    print(f"Using config file {config_file}")
    check_file = os.path.isfile(config_file)

    if check_file == False:
        print("Config file not found ... Creating new config")
        conf.create_new_config_file()
        print("Wrote new config" + config_file)
    else:
        print("Found config file " + config_file)

    init_main_window()
    # root.mainloop()

def init_main_window():
    width = conf.read_section('main window','width')
    height = conf.read_section('main window','height')
    root.geometry(f'{width}x{height}')

    db_file = conf.read_section('main', 'database')

    print(f"Using database {db_file}")

    #check if the database file exists, if not create an new scribe database.
    if os.path.isfile(db_file) is False:
        print("Database not found, it will now be created...")
        db = database(db_file)
        table1 = "create table if not exists marcnotes (id INTEGER PRIMARY KEY, notebook TEXT, tag TEXT,content TEXT, created TEXT,modified TEXT, pinned INTEGER,BGColour TEXT)"
        table2 = "create table if not exists notebookcovers (name TEXT,colour TEXT)"
        db.executeQuery(table1)
        db.executeQuery(table2)
        db.addToNotebookCovers("General", conf.read_section('colours', 'default notebook bg')) #we need at least one notebook to startt with
        print(f"Scribe database succesfully created: {db_file}")
    else:
        db = database(db_file)

    #root.iconbitmap(r"/home/marc/.local/bin/scribe/resources/notes.svg")

    if platform.system() == 'Linux':
         if(version_info.release==True):
            icon = tk.PhotoImage(file="~/.local/bin/scribe/resources/scribe_taskbar.png")
            # Set it as the window icon
            root.iconphoto(True, icon)


    root.title(f"Scribe {version_info.APP_VERSION}")
    main_win = MainWindow(root,db, conf)
    
    # set default view  - read this from stored settings
    root.protocol("WM_DELETE_WINDOW", window_closed)
    main_win.get_view(conf.read_section('main window','default view'))

    root.mainloop()



#Global variables
db = ""
root = tk.Tk()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

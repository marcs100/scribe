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
from app_config import Config
import configuration_file
import platform
from pathlib import Path
import version_info
import configuration_file
import track_open_notes as tracker
from tkinter import messagebox


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

    #----------------------------------------------------------------
    #Experimenting with database.searchWholeWords().
    #It uses a virtual table FTS5 table and the MATCH statement.
    #db = database("/home/marc/Documents/marcnotes_db")

    #normal search result
    #norm_results_num = db.getNumberOfSearchResults('#monkey')
    #print(f"number of normal results = {str(norm_results_num)}")

    #FST5 results with MATCH
    #The problem with the FST5 table for search is that it does not allow
    #strings with '#' e.g. '#debian' they give an error. Otherwise it works.

    #I could maybe go back to normal tables and just use like instead of MATCH.
    #e.g where content LIKE ' debian ' or content LIKE ' debian -
    #how do I do start of line and end of line that way though!'

    #FST5_results = db.searchWholeWordsFST5('#debian')
    #print(f"whole words results = {str(len(FST5_results))}")

    #results = db.searchWholeWords("#monkey")
    #print(f"whole words results = {str(len(results))}")
    #for result in results:
     #   print (result[COLUMN.CONTENT])

    #return

    #----------------------------------------------------------------



    init_main_window()
    # root.mainloop()

def init_main_window():
    #geometry = get_curr_screen_geometry()
    #width = round(geometry[0] * 0.9)
    #height = round(geometry[1] * 0.9)
    #print ("Width = " + str(width))
    #print("Height = " + str(height))
    #print(geometry)
    width = conf.read_section('main window','width')
    height = conf.read_section('main window','height')
    root.geometry(f'{width}x{height}')

    db_file = conf.read_section('main', 'database')
    db = database(db_file)

    print(f"Using database {db_file}")

    root.title(conf.read_section('main', 'app_title'))
    main_win = MainWindow(root,db, conf)
    
    # set default view  - read this from stored settings
    main_win.get_view(conf.read_section('main window','default view'))
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

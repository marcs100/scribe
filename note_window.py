from tkinter.constants import *
from database import database
import tkinter as tk
#from tkinter import ttk as ttk
import columns as COLUMN
import hashlib
import datetime
import config_file as conf
import note_attributes
#from main_window import MainWindow


class NoteWindow:

    def __init__(self, root, main_window):

        self.__note = None
        
        self.__attrib = note_attributes.NoteAttributes()  

        self.__init_window(root, main_window)
                           

    def __init_window(self, root, main_window):
        self._root_window = root
        self.__note_window = tk.Toplevel(self._root_window)
        self.__note_window.geometry('800x550')
       
        self.__main_window = main_window # This is a reference to the main view window so we can tell it to update views if notes gett added or removed

        self.__frame = tk.Frame(self.__note_window, bg=conf.read_section('colours', 'widget_bg'))

        self.__menu_frame = tk.Frame(self.__note_window, bg=conf.read_section('colours', 'widget_bg'))
        spacer_label = tk.Label(self.__menu_frame, text="       ", bg=conf.read_section('colours', 'widget_bg'),
                                fg=conf.read_section('colours', 'widget_text'))
        spacer_label2 = tk.Label(self.__menu_frame, text="       ", bg=conf.read_section('colours', 'widget_bg'),
                                fg=conf.read_section('colours', 'widget_text'))
        view_label = tk.Label(self.__menu_frame, text="dummy", bg=conf.read_section('colours', 'widget_bg'),
                              fg=conf.read_section('colours', 'widget_text'))
        spacer_label.pack(fill=Y, side='right')
        spacer_label2.pack(fill=Y, side='left')
        view_label.pack(fill=Y, side='right')

        self.__save_button = tk.Button(self.__menu_frame, bg=conf.read_section('colours', 'widget_bg'),
                                      fg=conf.read_section('colours', 'widget_text'), relief="flat", text="Save",
                                      command=self.__save_note)
        self.__save_button.pack(fill='y', side='left',  pady=2, padx=4)

        self.__delete_button = tk.Button(self.__menu_frame, bg=conf.read_section('colours', 'widget_bg'),
                                      fg=conf.read_section('colours', 'widget_text'), relief="flat", text="Delete",
                                      command=self.__delete_note)
        self.__delete_button.pack(fill='y', side='left',  pady=2, padx=2)

        self.__text_box = tk.Text(self.__frame, wrap=tk.WORD)
        self.__text_box.pack(fill='both', expand=TRUE)

        self.__menu_frame.pack(fill='both', expand=FALSE)
        self.__frame.pack(fill='both', expand=TRUE)


    def open_note(self, sqlid, db_in):
        self.__db = db_in 
        
        #determine if this is a new note or an existing note
        if sqlid == None:
            self.__attrib.id = 0
            self.__attrib.pinned= 0
            self.__attrib.new_note = True
            self.__attrib.notebook = conf.read_section('main', 'default_notebook')
            self.__attrib.colour = conf.read_section('colours','default_note_bg')
        else:
            self.__attrib.id = sqlid
            self.__attrib.new_note = False
            self.__note = self.__db.getNoteByID(self.__attrib.id)
            if self.__note is None:
                print("Note not found: sql id is" + self.__attrib.id)
                return
            self.__attrib.new_note = False
            self.__attrib.hash = hashlib.sha1(self.__note[0][COLUMN.CONTENT].encode('ascii', 'ignore')).hexdigest()

            self.__attrib.notebook= self.__note[0][COLUMN.NOTEBOOK]
            self.__attrib.colour = self.__note[0][COLUMN.BACK_COLOUR]
            self.__text_box['bg'] = self.__attrib.colour
            self.__attrib.content = self.__note[0][COLUMN.CONTENT]
            self.__text_box.insert(tk.END, self.__attrib.content)
            self.__attrib.pinned = self.__note[0][COLUMN.PINNED]
            self.__attrib.date_created = self.__note[0][COLUMN.CREATED]
            self.__attrib.date_modified = self.__note[0][COLUMN.MODIFIED]
            self.__attrib.tag = self.__note[0][COLUMN.TAG]
        
        self.__note_window.title("Notebook: " + self.__attrib.notebook)
        # to do ... update pinned widget here !!!!!!!!!

    def __save_note(self):
        #check hash to see if note has changed
        current_hash = hashlib.sha1(self.__text_box.get("1.0","end-1c")
                                    .encode('ascii', 'ignore')).hexdigest()

        if self.__attrib.new_note == True:
            print("Saving new note...")
            self.__attrib.date_created = datetime.datetime.now()
            self.__attrib.date_modified = self.__attrib.date_created
            # addNote(self, notebook, tag, contents, datestamp, pinnedStatus, backColour):
            self.__db.addNote(self.__attrib.notebook, self.__attrib.tag, self.__text_box.get("1.0",END), 
                              self.__attrib.date_created, self.__attrib.pinned, self.__attrib.colour)
            self.__new_note_flag = False
            return

        # We also need to check if the user has switched o a different notebook - not implemented yet!!!!!!!!
        if current_hash == self.__note_hash:
            print("Note has not changed")
            return
        
        print("Saving existing note with id " + str(self.__note[0][COLUMN.ID]))
        self.__attrib.date_modified = datetime.datetime.now()
        self.__db.updateNote(self.__note[0][COLUMN.ID], self.__attrib.notebook, self.__attrib.tag, 
                             self.__text_box.get("1.0",END), self.__attrib.date_modified, self.__attrib.pinned, self.__attrib.colour)
  
    def __delete_note(self):
        if(self.__attrib.new_note == False):
            # to do - need to put a warning here that note will be deleted

            print(f"Deleting note {self.__attrib.id}")
            self.__db.deleteNoteById(self.__attrib.id)

            #need to tell main window to update teh current view
            self.__main_window.update_currrent_view()

            #close the deleted note
            self.__note_window.destroy()


    def get_next_note(self):
        pass

    def get_previous_note(self):
        pass


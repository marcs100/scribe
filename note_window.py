from tkinter.constants import *
from database import database
import tkinter as tk
#from tkinter import ttk as ttk
import columns as COLUMN
import hashlib
import datetime
import config_file as conf
import note_attributes
from tkinter import colorchooser
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
        spacer_label3 = tk.Label(self.__menu_frame, text="  ", bg=conf.read_section('colours', 'widget_bg'),
                              fg=conf.read_section('colours', 'widget_text'))
        spacer_label.pack(fill=Y, side='right')
        spacer_label2.pack(fill=Y, side='left')
        spacer_label3.pack(fill=Y, side='right')

        self.__save_button = tk.Button(self.__menu_frame, bg=conf.read_section('colours', 'widget_bg'),
                                      fg=conf.read_section('colours', 'widget_text'), relief="flat", text="Save",
                                      command=self.__save_note)        

        self.__delete_button = tk.Button(self.__menu_frame, bg=conf.read_section('colours', 'widget_bg'),
                                      fg=conf.read_section('colours', 'widget_text'), relief="flat", text="Delete",
                                      command=self.__delete_note)
        
        self.__colour_button =  tk.Button(self.__menu_frame, bg=conf.read_section('colours', 'widget_bg'),
                                      fg=conf.read_section('colours', 'widget_text'), relief="flat", text="Colour",
                                      command=self.__get_colour)
        self.__pin_button = tk.Button(self.__menu_frame, bg=conf.read_section('colours', 'widget_bg'),
                                      fg=conf.read_section('colours', 'widget_text'), relief="flat", text="Pin",
                                      command=self.__toggle_pin)

         # Select notebook button
        self.__notebook_button = tk.Menubutton(self.__menu_frame, text="Notebook", relief="flat", 
                                           bg=conf.read_section('colours','widget_bg'), fg=conf.read_section('colours', 'widget_text'))
        self.__notebook_button.menu = tk.Menu(self.__notebook_button, bg=conf.read_section('colours','widget_bg'), fg=conf.read_section('colours', 'widget_text'))
        self.__notebook_button["menu"] = self.__notebook_button.menu

        self.__delete_button.pack(fill='y', side='right',  pady=2, padx=2)
        self.__notebook_button.pack(fill='y', side='left',pady=2, padx =4)
        self.__pin_button.pack(fill='y', side='left',  pady=2, padx=4)
        self.__save_button.pack(fill='y', side='left',  pady=2, padx=4)
        self.__colour_button.pack(fill='y', side='left',  pady=2, padx=4)


        self.__text_box = tk.Text(self.__frame, wrap=tk.WORD)
        self.__text_box.pack(fill='both', expand=TRUE)

        self.__menu_frame.pack(fill='both', expand=FALSE)
        self.__frame.pack(fill='both', expand=TRUE)


    def __populate_notebook_menu(self):
        notebooks = self.__db.getNotebookNames()
        for notebook in notebooks:
             notebook_str = str(notebook[0])
             self.__notebook_button.menu.add_command(label=notebook_str, command=lambda notebook_in=notebook_str: self.__select_notebook(notebook_in))
        

    def __select_notebook(self, notebook_in):
        if self.__attrib.notebook != notebook_in:
            self.__attrib.notebook = notebook_in
            print(notebook_in)
            self.__note_window.title("Notebook: " + self.__attrib.notebook)
            self.__attrib.modified = True # Set this so the change will be saved
    
    
    def open_note(self, sqlid, db_in):
        self.__db = db_in 

        self.__populate_notebook_menu()
        
        #determine if this is a new note or an existing note
        if sqlid == None:
            self.__attrib.id = 0
            self.__attrib.pinned= 0
            self.__pin_button['text'] = 'Pin'
            self.__attrib.new_note = True
            if self.__attrib.notebook == "":
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
            if self.__attrib.pinned == 0:
                self.__pin_button['text'] = 'Pin'
            else:
                self.__pin_button['text'] = 'Unpin'
            self.__attrib.date_created = self.__note[0][COLUMN.CREATED]
            self.__attrib.date_modified = self.__note[0][COLUMN.MODIFIED]
            self.__attrib.tag = self.__note[0][COLUMN.TAG]
        
        self.__note_window.title("Notebook: " + self.__attrib.notebook)
        self.__note_window.protocol("WM_DELETE_WINDOW", self.__close_note)

    # Note closing event
    def __close_note(self):
        self.__save_note()
        self.__note_window.destroy()
    
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
            self.__attrib.new_note = False
            self.__main_window.update_currrent_view()
            return

        # We also need to check if the user has switched o a different notebook - not implemented yet!!!!!!!!
        if (current_hash == self.__attrib.hash) and (self.__attrib.modified == False):
            print("Note has not changed")
            return
        
        print("Saving existing note with id " + str(self.__note[0][COLUMN.ID]))
        self.__attrib.date_modified = datetime.datetime.now()
        self.__db.updateNote(self.__note[0][COLUMN.ID], self.__attrib.notebook, self.__attrib.tag, 
                             self.__text_box.get("1.0",END), self.__attrib.date_modified, self.__attrib.pinned, self.__attrib.colour)
        self.__main_window.update_currrent_view()

    ###########################################################
    # pin button event to toggle pinned status for pinning and
    # unpinning notes
    ###########################################################
    def __toggle_pin(self):
        if self.__attrib.pinned == 0:
            #pin note
            self.__attrib.pinned = 1
            self.__pin_button['text'] = 'Unpin'
        else:
            #unpin note
            self.__attrib.pinned = 0
            self.__pin_button['text'] = 'Pin'
            pass
        self.__attrib.modified = True # note will get updated on save
        #self.__save_note()

  
    def __delete_note(self):
        if(self.__attrib.new_note == False):
            # to do - need to put a warning here that note will be deleted

            print(f"Deleting note {self.__attrib.id}")
            self.__db.deleteNoteById(self.__attrib.id)

            #need to tell main window to update teh current view
            self.__main_window.update_currrent_view()

            #close the deleted note
            self.__note_window.destroy()


    ##########################################################
    #Public facing function to override the default notebook
    #setting for new notes
    ##########################################################
    def set_notebook_name(self, notebook_name):
        self.__attrib.notebook = notebook_name

    def __get_colour(self):
        col = colorchooser.askcolor(title="Choose note colour", parent=self.__note_window)
        if col != (None,None):
            col = str(col[1])
            if self.__attrib.colour != col:
                self.__attrib.colour = col
                self.__text_box['bg'] = self.__attrib.colour 
                self.__attrib.modified = True
    
    def get_next_note(self):
        pass

    def get_previous_note(self):
        pass


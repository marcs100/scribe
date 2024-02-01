from tkinter.constants import *
from database import database
import tkinter as tk
#from tkinter import ttk as ttk
import columns as COLUMN
import hashlib
import datetime
import datetime_format
import config_file as conf
import note_attributes
from tkinter import colorchooser
from tkinter import messagebox


class NoteWindow:

    def __init__(self, root, main_window):

        self._note = None
        
        self._attrib = note_attributes.NoteAttributes()

        self._init_window(root, main_window)
                           
    #-------------------------------------
    # Initialise the main window
    #-------------------------------------
    def _init_window(self, root, main_window):
        self._root_window = root
        self._note_window = tk.Toplevel(self._root_window)
        mult_factor = int(conf.read_section('main','screen_scale'))
        width = 800 * mult_factor
        height = 550 * mult_factor
        geometry = f"{width}x{height}"
        self._note_window.geometry(geometry)
       
        self._main_window = main_window # This is a reference to the main view window so we can tell it to update views if notes gett added or removed

        self._frame = tk.Frame(self._note_window, bg=conf.read_section('colours', 'widget_bg'))

        self._menu_frame = tk.Frame(self._note_window, bg=conf.read_section('colours', 'widget_bg'))
        spacer_label = tk.Label(self._menu_frame, text="       ", bg=conf.read_section('colours', 'widget_bg'),
                                fg=conf.read_section('colours', 'widget_text'))
        spacer_label2 = tk.Label(self._menu_frame, text="       ", bg=conf.read_section('colours', 'widget_bg'),
                                fg=conf.read_section('colours', 'widget_text'))
        spacer_label3 = tk.Label(self._menu_frame, text="  ", bg=conf.read_section('colours', 'widget_bg'),
                              fg=conf.read_section('colours', 'widget_text'))
        spacer_label.pack(fill=Y, side='right')
        spacer_label2.pack(fill=Y, side='left')
        spacer_label3.pack(fill=Y, side='right')

        self._revert_button = tk.Button(self._menu_frame, bg=conf.read_section('colours', 'widget_bg'),
                                      fg=conf.read_section('colours', 'widget_text'), relief="flat", text="Revert",
                                      command=self._revert_text)

        self._delete_button = tk.Button(self._menu_frame, bg=conf.read_section('colours', 'widget_bg'),
                                      fg=conf.read_section('colours', 'widget_text'), relief="flat", text="Delete",
                                      command=self._delete_note)
        
        self._colour_button =  tk.Button(self._menu_frame, bg=conf.read_section('colours', 'widget_bg'),
                                      fg=conf.read_section('colours', 'widget_text'), relief="flat", text="Colour",
                                      command=self._get_colour)
        self._pin_button = tk.Button(self._menu_frame, bg=conf.read_section('colours', 'widget_bg'),
                                      fg=conf.read_section('colours', 'widget_text'), relief="flat", text="Pin",
                                      command=self._toggle_pin)

         # Select notebook button
        self._notebook_button = tk.Menubutton(self._menu_frame, text="Notebook", relief="flat",
                                           bg=conf.read_section('colours','widget_bg'), fg=conf.read_section('colours', 'widget_text'))
        self._notebook_button.menu = tk.Menu(self._notebook_button, bg=conf.read_section('colours','widget_bg'), fg=conf.read_section('colours', 'widget_text'))
        self._notebook_button["menu"] = self._notebook_button.menu

        self._delete_button.pack(fill='y', side='right',  pady=2, padx=2)
        self._notebook_button.pack(fill='y', side='left',pady=2, padx =4)
        self._pin_button.pack(fill='y', side='left',  pady=2, padx=4)
        self._revert_button.pack(fill='y', side='left',  pady=2, padx=4)
        self._colour_button.pack(fill='y', side='left',  pady=2, padx=4)

        self._text_box = tk.Text(self._frame, wrap=tk.WORD)

        #assign right click event so we can bring up a contaxt menu
        self._text_box.bind('<Button-3>', lambda event: self._right_clicked_note(event))
        self._text_box.pack(fill='both', expand=TRUE)

        self._menu_frame.pack(fill='both', expand=FALSE)
        self._frame.pack(fill='both', expand=TRUE)

    #---------------------------------------------------------------
    # Read all available notebooks and add the entries to a menu.
    #--------------------------------------------------------------
    def _populate_notebook_menu(self):
        notebooks = self._db.getNotebookNames()
        for notebook in notebooks:
             notebook_str = str(notebook[0])
             self._notebook_button.menu.add_command(label=notebook_str, command=lambda notebook_in=notebook_str: self._select_notebook(notebook_in))
        

    #---------------------------------------------------------
    # Allows use to change the notbook name for current note.
    #---------------------------------------------------------
    def _select_notebook(self, notebook_in):
        if self._attrib.notebook != notebook_in:
            self._attrib.notebook = notebook_in
            print(notebook_in)
            self._note_window.title("Notebook: " + self._attrib.notebook)
            self._attrib.modified = True # Set this so the change will be saved
    
    
    #--------------------------------------------------------------------
    # Open and display a new note or an existing note based on sql id.
    #--------------------------------------------------------------------
    def open_note(self, sqlid, db_in):
        self._db = db_in

        self._populate_notebook_menu()
        
        #determine if this is a new note or an existing note
        if sqlid == None:
            self._attrib.id = 0
            self._attrib.pinned= 0
            self._pin_button['text'] = 'Pin'
            self._attrib.new_note = True
            if self._attrib.notebook == "":
                self._attrib.notebook = conf.read_section('main', 'default_notebook')
            self._attrib.colour = conf.read_section('colours','default_note_bg')
        else:
            self._attrib.id = sqlid
            self._attrib.new_note = False
            self._note = self._db.getNoteByID(self._attrib.id)
            if self._note is None:
                print("Note not found: sql id is" + self._attrib.id)
                return
            self._attrib.new_note = False
            self._attrib.hash = hashlib.sha1(self._note[0][COLUMN.CONTENT].encode('ascii', 'ignore')).hexdigest()

            self._attrib.notebook= self._note[0][COLUMN.NOTEBOOK]
            self._attrib.colour = self._note[0][COLUMN.BACK_COLOUR]
            self._text_box['bg'] = self._attrib.colour
            self._attrib.content = self._note[0][COLUMN.CONTENT]
            self._text_box.insert(tk.END, self._attrib.content)
            self._attrib.pinned = self._note[0][COLUMN.PINNED]
            if self._attrib.pinned == 0:
                self._pin_button['text'] = 'Pin'
            else:
                self._pin_button['text'] = 'Unpin'
            self._attrib.date_created = self._note[0][COLUMN.CREATED]
            self._attrib.date_modified = self._note[0][COLUMN.MODIFIED]
            self._attrib.tag = self._note[0][COLUMN.TAG]
        
        self._note_window.title("Notebook: " + self._attrib.notebook)
        self._note_window.protocol("WM_DELETE_WINDOW", self._close_note)

    #------------------------------
    # Note closing event
    #-----------------------------
    def _close_note(self):
        self._save_note()
        self._note_window.destroy()
    

    #-------------------------------------------------------------
    # Save the current note if is is a new note or a chnage to the
    # note has been detected.
    #-------------------------------------------------------------
    def _save_note(self):
        #check hash to see if note has changed
        current_hash = hashlib.sha1(self._text_box.get("1.0","end-1c")
                                    .encode('ascii', 'ignore')).hexdigest()

        if self._attrib.new_note == True:
            #print(f"note content: <{self._text_box.get('1.0',END)}>")
            if self._text_box.get("1.0",END) != '\n': # don't save an empty new note'
                print("Saving new note...")
                self._attrib.date_created = datetime.datetime.now()
                self._attrib.date_modified = self._attrib.date_created
                # addNote(self, notebook, tag, contents, datestamp, pinnedStatus, backColour):
                self._db.addNote(self._attrib.notebook, self._attrib.tag, self._text_box.get("1.0",END),
                              self._attrib.date_created, self._attrib.pinned, self._attrib.colour)
                self._attrib.new_note = False
                self._main_window.update_current_view()
                return
            return

        # We also need to check if the user has switched o a different notebook - not implemented yet!!!!!!!!
        if (current_hash == self._attrib.hash) and (self._attrib.modified == False):
            print("Note has not changed")
            return
        
        print("Saving existing note with id " + str(self._note[0][COLUMN.ID]))
        self._attrib.date_modified = datetime.datetime.now()
        self._db.updateNote(self._note[0][COLUMN.ID], self._attrib.notebook, self._attrib.tag,
                             self._text_box.get("1.0",END), self._attrib.date_modified, self._attrib.pinned, self._attrib.colour)
        self._main_window.update_current_view()

    #--------------------------------------------------------------
    # Pin button event to toggle pinned status for pinning and
    # unpinning notes
    #--------------------------------------------------------------
    def _toggle_pin(self):
        if self._attrib.pinned == 0:
            #pin note
            self._attrib.pinned = 1
            self._pin_button['text'] = 'Unpin'
        else:
            #unpin note
            self._attrib.pinned = 0
            self._pin_button['text'] = 'Pin'
            pass
        self._attrib.modified = True # note will get updated on save
        #self._save_note()

    #-------------------------------------------------------
    # Revert text to the original as saved in the database.
    #-------------------------------------------------------
    def _revert_text(self):
        if self._attrib.new_note == False:
            #if it is not a new note then we shoul dhave the note id.
            original_note = self._db.getNoteByID(self._attrib.id)
            self._attrib.content = original_note[0][COLUMN.CONTENT]
            self._text_box.delete('1.0', END)
            self._text_box.insert(tk.END, self._attrib.content)


    #----------------------------------------------------------------
    # Delete the current note (after confirmation).
    #----------------------------------------------------------------
    def _delete_note(self):
        if(self._attrib.new_note == False):
            # to do - need to put a warning here that note will be deleted
            if  messagebox.askyesno("Delete Note",
                                    "Are you sure you want to delete this note?",
                                    parent=self._note_window) == True:
                print(f"Deleting note {self._attrib.id}")
                self._db.deleteNoteById(self._attrib.id)

                #need to tell main window to update teh current view
                self._main_window.update_current_view()

                #close the deleted note
                self._note_window.destroy()

    #-------------------------------------------------------
    # Dsiplay a window showing current note properties
    #-------------------------------------------------------
    def _show_note_properties(self):
        properties_window = tk.Toplevel(self._note_window)
        properties_window.title('Properties')
        mult_factor = int(conf.read_section('main','screen_scale'))
        width = 400 * mult_factor
        height = 220 * mult_factor
        geometry = f"{width}x{height}"
        properties_window.geometry(geometry)
        text_box = tk.Text(properties_window,bg=self._attrib.colour,
                           wrap=tk.WORD)
        text_box.insert(tk.END,"\n\n    ------------------------------------------\n")
        text_box.insert(tk.END,f"     Note id: {str(self._attrib.id)}\n")
        text_box.insert(tk.END,f"     Belongs to notebook: {self._attrib.notebook}\n\n")
        text_box.insert(tk.END,f"     Date Created:  {datetime_format.get_long_datetime(self._attrib.date_created)}\n")
        text_box.insert(tk.END,f"     Date Modified: {datetime_format.get_long_datetime(self._attrib.date_modified)}\n")
        text_box.insert(tk.END,"    ------------------------------------------")
        text_box.pack(fill='both', expand='true')
        text_box['state'] = 'disabled'


    #----------------------------------------------------------
    #Public facing function to override the default notebook
    #setting for new notes
    #----------------------------------------------------------
    def set_notebook_name(self, notebook_name):
        self._attrib.notebook = notebook_name

    def _get_colour(self):
        col = colorchooser.askcolor(title="Choose note colour", parent=self._note_window)
        if col != (None,None):
            col = str(col[1])
            if self._attrib.colour != col:
                self._attrib.colour = col
                self._text_box['bg'] = self._attrib.colour
                self._attrib.modified = True
    

    #--------------------------------------------------------------
    # event when user right clicks the current note.
    # Present a context menu.
    #--------------------------------------------------------------
    def _right_clicked_note(self, event):
        #create a contaxt menu
        menu = tk.Menu(self._frame, tearoff = 0)
        menu.add_command(label ="Properties", command=self._show_note_properties)
        menu.tk_popup(event.x_root, event.y_root)

    def get_next_note(self):
        pass

    def get_previous_note(self):
        pass


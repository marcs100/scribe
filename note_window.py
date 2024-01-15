from tkinter.constants import *
from database import database
import tkinter as tk
import columns as COLUMN
import constants as CONSTANTS
import hashlib
import datetime
#from main_window import MainWindow


class NoteWindow:

    def __init__(self, root, main_window):

        self.__note_window = None
        self._root_window = root
        self.__note_window = tk.Toplevel(self._root_window)
        self.__note_window.geometry('800x550')
        self.__note = None
        self.__note_hash = None
        self.__sql_id = None
        self.__current_notebook = None
        self.__main_window = main_window # This is a reference to the main view window so we can tell it to update views if notes gett added or removed

        self.__frame = tk.Frame(self.__note_window, bg=CONSTANTS.WIDGET_BACK_COLOUR)

        self.__menu_frame = tk.Frame(self.__note_window, bg=CONSTANTS.WIDGET_BACK_COLOUR)
        spacer_label = tk.Label(self.__menu_frame, text="       ", bg=CONSTANTS.WIDGET_BACK_COLOUR,
                                fg=CONSTANTS.WIDGET_TEXT_COLOUR)
        spacer_label2 = tk.Label(self.__menu_frame, text="       ", bg=CONSTANTS.WIDGET_BACK_COLOUR,
                                fg=CONSTANTS.WIDGET_TEXT_COLOUR)
        view_label = tk.Label(self.__menu_frame, text="dummy", bg=CONSTANTS.WIDGET_BACK_COLOUR,
                              fg=CONSTANTS.WIDGET_TEXT_COLOUR)
        spacer_label.pack(fill=Y, side='right')
        spacer_label2.pack(fill=Y, side='left')
        view_label.pack(fill=Y, side='right')

        self.__save_button = tk.Button(self.__menu_frame, bg=CONSTANTS.WIDGET_BACK_COLOUR,
                                      fg=CONSTANTS.WIDGET_TEXT_COLOUR, relief="flat", text="Save",
                                      command=self.__save_note)
        self.__save_button.pack(fill='y', side='left',  pady=2, padx=4)

        self.__delete_button = tk.Button(self.__menu_frame, bg=CONSTANTS.WIDGET_BACK_COLOUR,
                                      fg=CONSTANTS.WIDGET_TEXT_COLOUR, relief="flat", text="Delete",
                                      command=self.__delete_note)
        self.__delete_button.pack(fill='y', side='left',  pady=2, padx=2)

        self.__text_box = tk.Text(self.__frame, wrap=tk.WORD)
        self.__text_box.pack(fill='both', expand=TRUE)

        self.__menu_frame.pack(fill='both', expand=FALSE)
        self.__frame.pack(fill='both', expand=TRUE)
        self.__new_note_flag = False

    def open_note(self, sqlid, db_in):
        self.__sql_id = sqlid
        self.__db = db_in

        self.__note = self.__db.getNoteByID(self.__sql_id)
        if self.__note is None:
            print("Note not found: sql id is" + self.__sql_id)
            return

        # save the initial hash of the note contents
        self.__note_hash = hashlib.sha1(self.__note[0][COLUMN.CONTENT].encode('ascii', 'ignore')).hexdigest()

        self.__current_notebook = self.__note[0][COLUMN.NOTEBOOK]
        self.__note_window.title("Notebook: " + self.__current_notebook)
        self.__text_box['bg'] = self.__note[0][COLUMN.BACK_COLOUR]
        self.__text_box.insert(tk.END, self.__note[0][COLUMN.CONTENT])

    def __save_note(self):
        #check hash to see if note has changed
        current_hash = hashlib.sha1(self.__text_box.get("1.0","end-1c")
                                    .encode('ascii', 'ignore')).hexdigest()

        if self.__new_note_flag == True:
            print("Saving new note...")
            # update the database here !!!!!!!!!!!!!!!!!!!
            self.__new_note_flag = False
            return

        # We also need to check if the user has switched o a different notebook - not implemented yet!!!!!!!!
        if current_hash == self.__note_hash:
            print("Note has not changed")
            return
        
        print("Saving existing note with id " + str(self.__note[0][COLUMN.ID]))
        modified = datetime.now()
        self.__db.updateNote(self.__note[0][COLUMN.ID], self.__current_notebook, self.__note[0][COLUMN.TAG], self.__text_box.get("1.0",END), modified, self._pinned, self._bg_colour)
  
    def __delete_note(self):
        if(self.__new_note_flag == False):

            # to do - need to put a warning here that note will be deleted

            print(f"Deleting note {self.__sql_id}")
            self.__db.deleteNoteById(self.__sql_id)

            #need to tell main window to update teh current view
            self.__main_window.update_currrent_view()

            #close the deleted note
            self.__note_window.destroy()


    def get_next_note(self):
        pass

    def get_previous_note(self):
        pass


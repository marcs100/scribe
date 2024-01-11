from tkinter.constants import *
from database import database
import tkinter as tk
import columns as COLUMN
import constants as CONSTANTS
import hashlib
import datetime

class NoteWindow:

    def __init__(self, root):

        self._note_window = None
        self._root_window = root
        self._note_window = tk.Toplevel(self._root_window)
        self._note_window.geometry('800x550')
        self._note = None
        self._note_hash = None
        self._sql_id = None
        self._current_notebook = None

        self._frame = tk.Frame(self._note_window, bg=CONSTANTS.WIDGET_BACK_COLOUR)

        self._menu_frame = tk.Frame(self._note_window, bg=CONSTANTS.WIDGET_BACK_COLOUR)
        spacer_label = tk.Label(self._menu_frame, text="       ", bg=CONSTANTS.WIDGET_BACK_COLOUR,
                                fg=CONSTANTS.WIDGET_TEXT_COLOUR)
        spacer_label2 = tk.Label(self._menu_frame, text="       ", bg=CONSTANTS.WIDGET_BACK_COLOUR,
                                fg=CONSTANTS.WIDGET_TEXT_COLOUR)
        view_label = tk.Label(self._menu_frame, text="dummy", bg=CONSTANTS.WIDGET_BACK_COLOUR,
                              fg=CONSTANTS.WIDGET_TEXT_COLOUR)
        spacer_label.pack(fill=Y, side='right')
        spacer_label2.pack(fill=Y, side='left')
        view_label.pack(fill=Y, side='right')

        self._save_button = tk.Button(self._menu_frame, bg=CONSTANTS.WIDGET_BACK_COLOUR,
                                      fg=CONSTANTS.WIDGET_TEXT_COLOUR, relief="flat", text="Save",
                                      command=self.__save_note)
        self._save_button.pack(fill='y', side='left',  pady=2, padx=4)

        self._text_box = tk.Text(self._frame, wrap=tk.WORD)
        self._text_box.pack(fill='both', expand=TRUE)

        self._menu_frame.pack(fill='both', expand=FALSE)
        self._frame.pack(fill='both', expand=TRUE)

    def open_note(self, sqlid, db_in):
        self._sql_id = sqlid
        self._db = db_in

        self._note = self._db.getNoteByID(self._sql_id)
        if self._note is None:
            print("Note not found: sql id is" + self._sql_id)
            return

        # save the initial hash of the note contents
        self._note_hash = hashlib.sha1(self._note[0][COLUMN.CONTENT].encode('ascii', 'ignore')).hexdigest()

        self._current_notebook = self._note[0][COLUMN.NOTEBOOK]
        self._note_window.title("Notebook: " + self._current_notebook)
        self._text_box['bg'] = self._note[0][COLUMN.BACK_COLOUR]
        self._text_box.insert(tk.END, self._note[0][COLUMN.CONTENT])

    def __save_note(self):
        #check hash to see if note has changed
        current_hash = hashlib.sha1(self._text_box.get("1.0","end-1c")
                                    .encode('ascii', 'ignore')).hexdigest()

        if self._new_note_flag is True:
            print("Saving new note...")
            # update the database here !!!!!!!!!!!!!!!!!!!
            self._new_note_flag = False
            return

        # We also need to check if the user has switched o a different notebook - not implemented yet!!!!!!!!
        if current_hash == self._note_hash:
            print("Note has not changed")
            return
        
        print("Saving existing note with id " + str(self._note[0][COLUMN.ID]))
        modified = datetime.now()
        self._db.updateNote(self._note[0][COLUMN.ID], self._current_notebook, self._note[0][COLUMN.TAG], self._text_box.get("1.0",END), modified, self._pinned, self._bg_colour)
  


    def get_next_note(self):
        pass

    def get_previous_note(self):
        pass


import tkinter
from tkinter.constants import *
from database import database
import tkinter as tk
from tkinter import font
import columns as COLUMN
from note_window import NoteWindow
import constants as CONSTANTS

class MainWindow:
    def __init__(self, root, database):
        self.__root = root
        self.__db = database
        self.__frame = tk.Frame(self.__root,bg=CONSTANTS.WIDGET_BACK_COLOUR)
        self.__menu_frame = tk.Frame(self.__root, bg=CONSTANTS.WIDGET_BACK_COLOUR)
        self.__view_button = tk.Menubutton(self.__menu_frame, text="Select View", relief="flat", bg=CONSTANTS.WIDGET_BACK_COLOUR, fg=CONSTANTS.WIDGET_TEXT_COLOUR)
        self.__view_label = tk.Label(self.__menu_frame,text="dummy",bg=CONSTANTS.WIDGET_BACK_COLOUR, fg=CONSTANTS.WIDGET_TEXT_COLOUR)
        self.init_window()

    def init_window(self):
        print("In MainWindow.init_window.....")
        self.__lbl_font = font.Font(weight="bold")
        self.__view_label["font"] = self.__lbl_font

        menu = tk.Menubutton()
        self.__view_button.menu = tk.Menu(self.__view_button, bg=CONSTANTS.WIDGET_BACK_COLOUR, fg=CONSTANTS.WIDGET_TEXT_COLOUR)
        self.__view_button["menu"] = self.__view_button.menu

        self.__view_button.menu.add_command(label="Pinned", command=lambda view="pinned": self.get_view(view))
        self.__view_button.menu.add_command(label="Notebooks", command=lambda view="notebooks": self.get_view(view))
        self.__view_button.menu.add_command(label="Recent Notes", command=lambda view="recent": self.get_view(view))

        spacer_label = tk.Label(self.__menu_frame, text="          ", bg=CONSTANTS.WIDGET_BACK_COLOUR, fg=CONSTANTS.WIDGET_TEXT_COLOUR)

        self.__menu_frame.pack(fill='both', expand=FALSE)
        self.__frame.pack(fill='both', expand=TRUE)
        self.__view_label.pack(fill=Y, side='right', padx=15, pady=6)
        spacer_label.pack(fill=Y, side='right')
        self.__view_button.pack(fill=Y, side='right')
        print("leaving MainWindow.init_window.....")

        # self.__root.mainloop()

    def clear_frame(self):
        for widgets in self.__frame.winfo_children():
                widgets.destroy()

    def __clicked_note(self,event,sqlid):
        print("note id is " + str(sqlid))
        # open note for editing in new window
        note_window = NoteWindow(self.__root)
        note_window.open_note(sqlid, self.__db)

    def __clicked_notebook(self,event, name):
        print("notebook name is " + str(name))
        self.__get_note_pages_view(3, name)



    def get_view(self,view):
        print("Getting view: "+view)
        match view:
            case 'pinned':
                # I want to set the menu button checkbox thing here!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                self.__get_pinned_notes_view(3)
            case 'recent':
                self.__get_recent_notes_view(3)
            case 'notebooks':
                self.__get_notebooks_view(3)

    def __get_note_pages_view(self, number_of_columns, notebook):
        self.clear_frame()
        self.__view_label["text"] = "Viewing Notebook: " + notebook
        note_pages = self.__db.getNotebook(notebook)
        if note_pages is None:
            print("No pinned notes found")
            return

        col = 0
        row = 0
        max_col = number_of_columns - 1
        num_widgets_in_row = 1
        for note_page in note_pages:
            note_id = note_page[COLUMN.ID]
            self.__text_box = tk.Text(self.__frame, height=15, width=50, wrap=tk.WORD, bg=note_page[COLUMN.BACK_COLOUR])
            self.__text_box.insert(tk.END, note_page[COLUMN.CONTENT])
            self.__text_box.bind('<Double-1>', lambda event, sqlid=note_id: self.__clicked_note(event, sqlid))
            self.__text_box.grid(row=row, column=col, pady=3, padx=3)
            if col == max_col:
                col = 0
                row += num_widgets_in_row
            else:
                col += 1

    def __get_notebooks_view(self, number_of_columns):
        self.clear_frame()
        self.__view_label["text"] = "Viewing: Notebooks"
        col=0
        row=0
        max_col = number_of_columns-1
        num_widgets_in_row = 1
        notebook_names = self.__db.getNotebookNames()
        if notebook_names is None:
            print("No notebooks found!")
            return
        for notebook_name in notebook_names:
            print("Notebook name is " + str(notebook_name[0]))
            colour = self.__db.getNotebookColour(notebook_name[0])
            self.__text_box = tk.Text(self.__frame, height=5, width=30, wrap=tk.WORD, bg=colour)
            self.__text_box.insert(tk.END, str(notebook_name[0]))
            self.__text_box.bind('<Double-1>', lambda event,name=str(notebook_name[0]): self.__clicked_notebook(event,name))
            self.__text_box.grid(row=row, column=col, pady=3, padx=3)

            if col == max_col:
                col = 0
                row += num_widgets_in_row
            else:
                col += 1


    def __get_recent_notes_view(self, number_of_columns):
        self.clear_frame()
        self.__view_label["text"] = "Viewing: Recent Notes"
        recent_notes = self.__db.getRecentNotes(4)
        if recent_notes is None:
            print("No recent notes found")
            return 

        col=0
        row=0
        max_col = number_of_columns-1
        num_widgets_in_row = 1

        for recent_note in recent_notes:
            print("pinned note id is " + str(recent_note[COLUMN.ID]))
            note_id = recent_note[COLUMN.ID]
            self.__text_box = tk.Text(self.__frame, height=15, width=50, wrap=tk.WORD, bg=recent_note[COLUMN.BACK_COLOUR])
            self.__text_box.insert(tk.END, recent_note[COLUMN.CONTENT])
            self.__text_box.bind('<Double-1>', lambda event,sqlid=note_id: self.__clicked_note(event,sqlid))
            self.__text_box.grid(row=row, column=col, pady=3, padx=3)

            print("row = " + str(row)+ " column = "+ str(col))

            if col == max_col:
                col = 0
                row += num_widgets_in_row
            else:
                col += 1


    def __get_pinned_notes_view(self, number_of_columns):
        self.clear_frame()
        self.__view_label["text"] = "Viewing: Pinned Notes"
        pinned_notes = self.__db.getPinnedNotes()
        if pinned_notes is None:
            print("No pinned notes found")
            return 

        col = 0
        row = 0
        max_col = number_of_columns-1
        num_widgets_in_row = 1
        for pinned_note in pinned_notes:
            print("pinned note id is " + str(pinned_note[COLUMN.ID]))
            note_id = pinned_note[COLUMN.ID]
            self.__text_box = tk.Text(self.__frame, height=15, width=50, wrap=tk.WORD, bg=pinned_note[COLUMN.BACK_COLOUR])
            self.__text_box.insert(tk.END, pinned_note[COLUMN.CONTENT])
            self.__text_box.bind('<Double-1>', lambda event, sqlid=note_id: self.__clicked_note(event, sqlid))
            self.__text_box.grid(row=row, column=col, pady=3, padx=3)
            if col == max_col:
                col = 0
                row += num_widgets_in_row
            else:
                col += 1

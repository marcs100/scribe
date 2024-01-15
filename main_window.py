import tkinter
from tkinter.constants import *
from database import database
import tkinter as tk
from tkinter import font
import columns as COLUMN
from note_window import NoteWindow
import constants as CONSTANTS
import config_file as conf

class MainWindow:
    def __init__(self, root, database_in):
        self.__root = root
        self.__db = database_in
        self.__main_frame = tk.Frame(self.__root,bg=CONSTANTS.WIDGET_BACK_COLOUR) # this frame is to hold the canvass for the scrollbar
        
        self.__menu_frame = tk.Frame(self.__root, bg=CONSTANTS.WIDGET_BACK_COLOUR)
        
        #Adding a scrollbar is tricky in tkinter!!!!!!
        self.__canvas = tk.Canvas(self.__main_frame)
        self.__canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.__scrollbar = tk.Scrollbar(self.__main_frame, orient=VERTICAL, command=self.__canvas.yview)
        self.__scrollbar.pack(side=RIGHT, fill=Y)
        self.__canvas.configure(yscrollcommand=self.__scrollbar.set)
        self.__canvas.bind('<configure>', lambda e: self.__canvas.configure(scrollregion=self.__canvas.bbox("all")))
        
        self.__frame = tk.Frame(self.__canvas,bg=CONSTANTS.WIDGET_BACK_COLOUR)
        
        self.__canvas.create_window((0,0), window=self.__frame, anchor="nw")

        self.__view_button = tk.Menubutton(self.__menu_frame, text="Select View", relief="flat", bg=CONSTANTS.WIDGET_BACK_COLOUR, fg=CONSTANTS.WIDGET_TEXT_COLOUR)
        self.__view_label = tk.Label(self.__menu_frame,text="dummy",bg=CONSTANTS.WIDGET_BACK_COLOUR, fg=CONSTANTS.WIDGET_TEXT_COLOUR)
        
        self.width = 0
        self.height = 0
        self.__current_view = 'none'
        self.init_window()

    def init_window(self):
        self.__note_width = int(conf.read_section('main_window', 'note_width'))
        self.__notebook_width = int(conf.read_section('main_window', 'notebook_width'))
        
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

        self.__frame.bind("<Configure>", lambda event: self.__window_resized(event))

    
    '''EVENTS'''
    
    def clear_frame(self):
        for widgets in self.__frame.winfo_children():
                widgets.destroy()

    def __clicked_note(self,event,sqlid):
        print("note id is " + str(sqlid))
        # open note for editing in new window
        note_window = NoteWindow(self.__root, self)
        note_window.open_note(sqlid, self.__db)

    def __clicked_notebook(self,event, name):
        print("notebook name is " + str(name))
        self.__get_note_pages_view(name)

    def __window_resized(self,event):
        # we will save these parameters to the config file on the window closed event
        self.width = event.width   
        self.height = event.height
        #print(f"Window resized to {self.width}x{self.height}")

        #resize the widgets in the current view
        if self.__current_view != 'none':
            #print(f"*** Updating current view: {self.__current_view} ***")
            self.get_view(self.__current_view)


    '''END OF EVENTS'''

    #Public facing function to get a main view
    def get_view(self,view):
        print("Getting view: "+view)
        self.__current_view = view
        match view:
            case 'pinned':
                # I want to set the menu button checkbox thing here!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                self.__get_pinned_notes_view()
            case 'recent':
                self.__get_recent_notes_view()
            case 'notebooks':
                self.__get_notebooks_view()

    #public facing funtion to update current view (assuming it has been set
    #This can be called by other classes if the view needs updaing i.e. a note has been deleted
    def update_currrent_view(self):        
        if self.__current_view != 'none':
            self.get_view(self.__current_view)


    def __get_note_pages_view(self, notebook):
        self.clear_frame()
        self.__view_label["text"] = "Viewing Notebook: " + notebook
        note_pages = self.__db.getNotebook(notebook)
        if note_pages is None:
            print("No pinned notes found")
            return
        
        pad_x = 3
        col = 0
        row = 0
        max_col = self.calculate_columns(self.__note_width,6)
        max_col -= 1 # -1 becuase of zero based index for grid
        num_widgets_in_row = 1
        for note_page in note_pages:
            note_id = note_page[COLUMN.ID]
            self.__text_box = tk.Text(self.__frame, height=15, width=self.__note_width, wrap=tk.WORD, bg=note_page[COLUMN.BACK_COLOUR])
            self.__text_box.insert(tk.END, note_page[COLUMN.CONTENT])
            self.__text_box.bind('<Double-1>', lambda event, sqlid=note_id: self.__clicked_note(event, sqlid))
            self.__text_box.grid(row=row, column=col, pady=3, padx=pad_x)
            if col == max_col:
                col = 0
                row += num_widgets_in_row
            else:
                col += 1

    def __get_notebooks_view(self):
        self.clear_frame()
        self.__view_label["text"] = "Viewing: Notebooks"
        col=0
        row=0
        pad_x = 3
        max_col = self.calculate_columns(self.__notebook_width,pad_x)
        max_col -= 1 # -1 becuase of zero based index for grid
        num_widgets_in_row = 1
        notebook_names = self.__db.getNotebookNames()
        if notebook_names is None:
            print("No notebooks found!")
            return
        for notebook_name in notebook_names:
            #print("Notebook name is " + str(notebook_name[0]))
            colour = self.__db.getNotebookColour(notebook_name[0])
            self.__text_box = tk.Text(self.__frame, height=5, width=self.__notebook_width, wrap=tk.WORD, bg=colour)
            self.__text_box.insert(tk.END, str(notebook_name[0]))
            self.__text_box.bind('<Double-1>', lambda event,name=str(notebook_name[0]): self.__clicked_notebook(event,name))
            self.__text_box.grid(row=row, column=col, pady=3, padx=pad_x)

            if col == max_col:
                col = 0
                row += num_widgets_in_row
            else:
                col += 1


    def __get_recent_notes_view(self):
        self.clear_frame()
        self.__view_label["text"] = "Viewing: Recent Notes"
        recent_notes = self.__db.getRecentNotes(4)
        if recent_notes is None:
            print("No recent notes found")
            return 

        pad_x = 3
        col=0
        row=0
        max_col = self.calculate_columns(self.__note_width,pad_x)
        max_col -= 1 # -1 becuase of zero based index for grid
        num_widgets_in_row = 1

        for recent_note in recent_notes:
            #print(" recent note id is " + str(recent_note[COLUMN.ID]))
            note_id = recent_note[COLUMN.ID]
            self.__text_box = tk.Text(self.__frame, height=15, width=self.__note_width, wrap=tk.WORD, bg=recent_note[COLUMN.BACK_COLOUR])
            self.__text_box.insert(tk.END, recent_note[COLUMN.CONTENT])
            self.__text_box.bind('<Double-1>', lambda event,sqlid=note_id: self.__clicked_note(event,sqlid))
            self.__text_box.grid(row=row, column=col, pady=3, padx=pad_x)

            #print("row = " + str(row)+ " column = "+ str(col))

            if col == max_col:
                col = 0
                row += num_widgets_in_row
            else:
                col += 1


    def __get_pinned_notes_view(self):
        self.clear_frame()
        self.__view_label["text"] = "Viewing: Pinned Notes"
        pinned_notes = self.__db.getPinnedNotes()
        if pinned_notes is None:
            print("No pinned notes found")
            return 

        col = 0
        row = 0
        pad_x = 3
        max_col = self.calculate_columns(self.__note_width,6)
        max_col -= 1 # -1 becuase of zero based index for grid
        #max_col = number_of_columns-1
        num_widgets_in_row = 1
        for pinned_note in pinned_notes:
            #print("pinned note id is " + str(pinned_note[COLUMN.ID]))
            note_id = pinned_note[COLUMN.ID]
            self.__text_box = tk.Text(self.__frame, height=15, width=self.__note_width, wrap=tk.WORD, bg=pinned_note[COLUMN.BACK_COLOUR])
            self.__text_box.insert(tk.END, pinned_note[COLUMN.CONTENT])
            self.__text_box.bind('<Double-1>', lambda event, sqlid=note_id: self.__clicked_note(event, sqlid))
            self.__text_box.grid(row=row, column=col, pady=3, padx=pad_x)
            #self.calculate_columns(str(self.__text_box.cget('width')),1)
            if col == max_col:
                col = 0
                row += num_widgets_in_row
            else:
                col += 1
    #Calculate the maximum number of columns of textboxes that can be displayed in a given width
    # for the current screen size
    def calculate_columns(self, widget_width, border_size):
        '''
        The text widget width will be in characters we need to convert it to pixels
        I am going to guess the pixel size for the standard font is.
        Textbox size = 50, screen size for 3 notes is 2443, so 150 chars = 2443 pixels.
        2443/150 = 16. So each character is 16 pixels wide, lets say 15 becuase of borders

        On main PC (HD screen) screen size for 3 notes is 1240, so 1240/150 = 8 pixels per character.
        This makes sens becuase my laptop is scaled to 200% - not sure how python could detect that fact!!!!!
        '''
        
        #we need this becuase initially the screen size won't be reported becuase it has not gone through mainloop yet
        self.__root.update_idletasks()
        self.__root.update()

        screen_size = self.__root.winfo_width()

        num_chars = round(screen_size / 8)

        #number of widgets that can fit horizintally on screen
        num_columns = round(num_chars  / (widget_width + border_size))

        #print(f"****** Calculated number of columns as {num_columns} *********")

        return num_columns

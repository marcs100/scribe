import tkinter as tk
from tkinter.constants import *
from database import database
from tkinter import font
import columns as COLUMN
from note_window import NoteWindow
from search_window import SearchWindow
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import colorchooser
import run_script
import os, glob, sys
import track_open_notes as tracker

class MainWindow:

    #-------------------------------------------------------
    # Initialise the class
    #-------------------------------------------------------
    def __init__(self, root, database_in, config):
        self._root = root
        self._db = database_in
        self._conf = config
       
        self.width = 0
        self.height = 0
        self._current_view = 'none'
        self._selected_notebook = 'none'
        self._page_number = 1;
        self._search_window = None
        self.init_window()


    #-------------------------------------------------------
    # Initialise the main window
    #-------------------------------------------------------
    def init_window(self):
        self._note_width = int(self._conf.read_section('main_window', 'note width'))
        self._notebook_width = int(self._conf.read_section('main_window', 'notebook width'))
        

        #Adding a scrollbar is tricky in tkinter!!!!!!
        self._main_frame = tk.Frame(self._root,bg=self._conf.read_section('colours','widget bg')) # this frame is to hold the canvass for the scrollbar
        self._canvas = tk.Canvas(self._main_frame, bg=self._conf.read_section('colours','widget bg'))
        #self._scrollbar = tk.Scrollbar(self._main_frame, orient=VERTICAL, width=15,
        #           bg=self._conf.read_section('colours','widget bg'), command=self._canvas.yview)
        self._scrollbar = ttk.Scrollbar(self._main_frame, orient=VERTICAL, command=self._canvas.yview)
        self._scrollbar.pack(side=RIGHT, fill=Y)
        self._canvas.configure(yscrollcommand=self._scrollbar.set)
        self._canvas.bind('<Configure>', lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))

        #This is the frame inside the canvas that will be scrollable (do not pack as we will create a window in it)
        self._frame = tk.Frame(self._canvas,bg=self._conf.read_section('colours','widget bg'))
        self._canvas.create_window((0,0), window=self._frame, anchor="nw")
            

        self._menu_frame = tk.Frame(self._root, bg=self._conf.read_section('colours','widget bg'))
        self._menu_frame.pack(fill=BOTH, expand=FALSE)
        self._view_button = tk.Menubutton(self._menu_frame, text="Select View", relief="flat",
                                           bg=self._conf.read_section('colours','widget bg'), fg=self._conf.read_section('colours', 'widget text'))
               
        self._view_label = tk.Label(self._menu_frame,text="dummy",bg=self._conf.read_section('colours','widget bg'),
                                     fg=self._conf.read_section('colours', 'widget text'))
        lbl_font = font.Font(weight="bold")
        self._view_label["font"] = lbl_font
        #self._frame.pack(fill=BOTH, expand=TRUE)

          #New Note button
        self._new_note_button = tk.Button(self._menu_frame, bg=self._conf.read_section('colours', 'widget bg'),
                                      fg=self._conf.read_section('colours', 'widget text'), relief="flat", text="New Note",
                                      command=self._create_new_note)
        self._new_note_button.pack(fill=Y, side='left', padx=10, pady=3)

        # This should only be enabled when in 'view notebooks' view
        self._new_notebook_button = tk.Button(self._menu_frame,  bg=self._conf.read_section('colours', 'widget bg'),
                                        fg=self._conf.read_section('colours', 'widget text'), relief="flat", text="New Notebook",
                                        state='disabled', command=self._create_new_notebook)
        self._new_notebook_button.pack(fill=Y, side='left', padx=10, pady=3)

        # right side spacer from edge of frame
        spacer_label = tk.Label(self._menu_frame, text="     ", bg=self._conf.read_section('colours', 'widget bg'),
                                fg=self._conf.read_section('colours', 'widget text'))
        spacer_label.pack(fill=Y, side='right')

        self._scripts_button = tk.Menubutton(self._menu_frame, text="Scripts", relief="flat",
                                           bg=self._conf.read_section('colours','widget bg'), fg=self._conf.read_section('colours', 'widget text'))
        self._scripts_button.menu = tk.Menu(self._scripts_button, bg=self._conf.read_section('colours','widget bg'),
                                          fg=self._conf.read_section('colours', 'widget text'), tearoff=0)
        self._scripts_button["menu"] = self._scripts_button.menu
        self._populate_scripts_menu()
        self._scripts_button.pack(fill=Y, side='right', padx=3, pady=1)

        #menu = tk.Menubutton()
        self._view_button.menu = tk.Menu(self._view_button, bg=self._conf.read_section('colours','widget bg'),
                                          fg=self._conf.read_section('colours', 'widget text'), tearoff=0)
        self._view_button["menu"] = self._view_button.menu

        self._view_button.menu.add_command(label="Pinned", command=lambda view="pinned": self.get_view(view))
        self._view_button.menu.add_command(label="Notebooks", command=lambda view="notebooks": self.get_view(view))
        self._view_button.menu.add_command(label="Recent Notes", command=lambda view="recent": self.get_view(view))

        #self._view_button.menu.bind("<FocusOut>", lambda event: self._close_view_menu(event))

        self._view_button.pack(fill=Y, side='left',padx=30,pady=3)
        self._view_label.pack(fill=Y, side='left', pady=3)

        self._canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self._main_frame.pack(fill=BOTH, expand=TRUE)

        self._main_frame.bind("<Configure>", lambda event: self._window_resized(event))

        #Setup key bindings
        self._root.bind(self._conf.read_section('main window key bindings','search'), lambda event: self._show_search_window(event))

    
    '''EVENTS'''


    #--------------------------------------------------------------------
    # Show the search window to the user
    #-------------------------------------------------------------------
    def _show_search_window(self, event):
        self._search_window = SearchWindow(self._root, self, self._db, self._conf)


    #-------------------------------------------------------
    # Event (new notebook selected)
    # Get all the notebook names from database.
    # Ask user for name of new notebook, check it doesn't
    # already exist. If all is good add the notebook to
    # the database'
    #-------------------------------------------------------
    def _create_new_notebook(self):
        #get existing notebook names as we do not want to create any duplicates
        notebook_names = self._db.getNotebookNames()

        #ask user for the new notebook name - use default colour
        new_notebook = simpledialog.askstring("Input", "Enter new notebook name...")
        if new_notebook is not None:
            self._db.addToNotebookCovers(new_notebook, self._conf.read_section('colours', 'default_notebook_bg'))
            messagebox.showinfo("Scribe","New notebook {} has been created".format(new_notebook))
            self.update_current_view()
        

    #-------------------------------------------------------
    # Event (new note selected)
    # Create a new empty note.
    # If the user in notebook view, the note will be created
    # in the current notebook else it will use the default
    # notebook.
    #-------------------------------------------------------
    def _create_new_note(self):
        note_window = NoteWindow(self._root, self, self._conf)
        if self._selected_notebook != 'none':
            note_window.set_notebook_name(self._selected_notebook)
        note_window.open_note(None, self._db)

    #-------------------------------------------------------
    # Event (view chnaged or updating)
    # Clear the contents of the main frame.
    #-------------------------------------------------------
    def clear_frame(self):
        for widgets in self._frame.winfo_children():
                widgets.destroy()


    #-------------------------------------------------------
    # Event (note clicked)
    # Open the note the user has clciked on.
    #-------------------------------------------------------
    def _clicked_note(self,event,sqlid):
        print("note id is " + str(sqlid))
        if tracker.track_note(sqlid) == True:
        # open note for editing in new window
            note_window = NoteWindow(self._root, self, self._conf)
            note_window.open_note(sqlid, self._db)


    #-------------------------------------------------------
    # Event (notebook clocked)
    # Open the notebook the user has clicked on.
    #-------------------------------------------------------
    def _clicked_notebook(self,event, name):
        print("notebook name is " + name)
        self._selected_notebook = name
        self._get_note_pages_view(name)

    #----------------------------------------------------------------
    # Event (right click on notebook)
    # Show the context menu now that user has right click the mouse
    #    Change notebook colour
    #    Delete notebook - ** to do **
    #----------------------------------------------------------------
    def _right_click_notebook(self, event, name, textbox):
        print(f"Right click event for notebook {name}")
        menu = tk.Menu(self._frame, tearoff = 0)
        menu.add_command(label ="Change colour", command=lambda name=name: self._change_notebook_colour(name))
        menu.tk_popup(event.x_root, event.y_root)

    #-------------------------------------------------------
    # Event (window has been resized)
    # Calculate a new layout for displayed notes based on the
    # current window size.
    # The new size is saved so the config can be updated when
    # the main window closes.
    #-------------------------------------------------------
    def _window_resized(self,event):
        # we will save these parameters to the config file on the window closed event
        #print("*** In Resize window eevent ***")
        #try and control the amount og times the screen will get redrawn
        prev_width = int(self.width)
        prev_height = int(self.height)
        new_width = int(event.width)
        new_height = int(event.height)

        if new_width > prev_width:
           diff1 = new_width - prev_width
        else:
            diff1 = prev_width - new_width

        if new_height > prev_height:
           diff2 = new_height - prev_height
        else:
            diff2 = prev_height - new_height

        #save the new size
        self.width = event.width
        self.height = event.height       

        if diff1 > 25 or diff2 > 25:
            #resize the widgets in the current view
            #print("*** Redrwing screen ***")
            if self._current_view != 'none':
                self.get_view(self._current_view)


    #----------------------------------------------------------------
    # SearchWindow has updated the number of search results
    # Reset page number and show first page of results
    #---------------------------------------------------------------
    def received_search_results(self, number_of_results):
        print(f"Number of search results has been updated: {str(number_of_results)}")
        self._page_number = 1;
        self.get_view('search results')
        #search_results =

    '''END OF EVENTS'''

    #------------------------------------------------
    #Public facing function to get a main view
    #------------------------------------------------
    def get_view(self,view):
        #print("Getting view: "+view)
        self._current_view = view
        match view:
            case 'pinned':
                self._new_notebook_button["state"]='disabled'
                self._selected_notebook = 'none'
                self._get_pinned_notes_view()
            case 'recent':
                self._new_notebook_button["state"]='disabled'
                self._selected_notebook = 'none'
                self._get_recent_notes_view()
            case 'notebooks':
                self._new_notebook_button["state"]='normal'
                self._selected_notebook = 'none'
                self._get_notebooks_view()
            case 'notebook_pages':
                self._new_notebook_button["state"]='disabled'
                if self._selected_notebook != 'none':
                    self._get_note_pages_view(self._selected_notebook)
            case 'search results':
                self._new_notebook_button['state'] = 'disabled'
                self._selected_notebook = 'none'
                if(self._search_window is not None):
                    search_results = self._search_window.get_search_results(self._page_number) #will return the results from the saved current_search term
                    if search_results is not None:
                        self.get_search_results_view(search_results)
                    else:
                        print("In get_view -(None) search results returned")
                else:
                    print("in get_view() no reference to SearchWindow class")
    

    #-----------------------------------------------------------------------
    # public facing funtion to update current view (assuming it has been set
    # This can be called by other classes if the view needs updaing i.e. a
    # note has been deleted
    #-----------------------------------------------------------------------
    def update_current_view(self):
        if self._current_view != 'none':
            self.get_view(self._current_view)

    #----------------------------------------------------------------------
    # Get all the note pages from the currently selected notebook. 
    #----------------------------------------------------------------------
    def _get_note_pages_view(self, notebook):
        self.clear_frame()
        self._current_view = 'notebook_pages'
        self._view_label["text"] = "Viewing Notebook: " + notebook
        note_pages = self._db.getNotebook(notebook)
        if note_pages is None:
            print("No pinned notes found")
            return
        
        pad_x = 3
        col = 0
        row = 0
        max_col = self.calculate_columns(self._note_width,6)
        max_col -= 1 # -1 becuase of zero based index for grid
        num_widgets_in_row = 1
        for note_page in note_pages:
            note_id = note_page[COLUMN.ID]
            self._text_box = tk.Text(self._frame, height=15, width=self._note_width, wrap=tk.WORD, bg=note_page[COLUMN.BACK_COLOUR])
            self._text_box.insert(tk.END, note_page[COLUMN.CONTENT])
            self._text_box.bind('<Double-1>', lambda event, sqlid=note_id: self._clicked_note(event, sqlid))
            self._text_box.grid(row=row, column=col, pady=3, padx=pad_x)
            self._text_box['state'] = 'disabled'
            if col == max_col:
                col = 0
                row += num_widgets_in_row
            else:
                col += 1

    #-------------------------------------------------------
    # Display all the notebooks from the database
    #-------------------------------------------------------
    def _get_notebooks_view(self):
        self.clear_frame()
        self._view_label["text"] = "Viewing: Notebooks"
        col=0
        row=0
        pad_x = 3
        max_col = self.calculate_columns(self._notebook_width,pad_x)
        max_col -= 1 # -1 becuase of zero based index for grid
        num_widgets_in_row = 1
        notebook_names = self._db.getNotebookNames()
        if notebook_names is None:
            print("No notebooks found!")
            return
        for notebook_name in notebook_names:
            colour = self._db.getNotebookColour(notebook_name[0])
            self._text_box = tk.Text(self._frame, height=5, width=self._notebook_width, wrap=tk.WORD, bg=colour)
            self._text_box.insert(tk.END, str(notebook_name[0]))
            num_notes = self._db.getNumberOfNotesInNotebook(notebook_name[0])
            self._text_box.insert(tk.END, f"\n\n({str(num_notes)} notes)")
            #print (f"Number of notes in {notebook_name[0]} is {str(num_notes)}")
            self._text_box.bind('<Double-1>',
                                 lambda event,name=str(notebook_name[0]):self._clicked_notebook(event,name))

            #Trying to implement rigth click event here!!!!!!!!!!
            self._text_box.bind('<Button-3>',
                                 lambda event, name=str(notebook_name[0]),
                                 textbox=self._text_box:self._right_click_notebook(event,name, textbox))

            self._text_box.grid(row=row, column=col, pady=3, padx=pad_x)
            self._text_box['state'] = 'disabled'

            if col == max_col:
                col = 0
                row += num_widgets_in_row
            else:
                col += 1

    #-------------------------------------------------------
    # Display recent notes from the database
    # Number of notes to display is in the config file.
    #-------------------------------------------------------
    def _get_recent_notes_view(self):
        self.clear_frame()
        self._view_label["text"] = "Viewing: Recent Notes"
        recent_notes = self._db.getRecentNotes(int(self._conf.read_section('main', 'recent notes count')))
        if recent_notes is None:
            print("No recent notes found")
            return 

        pad_x = 3
        col=0
        row=0
        max_col = self.calculate_columns(self._note_width,pad_x)
        max_col -= 1 # -1 becuase of zero based index for grid
        num_widgets_in_row = 1

        for recent_note in recent_notes:
            note_id = recent_note[COLUMN.ID]
            self._text_box = tk.Text(self._frame, height=15, width=self._note_width, wrap=tk.WORD, bg=recent_note[COLUMN.BACK_COLOUR])
            self._text_box.insert(tk.END, recent_note[COLUMN.CONTENT])
            self._text_box.bind('<Double-1>', lambda event,sqlid=note_id: self._clicked_note(event,sqlid))
            self._text_box.grid(row=row, column=col, pady=3, padx=pad_x)
            self._text_box['state'] = 'disabled'
            if col == max_col:
                col = 0
                row += num_widgets_in_row
            else:
                col += 1

    #-------------------------------------------------------
    # Dsiplay all the pinned notes from the database.
    #-------------------------------------------------------
    def _get_pinned_notes_view(self):
        self.clear_frame()
        self._view_label["text"] = "Viewing: Pinned Notes"
        pinned_notes = self._db.getPinnedNotes()
        if pinned_notes is None:
            print("No pinned notes found")
            return 

        col = 0
        row = 0
        pad_x = 3
        max_col = self.calculate_columns(self._note_width,6)
        max_col -= 1 # -1 becuase of zero based index for grid
        num_widgets_in_row = 1
        for pinned_note in pinned_notes:
            note_id = pinned_note[COLUMN.ID]
            self._text_box = tk.Text(self._frame, height=15, width=self._note_width, wrap=tk.WORD, bg=pinned_note[COLUMN.BACK_COLOUR])
            self._text_box.insert(tk.END, pinned_note[COLUMN.CONTENT])
            self._text_box.bind('<Double-1>', lambda event, sqlid=note_id: self._clicked_note(event, sqlid))
            self._text_box.grid(row=row, column=col, pady=3, padx=pad_x)
            self._text_box['state'] = 'disabled'
            if col == max_col:
                col = 0
                row += num_widgets_in_row
            else:
                col += 1


    #-------------------------------------------------------
    # Display the search result (notes)
    #
    #-------------------------------------------------------
    def get_search_results_view(self, search_results):
        self._current_view = 'search results'
        self._selected_notebook = 'none'
        self.clear_frame()
        self._current_view = 'search results'
        self._view_label["text"] = "Viewing Search Results"

        if search_results is None:
            print("No search results notes found")
            return

        self._view_label["text"] = f"Viewing Search Results ({str(len(search_results))})"

        pad_x = 3
        col = 0
        row = 0
        max_col = self.calculate_columns(self._note_width,6)
        max_col -= 1 # -1 becuase of zero based index for grid
        num_widgets_in_row = 1
        for search_page in search_results:
            #print(f"Search page: {str(search_page)}")
            note_id = search_page[COLUMN.ID]

            self._text_box = tk.Text(self._frame,height=15,width=self._note_width, wrap=tk.WORD,
                        bg=search_page[COLUMN.BACK_COLOUR])
            self._text_box.insert(tk.END, search_page[COLUMN.CONTENT])
            self._text_box.bind('<Double-1>', lambda event, sqlid=note_id:self._clicked_note(event, sqlid))
            self._text_box.grid(row=row, column=col, pady=3, padx=pad_x)
            self._text_box['state'] = 'disabled'
            if col == max_col:
                col = 0
                row += num_widgets_in_row
            else:
                col += 1

    #-------------------------------------------------------
    # Allow the user to slect a new notebook colour
    #-------------------------------------------------------
    def _change_notebook_colour(self, name):
        print (f"Will chnage notebook colour for {name}")
        colour = colorchooser.askcolor(title="Choose notebook colour", parent=self._frame)
        if colour != (None,None):
            colour = str(colour[1])
            self._db.setNotebookColour(name,colour)
            self.update_current_view()

    #-------------------------------------------------------
    # Helper function to automatically read al the script
    # files and populate a menu with the values.
    #-------------------------------------------------------
    def _populate_scripts_menu(self):
        #self._scripts_button.menu.add_command(label="Pinned", command=lambda view="pinned": self.get_view(view))
        script_dir = self._module_path() + "/scripts/"

        script_files = glob.glob(script_dir+"*.py")

        for script_file in script_files:
            print(f"found script {script_file}")
            head, script_file_name = os.path.split(script_file)
            self._scripts_button.menu.add_command(label=script_file_name,
                command=lambda script=script_file: run_script.run_script(script, self._conf))


    #-------------------------------------------------------
    # Helper function
    # Thank you internet! - not sure if this is needed!!!!!!
    #-------------------------------------------------------
    def _we_are_frozen(self):
        # All of the modules are built-in to the interpreter, e.g., by py2exe
        return hasattr(sys, "frozen")

    #-------------------------------------------------------
    # Get the path for the current source code.
    #-------------------------------------------------------
    def _module_path(self):
        encoding = sys.getfilesystemencoding()
        if self._we_are_frozen():
            return os.path.dirname(str(sys.executable))
        return os.path.dirname(str(__file__))


    #----------------------------------------------------------------------
    # Calculate the maximum number of columns of textboxes that can be
    # displayed in a given width for the current screen size.
    #----------------------------------------------------------------------
    def calculate_columns(self, widget_width, border_size):
        '''
        The text widget width will be in characters we need to convert it to pixels
        I am going to guess the pixel size for the standard font is.
        Textbox size = 50, screen size for 3 notes is 2443, so 150 chars = 2443 pixels.
        2443/150 = 16. So each character is 16 pixels wide, lets say 15 becuase of borders

        On main PC (HD screen) screen size for 3 notes is 1240, so 1240/150 = 8 pixels per character.
        This makes sens becuase my laptop is scaled to 200% - not sure how python could detect that fact!!!!!
        '''

        #get screen scale value (multiplier)
        scr_scale = int(self._conf.read_section('main', 'screen scale'))

        
        #we need this becuase initially the screen size won't be reported becuase it has not gone through mainloop yet
        self._root.update_idletasks()
        self._root.update()

        screen_size = self._root.winfo_width()

        num_chars = round(screen_size / (8 * scr_scale))

        #number of widgets that can fit horizintally on screen
        num_columns = round(num_chars  / (widget_width + border_size))

        #print(f"****** Calculated number of columns as {num_columns} *********")

        return num_columns

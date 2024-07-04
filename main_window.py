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
from text_formatting import TextFormatter

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
        self._page_number = 1
        self._max_page = 1
        self._search_window = None
        self.init_window()
        self.width = self._root.winfo_width()
        self.height = self._root.winfo_height()
        self._notes_per_page = int(self._conf.read_section('main','notes per page'))
        self._number_of_notes = 0 # the number of notes in the currently selected notebook
        self._text_formatter = TextFormatter(self._conf)



    #-----------------------------------------------------------------------
    # Resize the window width +1 then back to original size!
    # This is only needed because the scrollbar does not seem to indicate
    # a scrollable region unless the winow is resized with the mouse.
    #------------------------------------------------------------------------
    def _force_resize(self):
        #print("in _force_resize()")
        self._root.geometry(f"{str(self._root.winfo_width()+1)}x{str(self._root.winfo_height())}")
        self._root.geometry(f"{str(self._root.winfo_width()-1)}x{str(self._root.winfo_height())}")


    #-------------------------------------------------------
    # Initialise the main window
    #-------------------------------------------------------
    def init_window(self):
        self._note_width = int(self._conf.read_section('main window', 'note width'))
        self._notebook_width = int(self._conf.read_section('main window', 'notebook width'))

        # This is a hack!!
        # if we add an image to a button we can set button size in pixelsrather than text.
        self._button_image = tk.PhotoImage(width=1, height=1)
        

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
        self._menu_frame.pack(fill='both', expand=FALSE)
        self._view_button = tk.Menubutton(self._menu_frame, text="Select View", relief="flat",
                                    bg=self._conf.read_section('colours','widget bg'),
                                    fg=self._conf.read_section('colours', 'widget text'),
                                    image = self._button_image,
                                    compound = 'c',
                                    height=8,
                                    width=65)
               
        self._view_label = tk.Label(self._menu_frame,text="dummy",bg=self._conf.read_section('colours','widget bg'),
                                     height=1, fg=self._conf.read_section('colours', 'widget text'))
        lbl_font = font.Font(weight="bold")
        self._view_label["font"] = lbl_font
        #self._frame.pack(fill=BOTH, expand=TRUE)

        #New Note button
        self._new_note_button = tk.Button(self._menu_frame, bg=self._conf.read_section('colours', 'widget bg'),
                                    fg=self._conf.read_section('colours', 'widget text'), relief=FLAT, text="New Note",
                                    command=self._create_new_note,
                                    borderwidth=0,
                                    anchor=tk.CENTER,
                                    image = self._button_image,
                                    compound = 'c',
                                    height=15,
                                    width=55)
        self._new_note_button.pack(side='left', padx=10, pady=3)

        # This should only be enabled when in 'view notebooks' view
        self._new_notebook_button = tk.Button(self._menu_frame,  bg=self._conf.read_section('colours', 'widget bg'),
                                    fg=self._conf.read_section('colours', 'widget text'), relief=FLAT, text="New Notebook",
                                    state='disabled', command=self._create_new_notebook,
                                    anchor=tk.CENTER,
                                    image = self._button_image,
                                    compound = 'c',
                                    height=15,
                                    width=75)
        self._new_notebook_button.pack(side='left', padx=10)

        # right side spacer from edge of frame
        spacer_label = tk.Label(self._menu_frame, text="     ",
                                bg=self._conf.read_section('colours', 'widget bg'),
                                fg=self._conf.read_section('colours', 'widget text'),
                                height=1)
        spacer_label.pack(fill=Y, side='right')

        self._scripts_button = tk.Menubutton(self._menu_frame, text="Scripts", relief="flat",
                                    bg=self._conf.read_section('colours','widget bg'),
                                    fg=self._conf.read_section('colours', 'widget text'),
                                    image = self._button_image,
                                    compound = 'c',
                                    height=5,
                                    width=30)

        self._scripts_button.menu = tk.Menu(self._scripts_button, bg=self._conf.read_section('colours','widget bg'),
                                          fg=self._conf.read_section('colours', 'widget text'), tearoff=0)
        self._scripts_button["menu"] = self._scripts_button.menu
        self._populate_scripts_menu()
        self._scripts_button.pack(side='right', padx=3, pady=1)

        #Page forward button
        self._page_forward_button = tk.Button(self._menu_frame, bg=self._conf.read_section('colours', 'widget bg'),
                                      fg=self._conf.read_section('colours', 'widget text'), relief="raised", text=">>",
                                      command=self._page_forward,
                                      image = self._button_image,
                                      compound = 'c',
                                      height=5,
                                      width=12)

        #Page back button
        self._page_back_button = tk.Button(self._menu_frame, bg=self._conf.read_section('colours', 'widget bg'),
                                      fg=self._conf.read_section('colours', 'widget text'), relief="raised", text="<<",
                                      command=self._page_back,
                                      image = self._button_image,
                                      compound = 'c',
                                      height=5,
                                      width=12)

        spacer_label2 = tk.Label(self._menu_frame, text="     ",
                                bg=self._conf.read_section('colours', 'widget bg'),
                                fg=self._conf.read_section('colours', 'widget text'),
                                height=1)
        spacer_label.pack(fill=Y, side='right')

        spacer_label2.pack(side='right')
        self._page_forward_button.pack(side='right',padx=3, pady=10)
        self._page_back_button.pack(side='right', padx=3, pady=10)

        #menu = tk.Menubutton()
        self._view_button.menu = tk.Menu(self._view_button, bg=self._conf.read_section('colours','widget bg'),
                                          fg=self._conf.read_section('colours', 'widget text'), tearoff=0)
        self._view_button["menu"] = self._view_button.menu

        self._view_button.menu.add_command(label="Pinned", command=lambda view="pinned": self.get_view(view))
        self._view_button.menu.add_command(label="Notebooks", command=lambda view="notebooks": self.get_view(view))
        self._view_button.menu.add_command(label="Recent Notes", command=lambda view="recent": self.get_view(view))

        #self._view_button.menu.bind("<FocusOut>", lambda event: self._close_view_menu(event))

        self._status_frame = tk.Frame(self._root, bg=self._conf.read_section('colours','widget bg'))
        self._status_label = tk.Label(self._status_frame,
                            bg=self._conf.read_section('colours','widget bg'),
                            fg=self._conf.read_section('colours','widget text'),
                            text='staus: blah blah',
                            height=1,
                            anchor="se")
        self._status_label.pack(fill='both', expand='true', padx=25)
        #self._status_label.grid(row=0, column=0, padx=25)

        self._view_button.pack(side='left',padx=30,pady=3)
        self._view_label.pack(fill=Y, side='left', pady=3)

        self._canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self._main_frame.pack(fill=BOTH, expand='true')
        self._status_frame.pack(fill='x', expand='false', side='bottom')

        self._main_frame.bind("<Configure>", lambda event: self._window_resized(event))

        #Setup key bindings
        self._root.bind(self._conf.read_section('main window key bindings','search'),
                        lambda event: self._show_search_window(event))
        self._root.bind(self._conf.read_section('main window key bindings','new note'),
                        lambda event: self._create_new_note())
        self._root.bind(self._conf.read_section('main window key bindings','show notebook view'),
                        lambda event, view="notebooks": self._get_view_event(event, view))
        self._root.bind(self._conf.read_section('main window key bindings','show pinned notes view'),
                        lambda event, view="pinned": self._get_view_event(event, view))
        self._root.bind(self._conf.read_section('main window key bindings','show recent notes view'),
                        lambda event, view="recent": self._get_view_event(event, view))

        self._root.bind(self._conf.read_section('main window key bindings','page forward'),
                        lambda event: self._page_forward())
        self._root.bind(self._conf.read_section('main window key bindings','page back'),
                        lambda event: self._page_back())

    
    '''EVENTS'''
    #--------------------------------------------------------------------
    # Move page forward
    #-------------------------------------------------------------------
    def _page_forward(self):
        #print("page forward function")
        #print(f"max page: {self._max_page}")
        #print(f"page num: {self._page_number}")

        if self._page_forward_button['state'] == 'disabled':
            return

        if self._page_number >= self._max_page:
            #print("page is greater then max page")
            return
        self._page_number += 1 # move page forward

        if self._current_view == 'search results':
            if self._search_window == None:
                #print("search_window is None")
                return
            if self._search_window.has_search_results() == False:
                #print("No results waiting")
                return
            search_results = self._search_window.get_search_results(self._page_number)
            #print("page forward got search results")
            self.get_view('search results')
        elif self._current_view == 'notebook pages':
            if self._number_of_notes == 0:
                return
            self.get_view('notebook pages')


    #--------------------------------------------------------------------
    # Move page back
    #-------------------------------------------------------------------
    def _page_back(self):
        #print("page back function")

        if self._page_back_button['state'] == 'disabled':
            return


        if self._page_number == 1:
            #print("page number is 1 can't go back")
            return
        self._page_number -= 1 # move page back

        if self._current_view == 'search results':
            if self._search_window == None:
                #print("not in search view")
                return
            if self._search_window.has_search_results() == False:
                return
            search_results = self._search_window.get_search_results(self._page_number)
            self.get_view('search results')

        elif self._current_view == 'notebook pages':
            if self._number_of_notes == 0:
                return
            self.get_view('notebook pages')


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
            self._db.addToNotebookCovers(new_notebook, self._conf.read_section('colours', 'default notebook bg'))
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
    # Event (notebook clicked)
    # Open the notebook the user has clicked on.
    #-------------------------------------------------------
    def _clicked_notebook(self,event, name):
        print("notebook name is " + name)
        self._selected_notebook = name
        self._page_number = 1 #reset page page back to e.g could be coming from page 3 of a search view
        #self._get_note_pages_view(name)
        self.get_view('notebook pages')

    #----------------------------------------------------------------
    # Event (right click on notebook)
    # Show the context menu now that user has right click the mouse
    #    Change notebook colour
    #    Delete notebook - ** to do **
    #----------------------------------------------------------------
    def _right_click_notebook(self, event, name, textbox):
        print(f"Right click event for notebook {name}")
        menu = tk.Menu(self._frame,
                       tearoff = 0,
                        bg=self._conf.read_section('colours','widget bg'),
                       fg=self._conf.read_section('colours','widget text'))
        menu.add_command(label ="Change colour", command=lambda name=name: self._change_notebook_colour(name))
        menu.add_command(label ="Delete notebook!", command=lambda name=name: self._delete_notebook(name))
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
        #print(f"Number of search results has been updated: {str(number_of_results)}")
        self._page_number = 1
        self._max_page = self._search_window.get_number_of_pages()
        self.get_view('search results')
        #search_results =

    #----------------------------------------------------------------
    # Get view as event, although we ignore the event parameter.
    #
    #---------------------------------------------------------------
    def _get_view_event(self, event, view):
        self.get_view(view)

    '''END OF EVENTS'''

    #------------------------------------------------
    #Public facing function to get a main view
    #------------------------------------------------
    def get_view(self,view):
        #print("Getting view: "+view)
        self._current_view = view
        self._page_forward_button['state']='disabled'
        self._page_back_button['state']='disabled'
        self._status_label['text'] = ''
        self._number_of_notes = 0 #reset number of notes in currrent notebook count
        match view:
            case 'pinned':
                self._page_number = 1
                self._new_notebook_button["state"]='disabled'
                self._selected_notebook = 'none'
                self._get_pinned_notes_view()
            case 'recent':
                self._page_number = 1
                self._new_notebook_button["state"]='disabled'
                self._selected_notebook = 'none'
                self._get_recent_notes_view()
            case 'notebooks':
                self._page_number = 1
                self._new_notebook_button["state"]='normal'
                self._selected_notebook = 'none'
                self._get_notebooks_view()
            case 'notebook pages':
                self._page_forward_button['state']='active'
                self._page_back_button['state']='active'
                self._new_notebook_button["state"]='disabled'
                if self._selected_notebook != 'none':
                    self._number_of_notes = self._db.getNumberOfNotesInNotebook(self._selected_notebook)

                    #calculate how many pages there are
                    self._max_page = self._number_of_notes // self._notes_per_page
                    if self._number_of_notes % self._notes_per_page > 0:
                        self._max_page +=1

                    #get the notes for the current page
                    offset = (self._page_number-1) * self._notes_per_page

                    #calculate the offset
                    if offset > self._number_of_notes:
                        print ("Error - note pages view: offset > number of results")
                        return
                    notebook_pages = self._db.getNotebookPage(self._selected_notebook, self._notes_per_page, offset)
                    self._get_notebook_pages_view(self._selected_notebook, notebook_pages)
            case 'search results':
                self._page_forward_button['state']='active'
                self._page_back_button['state']='active'
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

        self._force_resize() # force a resize window - to get scrollbar to behave!

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
    def _get_notebook_pages_view(self, notebook, notebook_pages):
        self.clear_frame()
        self._current_view = 'notebook pages'
        self._view_label["text"] = "Viewing Notebook: " + notebook
        if notebook_pages is None:
            print("No pages notes found")
            return

        #Update statues bar----------------------------------------------------------------------------
        #calculate upper range
        pages_upper_range = self._page_number * self._notes_per_page
        if self._number_of_notes < pages_upper_range:
            pages_upper_range = self._number_of_notes
        #calculate lower range
        pages_lower_range = 1 + (self._notes_per_page * self._page_number) - self._notes_per_page
        self._status_label['text'] =  f"Page {str(self._page_number)}   Showing notes: {str(pages_lower_range)} to {str(pages_upper_range)} of  {str(self._number_of_notes)}"
        #---------------------------------------------------------------------------------------------

        
        pad_x = 3
        col = 0
        row = 0
        max_col = self.calculate_columns(self._note_width,6)
        max_col -= 1 # -1 becuase of zero based index for grid
        num_widgets_in_row = 1
        for note_page in notebook_pages:
            note_id = note_page[COLUMN.ID]
            self._text_box = tk.Text(self._frame, height=15, width=self._note_width, wrap=tk.WORD, bg=note_page[COLUMN.BACK_COLOUR])
            self._text_box.insert(tk.END, note_page[COLUMN.CONTENT])
            self._text_box.bind('<Double-1>', lambda event, sqlid=note_id: self._clicked_note(event, sqlid))
            self._text_box.grid(row=row, column=col, pady=3, padx=pad_x)
            self._text_formatter.set_bold_text(self._text_box)
            self._text_formatter.set_title_text(self._text_box)
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
        max_col -= 1 # -1 because of zero based index for grid
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
        max_col -= 1 # -1 because of zero based index for grid
        num_widgets_in_row = 1

        for recent_note in recent_notes:
            note_id = recent_note[COLUMN.ID]
            self._text_box = tk.Text(self._frame, height=15, width=self._note_width, wrap=tk.WORD, bg=recent_note[COLUMN.BACK_COLOUR])
            self._text_box.insert(tk.END, recent_note[COLUMN.CONTENT])
            self._text_box.bind('<Double-1>', lambda event,sqlid=note_id: self._clicked_note(event,sqlid))
            self._text_box.grid(row=row, column=col, pady=3, padx=pad_x)
            self._text_formatter.set_bold_text(self._text_box)
            self._text_formatter.set_title_text(self._text_box)
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
        print("In get pinned notes view!!!!!!!!!")
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
        max_col -= 1 # -1 because of zero based index for grid
        num_widgets_in_row = 1
        for pinned_note in pinned_notes:
            note_id = pinned_note[COLUMN.ID]
            self._text_box = tk.Text(self._frame, height=15, width=self._note_width, wrap=tk.WORD, bg=pinned_note[COLUMN.BACK_COLOUR])
            self._text_box.insert(tk.END, pinned_note[COLUMN.CONTENT])
            self._text_box.bind('<Double-1>', lambda event, sqlid=note_id: self._clicked_note(event, sqlid))
            self._text_box.grid(row=row, column=col, pady=3, padx=pad_x)
            self._text_formatter.set_bold_text(self._text_box)
            self._text_formatter.set_title_text(self._text_box)
            self._text_box['state'] = 'disabled'
            if col == max_col:
                col = 0
                row += num_widgets_in_row
            else:
                col += 1

        #self._force_resize() #experiemnt only!!!!!!!!

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

        #Update statues bar----------------------------------------------------------------------------
        if self._search_window is not None:
            #update the status label
            num_results = self._search_window.get_number_search_of_results()

            #calculate upper range
            pages_upper_range = self._page_number * self._notes_per_page
            if num_results < pages_upper_range:
                pages_upper_range = num_results

            #calculate lower range
            pages_lower_range = 1 + (self._notes_per_page * self._page_number) - self._notes_per_page

            self._status_label['text'] =  f"Page {str(self._page_number)}   Search Results: {str(pages_lower_range)} to {str(pages_upper_range)} of  {str(num_results)}"
        #---------------------------------------------------------------------------------------------

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
    # Delete an enitre notebook!!!
    #-------------------------------------------------------
    def _delete_notebook(self, name):
        num_notes = self._db.getNumberOfNotesInNotebook(name)
        result = messagebox.askyesno("Delete Notebook {name}", f"Are you sure you want to delete this notebook containing {num_notes} notes?")
        if result == True:
            self._db.deleteNotebook(name)
            self._db.deleteNotebookCover(name)
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

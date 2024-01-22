import tkinter
from tkinter.constants import *
from database import database
import tkinter as tk
from tkinter import font
import columns as COLUMN
from note_window import NoteWindow
import config_file as conf
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import colorchooser

class MainWindow:
    def __init__(self, root, database_in):
        self.__root = root
        self.__db = database_in
       
        self.width = 0
        self.height = 0
        self.__current_view = 'none'
        self.__selected_notebook = 'none'
        self.init_window()

    def init_window(self):
        self.__note_width = int(conf.read_section('main_window', 'note_width'))
        self.__notebook_width = int(conf.read_section('main_window', 'notebook_width'))
        

        #Adding a scrollbar is tricky in tkinter!!!!!!
        self.__main_frame = tk.Frame(self.__root,bg=conf.read_section('colours','widget_bg')) # this frame is to hold the canvass for the scrollbar 
        self.__canvas = tk.Canvas(self.__main_frame, bg=conf.read_section('colours','widget_bg'))
        #self.__scrollbar = tk.Scrollbar(self.__main_frame, orient=VERTICAL, width=15, 
        #           bg=conf.read_section('colours','widget_bg'), command=self.__canvas.yview)
        self.__scrollbar = ttk.Scrollbar(self.__main_frame, orient=VERTICAL, command=self.__canvas.yview)
        self.__scrollbar.pack(side=RIGHT, fill=Y)
        self.__canvas.configure(yscrollcommand=self.__scrollbar.set)
        self.__canvas.bind('<Configure>', lambda e: self.__canvas.configure(scrollregion=self.__canvas.bbox("all")))

        #This is the frame inside the canvas that will be scrollable (do not pack as we will create a window in it)
        self.__frame = tk.Frame(self.__canvas,bg=conf.read_section('colours','widget_bg'))
        self.__canvas.create_window((0,0), window=self.__frame, anchor="nw")
            

        self.__menu_frame = tk.Frame(self.__root, bg=conf.read_section('colours','widget_bg'))
        self.__menu_frame.pack(fill=BOTH, expand=FALSE) 
        self.__view_button = tk.Menubutton(self.__menu_frame, text="Select View", relief="flat", 
                                           bg=conf.read_section('colours','widget_bg'), fg=conf.read_section('colours', 'widget_text'))
               
        self.__view_label = tk.Label(self.__menu_frame,text="dummy",bg=conf.read_section('colours','widget_bg'), 
                                     fg=conf.read_section('colours', 'widget_text'))
        lbl_font = font.Font(weight="bold")
        self.__view_label["font"] = lbl_font
        #self.__frame.pack(fill=BOTH, expand=TRUE) 

          #New Note button
        self.__new_note_button = tk.Button(self.__menu_frame, bg=conf.read_section('colours', 'widget_bg'),
                                      fg=conf.read_section('colours', 'widget_text'), relief="flat", text="New Note",
                                      command=self.__create_new_note)
        self.__new_note_button.pack(fill=Y, side='left', padx=10, pady=3)

        # This should only be enabled when in 'view notebooks' view
        self.__new_notebook_button = tk.Button(self.__menu_frame,  bg=conf.read_section('colours', 'widget_bg'),
                                        fg=conf.read_section('colours', 'widget_text'), relief="flat", text="New Notebook",
                                        state='disabled', command=self.__create_new_notebook)
        self.__new_notebook_button.pack(fill=Y, side='left', padx=10, pady=3)

        self.__search_input = tk.StringVar()
        self.__search_entry = tk.Entry(self.__menu_frame,textvariable=self.__search_input, bg=conf.read_section('colours','widget_bg'), fg=conf.read_section('colours','widget_text'))

        # right side spacer from edge of frame
        spacer_label = tk.Label(self.__menu_frame, text="     ", bg=conf.read_section('colours', 'widget_bg'),
                                fg=conf.read_section('colours', 'widget_text'))
        spacer_label.pack(fill=Y, side='right')

        self.__search_entry.pack(fill=Y, side='right',padx=3, pady=1)
        self.__search_button = tk.Button(self.__menu_frame,bg=conf.read_section('colours', 'widget_bg'),
                                           fg=conf.read_section('colours', 'widget_text'), relief="flat", text="search",
                                           command=self.__get_search_inpt)
        self.__search_button.pack(fill=Y, side='right', padx=5, pady=1)

         # Select view menu button
        #menu = tk.Menubutton()
        self.__view_button.menu = tk.Menu(self.__view_button, bg=conf.read_section('colours','widget_bg'), 
                                          fg=conf.read_section('colours', 'widget_text'))
        self.__view_button["menu"] = self.__view_button.menu

        self.__view_button.menu.add_command(label="Pinned", command=lambda view="pinned": self.get_view(view))
        self.__view_button.menu.add_command(label="Notebooks", command=lambda view="notebooks": self.get_view(view))
        self.__view_button.menu.add_command(label="Recent Notes", command=lambda view="recent": self.get_view(view))

        self.__view_button.pack(fill=Y, side='left',padx=30,pady=3)
        self.__view_label.pack(fill=Y, anchor='center', pady=3)

        self.__canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.__main_frame.pack(fill=BOTH, expand=TRUE)

        self.__main_frame.bind("<Configure>", lambda event: self.__window_resized(event))

    
    '''EVENTS'''

    def __get_search_inpt(self):
        print(f"Search input is {self.__search_input.get()}")
        self.get_view('search results')

    def __create_new_notebook(self):
        #get existing notebook names as we do not want to create any duplicates
        notebook_names = self.__db.getNotebookNames()

        #ask user for the new notebook name - use default colour
        new_notebook = simpledialog.askstring("Input", "Enter new notebook name...")
        if new_notebook is not None:
            self.__db.addToNotebookCovers(new_notebook, conf.read_section('colours', 'default_notebook_bg'))
            messagebox.showinfo("Scribe","New notebook {} has been created".format(new_notebook))
            self.update_currrent_view()
        

    def __create_new_note(self):
        note_window = NoteWindow(self.__root, self)
        if self.__selected_notebook != 'none':
            note_window.set_notebook_name(self.__selected_notebook)
        note_window.open_note(None, self.__db)

    
    def clear_frame(self):
        for widgets in self.__frame.winfo_children():
                widgets.destroy()

    def __clicked_note(self,event,sqlid):
        print("note id is " + str(sqlid))
        # open note for editing in new window
        note_window = NoteWindow(self.__root, self)
        note_window.open_note(sqlid, self.__db)


    def __clicked_notebook(self,event, name):
        print("notebook name is " + name)
        self.__selected_notebook = name
        self.__get_note_pages_view(name)

    def __right_click_notebook(self, event, name, textbox):
        print(f"Right click event for notebook {name}")
        menu = tk.Menu(self.__frame, tearoff = 0)
        menu.add_command(label ="Change colour", command=lambda name=name: self.__change_notebook_colour(name))
        menu.tk_popup(event.x_root, event.y_root)

    def __window_resized(self,event):
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
            if self.__current_view != 'none':
                self.get_view(self.__current_view)



    '''END OF EVENTS'''
    ##############################################################
    #Public facing function to get a main view
    ##############################################################
    def get_view(self,view):
        #print("Getting view: "+view)
        self.__current_view = view
        match view:
            case 'pinned':
                self.__new_notebook_button["state"]='disabled'
                self.__selected_notebook = 'none'
                self.__get_pinned_notes_view()
            case 'recent':
                self.__new_notebook_button["state"]='disabled'
                self.__selected_notebook = 'none'
                self.__get_recent_notes_view()
            case 'notebooks':
                self.__new_notebook_button["state"]='normal'
                self.__selected_notebook = 'none'
                self.__get_notebooks_view()
            case 'notebook_pages':
                self.__new_notebook_button["state"]='disabled'
                if self.__selected_notebook != 'none':
                    self.__get_note_pages_view(self.__selected_notebook)
            case 'search results':
                    self.__new_notebook_button["state"]='disabled'
                    self.__selected_notebook = 'none'
                    self.__get_search_results_view()
    

    #################################################################################
    #public facing funtion to update current view (assuming it has been set
    #This can be called by other classes if the view needs updaing i.e. a note has been deleted
    #################################################################################
    def update_currrent_view(self):        
        if self.__current_view != 'none':
            self.get_view(self.__current_view)


    def __get_note_pages_view(self, notebook):
        self.clear_frame()
        self.__current_view = 'notebook_pages'
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
            self.__text_box['state'] = 'disabled'
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
            colour = self.__db.getNotebookColour(notebook_name[0])
            self.__text_box = tk.Text(self.__frame, height=5, width=self.__notebook_width, wrap=tk.WORD, bg=colour)
            self.__text_box.insert(tk.END, str(notebook_name[0]))
            self.__text_box.bind('<Double-1>',
                                 lambda event,name=str(notebook_name[0]):self.__clicked_notebook(event,name))

            #Trying to implement rigth click event here!!!!!!!!!!
            self.__text_box.bind('<Button-3>',
                                 lambda event, name=str(notebook_name[0]),
                                 textbox=self.__text_box:self.__right_click_notebook(event,name, textbox))

            self.__text_box.grid(row=row, column=col, pady=3, padx=pad_x)
            self.__text_box['state'] = 'disabled'

            if col == max_col:
                col = 0
                row += num_widgets_in_row
            else:
                col += 1


    def __get_recent_notes_view(self):
        self.clear_frame()
        self.__view_label["text"] = "Viewing: Recent Notes"
        recent_notes = self.__db.getRecentNotes(int(conf.read_section('main', 'recent_notes_count')))
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
            note_id = recent_note[COLUMN.ID]
            self.__text_box = tk.Text(self.__frame, height=15, width=self.__note_width, wrap=tk.WORD, bg=recent_note[COLUMN.BACK_COLOUR])
            self.__text_box.insert(tk.END, recent_note[COLUMN.CONTENT])
            self.__text_box.bind('<Double-1>', lambda event,sqlid=note_id: self.__clicked_note(event,sqlid))
            self.__text_box.grid(row=row, column=col, pady=3, padx=pad_x)
            self.__text_box['state'] = 'disabled'
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
        num_widgets_in_row = 1
        for pinned_note in pinned_notes:
            note_id = pinned_note[COLUMN.ID]
            self.__text_box = tk.Text(self.__frame, height=15, width=self.__note_width, wrap=tk.WORD, bg=pinned_note[COLUMN.BACK_COLOUR])
            self.__text_box.insert(tk.END, pinned_note[COLUMN.CONTENT])
            self.__text_box.bind('<Double-1>', lambda event, sqlid=note_id: self.__clicked_note(event, sqlid))
            self.__text_box.grid(row=row, column=col, pady=3, padx=pad_x)
            self.__text_box['state'] = 'disabled'
            if col == max_col:
                col = 0
                row += num_widgets_in_row
            else:
                col += 1


    def __get_search_results_view(self):
        self.clear_frame()
        self.__current_view = 'search results'
        self.__view_label["text"] = "Viewing Search Results"
        search_pages = self.__db.getSearchResults(self.__search_input.get(), 500, 0)
        if search_pages is None:
            print("No search results notes found")
            return

        pad_x = 3
        col = 0
        row = 0
        max_col = self.calculate_columns(self.__note_width,6)
        max_col -= 1 # -1 becuase of zero based index for grid
        num_widgets_in_row = 1
        for search_page in search_pages:
            note_id = search_page[COLUMN.ID]

            self.__text_box = tk.Text(self.__frame,height=15,width=self.__note_width, wrap=tk.WORD,
                        bg=search_page[COLUMN.BACK_COLOUR])
            self.__text_box.insert(tk.END, search_page[COLUMN.CONTENT])
            self.__text_box.bind('<Double-1>', lambda event, sqlid=note_id:self.__clicked_note(event, sqlid))
            self.__text_box.grid(row=row, column=col, pady=3, padx=pad_x)
            self.__text_box['state'] = 'disabled'
            if col == max_col:
                col = 0
                row += num_widgets_in_row
            else:
                col += 1

    def __change_notebook_colour(self, name):
        print (f"Will chnage notebook colour for {name}")
        colour = colorchooser.askcolor(title="Choose notebook colour", parent=self.__frame)
        if colour != (None,None):
            colour = str(colour[1])
            self.__db.setNotebookColour(name,colour)
            self.update_currrent_view()



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

        #get screen scale value (multiplier)
        scr_scale = int(conf.read_section('main', 'screen_scale'))

        
        #we need this becuase initially the screen size won't be reported becuase it has not gone through mainloop yet
        self.__root.update_idletasks()
        self.__root.update()

        screen_size = self.__root.winfo_width()

        num_chars = round(screen_size / (8 * scr_scale))

        #number of widgets that can fit horizintally on screen
        num_columns = round(num_chars  / (widget_width + border_size))

        #print(f"****** Calculated number of columns as {num_columns} *********")

        return num_columns

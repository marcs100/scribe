import tkinter as tk
from tkinter.constants import *
from database import database



global init
init = 0 # keeps track of open windows - we only want one open at a time.


class SearchWindow:
    #-------------------------------------------------------
    # init funtion
    # root = main root window to attch TOP
    # main_window = reference to the MainWindow classmethod
    # database = reference to the currently initialised database
    # config = refenece to an isnatnce the Config claass
    #-------------------------------------------------------
    def __init__(self, root_ref, main_window_ref, database, config):
        global init
        if init == 1:
            return # there is already a window open
        init = 1
        self._db = database
        self._conf = config
        self._main_window = main_window_ref
        self._root = root_ref
        self.init_window()
        self._notes_per_page = int(self._conf.read_section('main','notes per page'))
        self._search_query=''
        self._got_results = False

    #-------------------------------------------------------
    # Initialise the main search window
    #-------------------------------------------------------
    def init_window(self):
        self._search_window = tk.Toplevel(self._root)
        self._search_window.title('Search..')
        self._frame = tk.Frame(self._search_window, bg=self._conf.read_section('colours', 'widget bg'))
        mult_factor = int(self._conf.read_section('main','screen scale'))
        width = 400 * mult_factor
        height = 100 * mult_factor
        geometry = f"{width}x{height}"
        self._search_window.geometry(geometry)
        self._search_input = tk.StringVar()
        self._search_entry = tk.Entry(self._frame,
                                textvariable=self._search_input,
                                bg=self._conf.read_section('colours','search bg'),
                                fg=self._conf.read_section('colours','widget text'),
                                width=30,
                                font='Arial 12',
                                relief='sunken')

        self._search_entry.bind('<Return>', lambda event: self._do_search(event) )

        self._entry_label = tk.Label(self._frame, text='Enter search term...',
                        bg=self._conf.read_section('colours','widget bg'),
                        fg=self._conf.read_section('colours','widget text'))

        self._label = tk.Label(self._frame, text='...',
                        bg=self._conf.read_section('colours','widget bg'),
                        fg=self._conf.read_section('colours','widget text'))

        self._entry_label.pack()
        self._search_entry.pack(pady=20)
        self._label.pack(pady=10)
        self._frame.pack(fill='both', expand='true')

        self._search_window.protocol("WM_DELETE_WINDOW", self.close_search_window)
        self._search_window.attributes("-topmost", True)
        self._search_window.attributes('-type', 'dialog')

        self._search_entry.focus_set()

    #-------------------------------------------------------
    # Event - User indicated search input is complete
    #-------------------------------------------------------
    def _do_search(self,event):
        #print("*** event triggered -- do_search called ***");
        self._search_query = self._search_input.get()
        if self._search_input.get()!= '':
            print(f"searhing for ..... {self._search_query}")
            self._num_results = self._get_number_search_of_results()
            if self._num_results > 0:
                self._got_results = True
            self._label.configure(text=f"Found {self._num_results} results")
            #Send these search results back to the main Window
            self._main_window.received_search_results(self._num_results)

    #-------------------------------------------------------
    # Fetch the search results from the database
    # Search term is in self._search_input.get()
    #-------------------------------------------------------
    def _get_number_search_of_results(self):
        if(self._search_query == ''):
            return 0
        return self._db.getNumberOfSearchResults(self._search_query)

    #-------------------------------------------------------
    # Public facing function
    # Return the currenlt saved number of search results
    # withotu the need to intergatet the database
    #-------------------------------------------------------
    def get_number_search_of_results(self):
        return self._num_results

    #----------------------------------------------------
    # Public facing function to indicate if earch results
    # have been collected
    #----------------------------------------------------
    def has_search_results(self):
        return self._got_results


    #-------------------------------------------------------
    # Get all search results in one go.
    # Search term is in self._search_input.get()
    #-------------------------------------------------------
    def get_search_results(self):
        if(self._search_query == ''):
            return None
        search_results = self._db.getSearchResults(self._search_query)
        return search_results

    #-------------------------------------------------------
    # Get the a page of the search results.
    # The serach term is in self._search_input.get()
    #-------------------------------------------------------
    def get_search_results(self, page_number):
        print("Entered get_search_results(page_number)")
        print(f"page number: {str(page_number)}")
        if self._search_query == '':
            #print("self._search_query is empty")
            return None

        offset = (page_number-1) * self._notes_per_page

        if offset > self._num_results:
            return None

        print(f"notes per page: {str(self._notes_per_page)} offset: {str(offset)}")
        search_results = self._db.getSearchResults(self._search_query, self._notes_per_page, offset)
        print(f"Got {str(len(search_results))} in get_search_results()")
        return search_results


    #---------------------------------------
    #Return the number of pages for the
    #currrent search results
    #---------------------------------------
    def get_number_of_pages(self):
        #round down to nearest whole number
        num_pages = self._num_results // self._notes_per_page
        if self._num_results % self._notes_per_page > 0:
            num_pages +=1
        return num_pages



    #-----------------------------------------
    # Event - close the window
    # Reset init so a new window can be opened.
    #-----------------------------------------
    def close_search_window(self):
        global init
        init = 0;
        self._search_window.destroy()



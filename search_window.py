import tkinter as tk
from tkinter.constants import *
import database
from database import database
from tkinter import messagebox
import platform



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
        height = 150 * mult_factor
        geometry = f"{width}x{height}"
        self._search_window.geometry(geometry)

        #inner frame for search options and options label
        self._inner_frame = tk.Frame(self._search_window, bg=self._conf.read_section('colours', 'widget bg'))

        '''
        combo_style = ttk.Style()
        combo_style.configure('search.TCombobox', background=self._conf.read_section('colours','widget bg'),
                        foreground=self._conf.read_section('colours','widget text'),
                        font=('Arial', 12))

        #style='search.Combobox'
        self._combombox = ttk.Combobox(self._inner_frame, values = ['Any term', 'Whole word', 'Hash tag list'],
                                width=20, style='search.TCombobox')
        '''

        self._options_button = tk.Menubutton(self._inner_frame, text="...", relief="raised",
                                bg=self._conf.read_section('colours','widget bg'), fg=self._conf.read_section('colours', 'widget text'))
        self._options_button.menu = tk.Menu(self._options_button,tearoff=0)
        self._options_button["menu"] = self._options_button.menu

        self._selected_search_option = tk.StringVar(value="Standard *") # declare variable and set default radio on

        self._options_button.menu.add_radiobutton(label="Standard *", variable=self._selected_search_option,
                                value = "Standard *", command=lambda label_text="Search any term *": self._update_options_label(label_text))

        self._options_button.menu.add_radiobutton(label="Search exact term", variable=self._selected_search_option,
                                value = "Whole words only", command=lambda label_text="Search exact term": self._update_options_label(label_text))

        self._options_button.menu.add_radiobutton(label="Hash tag list", variable=self._selected_search_option,
                                value = "Hash tag list", command=lambda label_text="Search hash tags": self._update_options_label(label_text))

        self._options_label = tk.Label(self._inner_frame, bg=self._conf.read_section('colours','widget bg'),
                                      fg=self._conf.read_section('colours', 'widget text'), text="Search any term *",
                                      justify='right')

        self._search_input = tk.StringVar()
        self._search_entry = tk.Entry(self._frame,
                                textvariable=self._search_input,
                                bg=self._conf.read_section('colours','search bg'),
                                fg=self._conf.read_section('colours','widget text'),
                                width=30,
                                font='Arial 12',
                                relief='sunken')

        self._search_entry.bind('<Return>', lambda event: self._do_search(event) )

        self._entry_label = tk.Label(self._inner_frame, text='Options..',
                        bg=self._conf.read_section('colours','widget bg'),
                        fg=self._conf.read_section('colours','widget text'))

        self._label = tk.Label(self._frame, text='...',
                        bg=self._conf.read_section('colours','widget bg'),
                        fg=self._conf.read_section('colours','widget text'))


        self._spacer_label_1 = tk.Label(self._inner_frame, text="                    ",
                                bg=self._conf.read_section('colours', 'widget bg'),
                                fg=self._conf.read_section('colours', 'widget text'))

        self._spacer_label_2 = tk.Label(self._inner_frame, text="                                     ",
                                bg=self._conf.read_section('colours', 'widget bg'),
                                fg=self._conf.read_section('colours', 'widget text'))

        #self._entry_label.pack(side='left', fill='y', expand='true')
        #self._combombox.pack(side='right', fill='y', padx=200, pady=20)
        self._spacer_label_1.pack(side='right', fill='none', expand = 'false')
        self._options_button.pack(side='right',expand='false', fill='none')
        self._spacer_label_2.pack(side='left', fill='none', expand = 'false')
        self._options_label.pack(side='left', expand='true', fill='none')

        self._inner_frame.pack(fill='both', expand='true')
        self._search_entry.pack(pady=1)
        self._label.pack(pady=10)
        self._frame.pack(fill='both', expand='true')

        self._search_window.protocol("WM_DELETE_WINDOW", self.close_search_window)
        self._search_window.attributes("-topmost", True)
        if platform.system() == 'Linux':
            self._search_window.attributes('-type', 'dialog')

        self._search_entry.focus_set()


    #---------------------------------------------------------
    # Event to updat eoption label to corresond with selected
    # radio buttin in search oprions menu.
    #---------------------------------------------------------
    def _update_options_label(self, label_text):
        self._options_label['text']=label_text


    #-------------------------------------------------------
    # Event - User indicated search input is complete
    #-------------------------------------------------------
    def _do_search(self,event):
        #print("*** event triggered -- do_search called ***");
        self._search_query = self._search_input.get()
        if self._search_input.get()!= '':
            #print(f"searhing for ..... {self._search_query}")
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
        mode = self._get_search_mode()
        if mode == self._db.SEARCH_HASH_TAGS:
            search_list = self._convert_to_hashtag_list(self._search_query)
            return self._db.getNumberOfSearchResults(search_list, mode)
        else:
            return self._db.getNumberOfSearchResults(self._search_query, mode)

    #-------------------------------------------------------
    # Get the current search mode
    #-------------------------------------------------------
    def _get_search_mode(self):
        mode = None
        #print(f"selected search option is {self._selected_search_option.get()}")
        match self._selected_search_option.get():
            case  "Standard *":
                mode = database.SEARCH_STANDARD
            case "Whole words only":
                mode = database.SEARCH_WHOLE_WORDS
            case "Hash tag list":
                mode = database.SEARCH_HASH_TAGS
        return mode

    #-------------------------------------------------------
    # Public facing function
    # Return the currenlt saved number of search results
    # withotu the need to intergatet the database
    #-------------------------------------------------------
    def get_number_search_of_results(self):
        return self._num_results

    #----------------------------------------------------
    # Public facing function to indicate if search results
    # have been collected
    #----------------------------------------------------
    def has_search_results(self):
        return self._got_results


    #-------------------------------------------------------
    # Get all search results in one go.
    # Search term is in self._search_input.get()
    #-------------------------------------------------------
    ''' No function overiding in python!!!
    def get_search_results(self):
        if(self._search_query == ''):
            return None
        mode = self._get_search_mode()
        if mode == self._db.SEARCH_HASH_TAGS:
            search_list = self._convert_to_hashtag_list(self._search_query)
            search_results = self._db.getSearchResults(search_list, mode)
        else:
            search_results = self._db.getSearchResults(self._search_query, mode)
        return search_results
    '''

    #-------------------------------------------------------
    # Convert search string into a list of hashtags. Split
    # by comma and space. Add '#' to start of element if it
    # does not already start with '#'.
    # Remove any invalid has tags and propmt ther user with
    # a warning.
    #-------------------------------------------------------
    def _convert_to_hashtag_list(self, search_term):
        invalid_tags=[]
        got_error = False

        search_term = search_term.replace(',',' ') # replace any commas with a space
        search_list = search_term.split(' ')
        search_list = list(filter(None, search_list)) # filter out empty entries

        for index, term in enumerate(search_list):
            if term[0] != '#':
                term = '#' + term
                search_list[index] = term # add '#' to start of string if not there already

            #check there is only one # in the 'string''
            if term.count('#') > 1:
                invalid_tags.append(term)
                got_error = True

        #print (search_list)

        if got_error == True:
            #print("Invalid tags: ")
            #print(invalid_tags)
            #warn the user some invalid tags are going to be removed
            messagebox.INFO('Warning',
                            f"Removing invalid hash tags: {str(invalid_hash_tags)}")
            for term in invalid_tags:
                search_list.remove(term)

        return search_list


    #-------------------------------------------------------
    # Get a page of the search results.
    # The serach term is in self._search_input.get()
    #-------------------------------------------------------
    def get_search_results(self, page_number):
        #print("Entered get_search_results(page_number)")
        #print(f"page number: {str(page_number)}")
        if self._search_query == '':
            #print("self._search_query is empty")
            return None

        offset = (page_number-1) * self._notes_per_page

        if offset > self._num_results:
            return None

        #print(f"notes per page: {str(self._notes_per_page)} offset: {str(offset)}")
        mode = self._get_search_mode()

        mode = self._get_search_mode()
        search_results = None
        if mode == self._db.SEARCH_HASH_TAGS:
            search_list = self._convert_to_hashtag_list(self._search_query)
            search_results = self._db.getSearchResults(search_list, self._notes_per_page, offset, mode)
        else:
            search_results = self._db.getSearchResults(self._search_query, self._notes_per_page, offset, mode)

        #search_results = self._db.getSearchResults(self._search_query, self._notes_per_page, offset, mode)
        #print(f"Got {str(len(search_results))} in get_search_results()")
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



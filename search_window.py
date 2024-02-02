import tkinter as tk
from tkinter.constants import *
from database import database

init = 0 # keeps track of open windows - we only want one open at a time.
search_window=None
current_search = ''
config = None

#-------------------------------------------------------
# init funtion
# root = main root window to attch TOP
# main_window = reference to the MainWindow classmethod
# database = reference to the currently initialised database
# config = refenece to an isnatnce the Config claass
#-------------------------------------------------------
def initialise_search(root_ref, main_window_ref, database, config):
    global init
    if init == 1:
        return # there is already a window open
    global db
    db = database;
    global conf
    conf = config
    global root
    root = root_ref
    global main_window
    main_window = main_window_ref
    init_window()
    init = 1

#-------------------------------------------------------
# Initialise the main search window
#-------------------------------------------------------
def init_window():
    global search_window
    search_window = tk.Toplevel(root)
    search_window.title('Search..')
    frame = tk.Frame(search_window, bg=conf.read_section('colours', 'widget_bg'))
    mult_factor = int(conf.read_section('main','screen_scale'))
    width = 400 * mult_factor
    height = 100 * mult_factor
    geometry = f"{width}x{height}"
    search_window.geometry(geometry)
    global search_input
    search_input = tk.StringVar()
    search_entry = tk.Entry(frame,
                            textvariable=search_input,
                            bg=conf.read_section('colours','search_bg'),
                            fg=conf.read_section('colours','widget_text'),
                            width=30,
                            font='Arial 12',
                            relief='sunken')

    search_entry.bind('<Return>', lambda event: do_search(event) )

    global label
    label = tk.Label(frame, text='...',
                     bg=conf.read_section('colours','widget_bg'),
                     fg=conf.read_section('colours','widget_text'))

    search_entry.pack(pady=20)
    label.pack(pady=10)
    frame.pack(fill='both', expand='true')

    search_window.protocol("WM_DELETE_WINDOW", close_search_window)
    search_window.attributes("-topmost", True)

    search_entry.focus_set()

#-------------------------------------------------------
# Event - User indicated search input is complete
#-------------------------------------------------------
def do_search(event):
    #print("*** event triggered -- do_search called ***");
    global current_search
    current_search = search_input.get()
    if current_search != '':
        print(f"searhing for ..... {current_search}")
        search_results = get_search_results()
        num_results = db.getNumberOfSearchResults(search_input.get())
        label.configure(text=f"Found {num_results} results")
        #Send these search results back to the main Window
        main_window.get_search_results_view(search_results)

#-------------------------------------------------------
# Fetch the search results from the database
# and send back to main window
#-------------------------------------------------------
def get_search_results():
    global current_search
    current_search = search_input.get();
    search_results = db.getSearchResults(search_input.get(), 2000, 0)
    return search_results






#-----------------------------------------
# Event - close the window
# Reset init so a new window can be opened.
#-----------------------------------------
def close_search_window():
    global init
    init = 0;
    search_window.destroy()

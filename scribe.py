# This is a sample Python script.
import tkinter
from tkinter.constants import *
from database import database
import tkinter as tk
from tkinter import font
import columns as COLUMN
from note_window import NoteWindow
import constants as CONSTANTS

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

def clear_frame():
   for widgets in frame.winfo_children():
      widgets.destroy()

def clicked_note(event,sqlid):
    print("note id is " + str(sqlid))
    # open note for editing in new window
    note_window = NoteWindow(root)
    note_window.open_note(sqlid, db)

def clicked_notebook(event, name):
    print("notebook name is " + str(name))
    get_note_pages_view(3, name)



def get_view(view):
    print("Getting view: "+view)
    match view:
        case 'pinned':
            # I want to set the menu button checkbox thing here!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            get_pinned_notes_view(3)
        case 'recent':
            get_recent_notes_view(3)
        case 'notebooks':
            get_notebooks_view(3)

def get_note_pages_view(number_of_columns, notebook):
    clear_frame()
    view_label["text"] = "Viewing Notebook: " + notebook
    note_pages = db.getNotebook(notebook)
    if note_pages is None:
        print("No pinned notes found")
        return

    col = 0
    row = 0
    max_col = number_of_columns - 1
    num_widgets_in_row = 1
    for note_page in note_pages:
        note_id = note_page[COLUMN.ID]
        text_box = tk.Text(frame, height=15, width=50, wrap=tk.WORD, bg=note_page[COLUMN.BACK_COLOUR])
        text_box.insert(tk.END, note_page[COLUMN.CONTENT])
        text_box.bind('<Double-1>', lambda event, sqlid=note_id: clicked_note(event, sqlid))
        text_box.grid(row=row, column=col, pady=3, padx=3)
        if col == max_col:
            col = 0
            row += num_widgets_in_row
        else:
            col += 1

def get_notebooks_view(number_of_columns):
    clear_frame()
    view_label["text"] = "Viewing: Notebooks"
    col=0
    row=0
    max_col = number_of_columns-1
    num_widgets_in_row = 1
    notebook_names = db.getNotebookNames()
    if notebook_names is None:
        print("No notebooks found!")
        return
    for notebook_name in notebook_names:
        print("Notebook name is " + str(notebook_name[0]))
        colour = db.getNotebookColour(notebook_name[0])
        text_box = tk.Text(frame, height=5, width=30, wrap=tk.WORD, bg=colour)
        text_box.insert(tk.END, str(notebook_name[0]))
        text_box.bind('<Double-1>', lambda event,name=str(notebook_name[0]): clicked_notebook(event,name))
        text_box.grid(row=row, column=col, pady=3, padx=3)

        if col == max_col:
            col = 0
            row += num_widgets_in_row
        else:
            col += 1


def get_recent_notes_view(number_of_columns):
    clear_frame()
    view_label["text"] = "Viewing: Recent Notes"
    recent_notes = db.getRecentNotes(4)
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
        text_box = tk.Text(frame, height=15, width=50, wrap=tk.WORD, bg=recent_note[COLUMN.BACK_COLOUR])
        text_box.insert(tk.END, recent_note[COLUMN.CONTENT])
        text_box.bind('<Double-1>', lambda event,sqlid=note_id: clicked_note(event,sqlid))
        text_box.grid(row=row, column=col, pady=3, padx=3)

        print("row = " + str(row)+ " column = "+ str(col))

        if col == max_col:
            col = 0
            row += num_widgets_in_row
        else:
            col += 1


def get_pinned_notes_view(number_of_columns):
    clear_frame()
    view_label["text"] = "Viewing: Pinned Notes"
    pinned_notes = db.getPinnedNotes()
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
        text_box = tk.Text(frame, height=15, width=50, wrap=tk.WORD, bg=pinned_note[COLUMN.BACK_COLOUR])
        text_box.insert(tk.END, pinned_note[COLUMN.CONTENT])
        text_box.bind('<Double-1>', lambda event, sqlid=note_id: clicked_note(event, sqlid))
        text_box.grid(row=row, column=col, pady=3, padx=3)
        if col == max_col:
            col = 0
            row += num_widgets_in_row
        else:
            col += 1

    # for noteid in note_ids:
    #    print(str(noteid))

def get_curr_screen_geometry():
    """
    Workaround to get the size of the current screen in a multi-screen setup.
    """
    root = tk.Tk()
    root.update_idletasks()
    root.attributes('-fullscreen', True)
    root.state('iconic')
    #geometry = root.winfo_geometry()
    width = root.winfo_width()
    height = root.winfo_height()
    root.destroy()
    return (width,height)



def main():
    init_main_window()
    #defaultView = "recent"
    default_view = "pinned"
    get_view(default_view)
    root.mainloop()

def init_main_window():
    geometry = get_curr_screen_geometry()
    width = round(geometry[0] * 0.9)
    height = round(geometry[1] * 0.9)
    print ("Width = " + str(width))
    print("Height = " + str(height))
    print(geometry)
    root.geometry(f'{width}x{height}')
    # root.geometry('1400x800')
    root.title(CONSTANTS.APP_TITLE)

    lbl_font = font.Font(weight="bold")
    view_label["font"] = lbl_font

    menu = tk.Menubutton()
    view_button.menu = tk.Menu(view_button, bg=CONSTANTS.WIDGET_BACK_COLOUR, fg=CONSTANTS.WIDGET_TEXT_COLOUR)
    view_button["menu"] = view_button.menu

    view_button.menu.add_command(label="Pinned", command=lambda view="pinned": get_view(view))
    view_button.menu.add_command(label="Notebooks", command=lambda view="notebooks": get_view(view))
    view_button.menu.add_command(label="Recent Notes", command=lambda view="recent": get_view(view))

    spacer_label = tk.Label(menu_frame, text="          ", bg=CONSTANTS.WIDGET_BACK_COLOUR, fg=CONSTANTS.WIDGET_TEXT_COLOUR)

    menu_frame.pack(fill='both', expand=FALSE)
    frame.pack(fill='both', expand=TRUE)
    view_label.pack(fill=Y, side='right', padx=15, pady=6)
    spacer_label.pack(fill=Y, side='right')
    view_button.pack(fill=Y, side='right')
    #view_button.grid(row=0,column=0, padx=5)
    #view_label.grid(row=0, column=1)


#Global variables
db = database("/home/marc/Documents/marcnotes_db")
root = tk.Tk()
frame = tk.Frame(root,bg=CONSTANTS.WIDGET_BACK_COLOUR)
menu_frame = tk.Frame(root, bg=CONSTANTS.WIDGET_BACK_COLOUR)
view_button = tk.Menubutton(menu_frame, text="Select View", relief="flat", bg=CONSTANTS.WIDGET_BACK_COLOUR, fg=CONSTANTS.WIDGET_TEXT_COLOUR)
view_label = tk.Label(menu_frame,text="dummy",bg=CONSTANTS.WIDGET_BACK_COLOUR, fg=CONSTANTS.WIDGET_TEXT_COLOUR)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

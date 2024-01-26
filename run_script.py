from subprocess import Popen, PIPE
import tkinter as tk
import config_file as conf

def update_text_box(text_box, line_in):
    text_box.insert(tk.END, line_in)
    text_box.update()
    text_box.update_idletasks()

def close_window(window):
    window.destroy()

#Run a python script and pipe stdout and stderr to a tkinter window
def run_script(script_name):

    line = ""
    mult_factor = int(conf.read_section('main','screen_scale'))
    width = 750 * mult_factor
    height = 500 * mult_factor
    geometry = f"{width}x{height}"
    root = tk.Tk()
    root.geometry(geometry)
    root.title('Running python script...')
    text_box = tk.Text(root, wrap=tk.WORD, bg='#000000', fg='#ffffff')
    text_box.pack(fill='both', expand='true')

    button = tk.Button(root, relief='flat', text="Close",
                       command= lambda window=root: close_window(window))
    button['state'] = tk.DISABLED
    button.pack(fill='both', expand='true')

    root.update()

    with Popen (["/usr/bin/python3", script_name], stderr=PIPE,stdout=PIPE) as process:
        while True:
            line = process.stdout.read1().decode("utf-8")
            text_box.insert(tk.END, line)
            text_box.update()
            text_box.update_idletasks()
            root.update()
            if not line:

                while True: #look for errors
                    error = process.stderr.read1().decode("utf-8")
                    text_box.insert(tk.END, error)
                    text_box.update()
                    text_box.update_idletasks()
                    root.update()
                    if not error: break
                if not line: break
    button['state'] = tk.NORMAL
    root.mainloop()

    #print("Captured: " + result.stdout)






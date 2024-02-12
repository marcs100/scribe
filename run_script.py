from subprocess import Popen, PIPE
import tkinter as tk
import platform
import configuration_file

def update_text_box(text_box, line_in):
    text_box.insert(tk.END, line_in)
    text_box.update()
    text_box.update_idletasks()


#Run a python script and pipe stdout and stderr to a tkinter window
def run_script(script_name, config):

    line = ""
    mult_factor = int(config.read_section('main','screen scale'))
    width = 750 * mult_factor
    height = 500 * mult_factor
    geometry = f"{width}x{height}"
    root = tk.Tk()
    root.geometry(geometry)
    root.title('Running python script...')
    text_box = tk.Text(root, wrap=tk.WORD, bg='#000000', fg='#ffffff')
    text_box.pack(fill='both', expand='true')

    root.update()

    prog = '/usr/bin/python3'

    config_file = configuration_file.get_config_file()

    if platform.system() == 'Windows':
        prog = 'python'

    with Popen ([prog, script_name, config_file], stderr=PIPE,stdout=PIPE) as process:
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




    root.mainloop()

    #print("Captured: " + result.stdout)






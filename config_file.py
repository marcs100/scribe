import os.path
import configparser

config = configparser.ConfigParser()

def create_new_config_file():
    config.add_section('main')
    config.add_section('main_window')
    config.add_section('note_window')
    config.add_section('colours')
    
    config['main']['app_title'] = "Scribe v1.0"
    config['main']['database'] = "/home/marc/Documents/marcnotes_db"
    config['main']['recent_notes_count'] = "8"
    config['main']['default_notebook'] = "General"
    config['main']['screen_scale'] = "1"
    
    config['main_window']['default_view'] = "pinned"
    config['main_window']['width'] = "1000"
    config['main_window']['height'] = "600"
    config['main_window']['note_width'] = "50"
    config['main_window']['notebook_width'] = "30"

    config['colours']['widget_bg'] = '#303234' # blackish
    config['colours']['widget_text'] = '#e7edef' # off white (hint of blue)
    config['colours']['note_text'] = '#484445'
    config['colours']['default_note_bg'] = '#e7edef' # off white (hint of blue)
    
    write_config()


def write_config():
    with open("./scribe.config", 'w') as configfile:
        config.write(configfile)

def write_section(section, param, param_value, write_to_file):
    config[section][param] = param_value
    if write_to_file is True:
        write_config()



def read_section(section,parm):
    config.read("./scribe.config")
    return config[section][parm]

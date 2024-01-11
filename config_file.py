import os.path
import configparser
import constants as CONSTANTS

config = configparser.ConfigParser()

def create_new_config_file():
    config.add_section('main')
    config.add_section('main_window')
    config.add_section('note_window')
    config['main']['database'] = "/home/marc/Documents/marcnotes_db"
    config['main_window']['default_view'] = "pinned"
    write_config()

def write_config():
    with open(CONSTANTS.CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

def read(section,parm):
    config.read(CONSTANTS.CONFIG_FILE)
    return config[section][parm]

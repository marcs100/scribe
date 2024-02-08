import os.path
import configparser
import version_info

class Config:

    def __init__(self, config_file):
        self._config_file = config_file
        self._config = configparser.ConfigParser()

    def create_new_config_file(self):
        self._config.add_section('main')
        self._config.add_section('main_window')
        #config.add_section('note_window')
        self._config.add_section('colours')
        self._config.add_section('main window key bindings')
        self._config.add_section('note page key bindings')

        self._config['main']['app_title'] = "Scribe v1.0"
        if version_info.release == True:
            self._config['main']['database'] = "/home/marc/sync/scribe/scribe_data.db"
        else:
            self._config['main']['database'] = "/home/marc/Documents/marcnotes_db"
        self._config['main']['recent notes count'] = "8"
        self._config['main']['default notebook'] = "General"
        self._config['main']['screen scale'] = "1"
        self._config['main']['backup location'] = "/home/marc/Documents/backups/"
        self._config['main']['notes per page'] = "30"

        self._config['main_window']['default view'] = "pinned"
        self._config['main_window']['width'] = "1000"
        self._config['main_window']['height'] = "600"
        self._config['main_window']['note width'] = "50"
        self._config['main_window']['notebook width'] = "30"

        self._config['colours']['widget bg'] = '#303234' # blackish
        self._config['colours']['widget text'] = '#e7edef' # off white (hint of blue)
        self._config['colours']['note_text'] = '#484445'
        self._config['colours']['default note_bg'] = '#e7edef' # off white (hint of blue)
        self._config['colours']['default notebook_bg'] = '#e7edef' # off white (hint of blue)
        self._config['colours']['widget highlight'] = "#5f6260"
        self._config['colours']['search bg'] = "#6d7c7a"

        self._config['main window key bindings']['search'] = "<Control-f>"
        self._config['main window key bindings']['new note'] = "<Control-n>"
        self._config['main window key bindings']['show notebook view'] = "<Control-Alt-n>"
        self._config['main window key bindings']['show pinned notes view'] = "<Control-Alt-p>"
        self._config['main window key bindings']['show recent notes view'] = "<Control-Alt-r>"

        self._config['note page key bindings']['search'] = "<Control-f>"

        self.write_config()


    def write_config(self):
        with open(self._config_file, 'w') as configfile:
            self._config.write(configfile)

    def write_section(self, section, param, param_value, write_to_file):
        self._config[section][param] = param_value
        if write_to_file == True:
            self.write_config()

    def read_section(self, section,parm):
        self._config.read(self._config_file)
        return self._config[section][parm]

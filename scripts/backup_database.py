import shutil
import os
import sys
import datetime

def we_are_frozen():
    # All of the modules are built-in to the interpreter, e.g., by py2exe
    return hasattr(sys, "frozen")

def module_path():
    encoding = sys.getfilesystemencoding()
    if we_are_frozen():
        return os.path.dirname(str(sys.executable))
    return os.path.dirname(str(__file__))



#current_working_directory = os.getcwd()
source_directory = module_path()
#path = os.path.abspath(this.__file__)
#print("** current source path is: "  + str(source_directory))

#now we need to remove the last directory to move one step down
source_dir_split = source_directory.split('/')
#print("Split string is "+ str(source_dir_split))

#Will need to do something for windows here!!!!!!!!!!!!!
#source_directory = "/"

source_directory = ""

for index in range(len(source_dir_split)-1):
    source_directory += source_dir_split[index] + "/"

#print("** Modified source path is: "  + str(source_directory))

#The script directoty must be one level up from the main source code!
if source_directory not in sys.path:
    sys.path.append(source_directory)

 #Now we cann access Scribe modules
import config_file

print("---------------------------------")
print("|    Backing up database file   |")
print("---------------------------------")
print("\n")

#get backuo loaction from config file
backup_location = config_file.read_section('main','backup_location')
db_file_with_path = config_file.read_section('main','database')

#The db file imcludes the path so we need to strip the file name from it
head, db_file = os.path.split(db_file_with_path)

time_stamp = str(datetime.datetime.now())
time_stamp = time_stamp.replace(":", "_") # needed for Windows OS

backup_file = db_file + "-" + time_stamp + ".db"

print (f"Creating backup {backup_location}{backup_file}\n")


os.makedirs(backup_location, exist_ok=True)

print(f"Copying {db_file_with_path} to {backup_file}")
shutil.copyfile(db_file_with_path,backup_location+backup_file)

print ("** Backup successful **")


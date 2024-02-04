import shutil
import os
import sys
import datetime
import configparser

def main():

    num_args = len(sys.argv)
    if(num_args == 1 ):
        print("Error: expecting argument but none given")
        return

    conf_file = str(sys.argv[1])
    #print(f"Got argument: {conf_file}")

    config = configparser.ConfigParser()
    config.read(conf_file)

    print("---------------------------------")
    print("|    Backing up database file   |")
    print("---------------------------------")
    print("\n")

    backup_location = config['main']['backup_location']
    db_file_with_path = config['main']['database']

    #The db file imcludes the path so we need to strip the file name from it
    head, db_file = os.path.split(db_file_with_path)

    time_stamp = str(datetime.datetime.now())
    time_stamp = time_stamp.replace(":", "_") # needed for Windows OS

    backup_file = db_file + "-" + time_stamp + ".db"

    print (f"Creating backup file: {backup_file}\n")
    print (f"Bachup location {backup_location}\n\n")


    os.makedirs(backup_location, exist_ok=True)

    print(f"Copying {db_file_with_path} to {backup_location}{backup_file}\n\n")
    shutil.copyfile(db_file_with_path,backup_location+backup_file)

    print ("** Backup successful **")

if __name__ == "__main__":
    main()


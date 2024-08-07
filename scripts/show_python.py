#import shutil
import os
import sys
import datetime
import configparser
import subprocess

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
    print("|    Python origin              |")
    print("---------------------------------")
    print("\n")

    #shutil.copyfile(db_file_with_path,backup_location+backup_file)
    result = subprocess.run(['which', 'python'], capture_output=True)
    print(result.stdout)

if __name__ == "__main__":
    main()


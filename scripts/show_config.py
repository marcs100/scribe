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

    for section in config.sections():
        print(f"\n[{section}]")
        for (key, val) in config.items(section):
            print(f"{key} = {val}")


if __name__ == "__main__":
    main()


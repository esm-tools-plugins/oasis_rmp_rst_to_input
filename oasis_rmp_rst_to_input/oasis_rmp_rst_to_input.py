import os
import sys
import yaml

import argparse

def oasis_rmp_rst_to_input(config):
    """
    Copies rmp and rst OASIS files from experiments to input folders
    """
    print(config)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", default=None, help="config file to use for testing")

    parsed_args = vars(parser.parse_args())

    config_file = parsed_args["config_file"]
    if os.path.isfile(config_file):
        with open(config_file, "r") as cf:
            config = yaml.load(cf, Loader=yaml.FullLoader)
        if "dictitems" in config:
            config = config["dictitems"]
        oasis_rmp_rst_to_input(config)
    else:
        print(f"The 'config_file' specified ({config_file}) does not exist")
        sys.exit(0)

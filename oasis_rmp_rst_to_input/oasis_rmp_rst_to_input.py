import os
import sys
import yaml

import argparse
import shutil

def oasis_rmp_rst_to_input(config, user_pool=None):
    """
    Copies rmp and rst OASIS files from experiments to input folders
    """
    if "oasis3mct" not in config or "general" not in config:
        plugin_error(
            "This plugin only works if the simulation uses 'oasis3mct' and 'general'."
        )
        return config

    general = config["general"]
    oasis = config["oasis3mct"]

    # Check necessary variables exist and are not empty
    var_dict = {
        "oasis3mct": ["pool_dir"],
        "general": ["pool_dir"],
        "fesom": ["nproc"]
    }
    for section, variables in var_dict.items():
        for var in variables:
            if var not in config[section]:
                plugin_error(f"Variable '{section}.{var}' does not exist.")
                return config
            if not config[section][var]:
                plugin_error(f"Variable '{section}.{var}' is empty.")
                return config

    # Check if the pool_dir is writable
    pool_dir = general["pool_dir"]
    oasis_pool = oasis["pool_dir"]
    if iswritable(oasis_pool) or user_pool:
        # Check syntax, pool_dir should be part of the oasis_pool
        if pool_dir not in oasis_pool:
            plugin_error(
                f"The oasis pool ('{oasis_pool}') does not contain the general pool "
                + f"('{pool_dir}')."
            )
            return config
        # Check for a user-defined pool, only for testing
        if user_pool:
            if iswritable(user_pool):
                oasis_pool = oasis_pool.replace(pool_dir, user_pool)
            else:
                plugin_error(
                    f"The pool defined by the user ('{user_pool}') is not writable."
                )
                return config
        # Check if the target folder exist and if not, create it
        folder = f"{oasis_pool}/{config['fesom']['nproc']}/"
        if not os.path.isdir(folder):
            try:
                os.makedirs(folder)
            except PermissionError:
                plugin_error(
                    f"You don't have the writing permissions to create {folder}."
                )
        # Check files existance and copy!
    else:
        plugin_error(
            f"You do not have write access to the oasis pool dir ('{pool_dir}')"
        )

    return config


def plugin_error(sentence):
    print(sentence)
    print("Does nothing and moves on into the next step of the recipe.")


def iswritable(path):
    if os.access(path, os.W_OK) is not True:
        return False
    else:
        return True


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", default=None, help="config file to use for testing")

    parsed_args = vars(parser.parse_args())

    user_pool = "/work/ollie/mandresm/esm_yaml_test/"

    config_file = parsed_args["config_file"]
    if os.path.isfile(config_file):
        with open(config_file, "r") as cf:
            config = yaml.load(cf, Loader=yaml.FullLoader)
        if "dictitems" in config:
            config = config["dictitems"]
        oasis_rmp_rst_to_input(config, user_pool)
    else:
        print(f"The 'config_file' specified ({config_file}) does not exist")
        sys.exit(0)

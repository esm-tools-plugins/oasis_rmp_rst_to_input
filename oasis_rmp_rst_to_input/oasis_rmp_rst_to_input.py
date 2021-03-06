import os
import sys
import yaml
import shutil

def oasis_rmp_rst_to_input(config, user_pool=None):
    """
    Copies rmp and rst OASIS files from experiments to input folders.
    You can include this plugin into your simulations by adding the
    ``oasis_rmp_rst_to_input`` step to the simulation recipe.

    For testing purposes, you can also choose to run the python file
    (``python3 oasis_rmp_rst_to_input.py <config_file> [--pool <user_input_folder>]``).
    This will read the ``<config_file>`` from a experiment and perform the same
    operations as when executed from the recipe. If ``user_input_folder`` is specified,
    the ``pool_dir`` defined in the ``config_file`` will be ignored and
    ``user_input_folder`` will be used as a target pool directory for the copying.
    ``user_input_folder`` feature is only available outside of a recipe.
    """

    # This plugin should never crush a simulation, therefore, everything is done
    # inside a try block
    try:
        # Get verbose mode
        verbose = config.get("general", {}).get("verbose", True)
        # Run sanity checks and recover some useful variables from the config
        check_passed, input_dir, restart_folder = check_vars_and_writing_permisions(
            config, user_pool, verbose
        )
        if check_passed:
            # Check if the target folder exists and if not, create it
            target_folder = f"{input_dir}/{config['fesom']['nproc']}/"
            if not os.path.isdir(target_folder):
                try:
                    os.makedirs(target_folder)
                except PermissionError:
                    plugin_error(
                        "You don't have the writing permissions to create "
                        + f"{target_folder}."
                    )
            # List oasis restarts in the experiment
            restart_files = []
            ignore_restarts = ["areas.nc", "grids.nc", "masks.nc"]
            for f in os.listdir(restart_folder):
                if f not in ignore_restarts and f.endswith(".nc"):
                    restart_files.append(f)
            if not restart_files:
                plugin_error(
                    "No restart files to be copied from the experiment "
                    + f"directory ('{restart_folder}')"
                )
            # Check files existence and copy
            if verbose:
                print(f"Copying files to input folder ('{target_folder}')...")
            for restart_file in restart_files:
                if os.path.isfile(f"{target_folder}/{restart_file}") and verbose:
                    print(f"\t{restart_file}: already exists and won't be copied")
                else:
                    shutil.copy2(
                        f"{restart_folder}/{restart_file}",
                        f"{target_folder}/{restart_file}"
                    )
                    if verbose:
                        print(f"\t{restart_file}: successfully copied")

    except:
        plugin_error(
            "Something unexpected happened during the execution of this plugin.",
            verbose
        )

    return config


def check_vars_and_writing_permisions(config, user_pool, verbose):
    """
    Sanity checks and replacing the ``user_pool`` if defined.
    """

    check_passed = True
    input_dir = None
    restart_folder = None

    # Check dictionaries
    if "oasis3mct" not in config or "general" not in config:
        plugin_error(
            "This plugin only works if the simulation uses 'oasis3mct' and 'general'.",
            verbose
        )
        check_passed = False

    general = config["general"]
    oasis = config["oasis3mct"]

    # Check that the necessary variables exist and are not empty
    var_dict = {
        "oasis3mct": ["pool_dir", "input_dir", "experiment_restart_out_dir"],
        "general": ["run_number"],
        "fesom": ["nproc"]
    }
    for section, variables in var_dict.items():
        for var in variables:
            if var not in config[section]:
                plugin_error(f"Variable '{section}.{var}' does not exist.", verbose)
                check_passed = False
            if not config[section][var]:
                plugin_error(f"Variable '{section}.{var}' is empty.", verbose)
                check_passed = False

    # Check if it is the first run
    if general["run_number"] == 1 and verbose:
        print("Nothing to do for the first leg.")
        return False, None, None

    # Check if the pool_dir is writable
    pool_dir = oasis["pool_dir"]
    input_dir = oasis["input_dir"]
    if iswritable(pool_dir) or user_pool:
        # Check syntax, pool_dir should be part of the input_dir
        if pool_dir not in input_dir:
            plugin_error(
                (
                    f"The oasis input dir ('{input_dir}') does not contain the general "
                    + f"pool ('{pool_dir}')."
                ),
                verbose
            )
            check_passed = False
        # Check if the input_dir exists and is writable
        if not iswritable(input_dir) and os.path.isdir(input_dir) and not user_pool:
            plugin_error(
                f"You do not have write access to the oasis input dir ('{input_dir}')",
                verbose
            )
            check_passed = False
        # Check for a user-defined pool, only for testing, ``user_pool`` is None when
        # run from a recipe
        if user_pool:
            if iswritable(user_pool):
                input_dir = input_dir.replace(pool_dir, user_pool)
            else:
                plugin_error(
                    f"The pool defined by the user ('{user_pool}') is not writable.",
                    verbose
                )
                check_passed = False
        # Check if restart folder exists
        restart_folder = config["oasis3mct"]["experiment_restart_out_dir"]
        if not os.path.isdir(restart_folder):
            plugin_error(
                f"The restart folder {restart_folder} does not exist.",
                verbose
            )
            check_passed = False
    else:
        plugin_error(
            f"You do not have write access to the pool dir ('{pool_dir}')",
            verbose
        )
        check_passed = False

    return check_passed, input_dir, restart_folder


def plugin_error(sentence, verbose):
    """
    Error message.
    """
    if verbose:
        print(sentence)
        print("Does nothing and moves on into the next step of the recipe.")


def iswritable(path):
    """
    Method to find wheter a directory is writable or not.
    """
    if os.access(path, os.W_OK) is not True:
        return False
    else:
        return True


if __name__ == "__main__":
    """
    Script to use when executing externally to a simulation.
    """

    import argparse

    # Parse input
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", default=None, help="config file to use for testing")
    parser.add_argument("-p", "--pool", default=None)

    parsed_args = vars(parser.parse_args())

    user_pool = parsed_args["pool"]
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

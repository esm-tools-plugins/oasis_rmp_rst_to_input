======================
oasis_rmp_rst_to_input
======================

A plugin to copy the OASIS remapping and restart files from the experiment directory
into the input folder following a given structure. This plugin is design for `AWICM3`.

Installation
------------

For testing simply clone this package and run::

    pip install -e .

Testing
-------

You can test this pluggin outside of run time by executing the
``oasis_rmp_rst_to_input.py`` and giving it a ``config_file`` as an input::

    python3 oasis_rmp_rst_to_input/oasis_rmp_rst_to_input.py <config_file.yaml> [-p <pool_dir>]

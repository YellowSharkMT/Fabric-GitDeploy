Install the package to a `virtualenv`:

    python setup.py develop

The recommended way to use it is to first create a folder in the root of your project, named `fabfile/`, and populate it like so:

    fabfile/
        - __init__.py
        - config.py

See the files in this sample app for more info, you should be able to use them as a template for your own project(s).

You could also do the following in that `fabfile/__init__.py` script:

    # fabfile/__init__.py
    import os
    os.environ['FAB_CONFIG'] = '/path/to/config.py'
    from fabfile import *

Obviously you can break out of the structure defined above, by calling `fab` with the `-f` parameter, like so:

    fab -f /path/to/fab_some_project.py [commands]

Doing so would allow you to place both the fabfile and the config file in completely arbitrary locations, inside or outside of the project root.
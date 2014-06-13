#Fabric-GitDeploy

This is a WordPress-centric [Fabric](http://fabfile.org) package that contains a number of tasks to aid in the process of deploying web apps. It should be easily modified to suit other applications besides WordPress though, as it covers several common needs: shuffling databases, pushing to & pulling from Git repositories, and synchronizing unversioned files (like uploaded assets, sitemaps, etc). 

See `fab -l` for list of tasks, and `fab -d TASKNAME` for detailed information on a task.

There are variables to configure at the top of the `fabfile/__init__.py` script before using this script.

##Available tasks:

    db         Copies the database from one server to another, essentially an export/import. (src: prod, dest: local)
    deploy     Deploys your local code to a remote server. (dest: prod, branch: master, dest_branch: master)
    dump       Dumps a database, then downloads it to `backup/` folder. Useful for performing back-ups. (src: prod, fetch_dump: True)
    provision  NOT RECOMMENDED - Provisions web root & archive folders, as well as git repo.
    restart    Executes any commands defined in the APP_RESTART_COMMANDS config value.
    rsync      Synchronizes the unversioned folders from one environment to another. (src: prod, dest: local)
    sync       Synchronizes the database and un-versioned files from one environment to another. (src: prod, dest: local)
    test       Tests connection to a specified host. (dest: prod)
    upgrade    Upgrades the Fabric-GitDeploy package.

##Information on tasks:

###`db`

Copies the database from one server to another, essentially an export/import. (src: prod, dest: local)

This involves dumping a database, downloading it to the local server if necessary, inserting it into the
destination server, and then updating a few database entries to make WordPress work on the destination server
(like wp_options/home, and wp_options/siteurl).

Example usage:

- `fab db            # Runs task with the default parameters, same as the following:`
- `fab db:prod,local # Updates the local database with the latest database dump from the production server.`
- `fab db:prod,dev   # This does the same as above, except the destination is to the dev server.`

Note: using "local" as a source is not currently supported.

Arguments: src='prod', dest='local'

###`deploy`

Deploys your local code to a remote server. (dest: prod, branch: master, dest_branch: master)

This task pushes your local git repo to the destination server, then updates the destination's webroot via
`git pull`. Then it executes any post-deployment tasks, like setting file permissions, as well as deleting any
sensitive files from the webroot (.git files, Gruntfile, Vagrant configs, etc. See the `_post_deploy()` function
for more info), restarting PHP (to flush the opcode cache), and flushing the Varnish cache.

Example usage:

- `fab deploy        # Most common, this pushes latest local updates to the production server.`
- `fab deploy:prod   # Same as above, as "prod" is the default destination.`
- `fab deploy:dev    # Deploys code to the dev server`

Arguments: dest='prod', branch='master', dest_branch='master'

###`dump`

Dumps a database, then downloads it to `backup/` folder. Useful for performing back-ups. (src: prod, fetch_dump: True)

Example usage:

- `fab dump            # dumps the prod database, downloads it to the local `backup/` folder.`
- `fab dump:prod,True  # same as above, these are the task defaults.`
- `fab dump:dev,False  # dumps the dev environment's database, but does NOT download it, this just leaves it on the remote server.`

Note that there is no "cleanup" command or anything that deletes these dump files from the remote server, so if you
have space constraints, you'll need to manually go in and purge the `archives` directory (which is defined at the
top of this file).

Arguments: src='prod', fetch_dump=True

###`provision`

NOT RECOMMENDED - Provisions web root & archive folders, as well as git repo.

This task has not been hard-tested, and since it rarely needs to be done, there hasn't been much effort put into
scripting this aspect of things, especially considering all of the error-handling that would need to go on with this.

Instead, consider it a rough guide of things to do, in order to set up a new location for deployment.

Arguments: dest=None

###`restart`

Executes any commands defined in the APP_RESTART_COMMANDS config value.

Arguments: dest='prod'

###`rsync`

Synchronizes the unversioned folders from one environment to another. (src: prod, dest: local)

Typically this is used to download the WordPress uploads folder from the production server, as well as any other
folders defined in the UNVERSIONED_FOLDERS config value. Note that this function DOES NOT copy/transfer any of the
application code - that must be done instead using the "deploy" task.

Example usage:

- `fab rsync             # Default params, same as following command.`
- `fab rsync:prod,local  # Downloads unversioned files from the production to the local server.`
- `fab rsync:local,prod  # NOT RECOMMENDED - have not developed/tested this yet.`
- `fab rsync:local,dev   # NOT RECOMMENDED - have not developed/tested this yet.`
- `fab rsync:prod,dev    # NOT RECOMMENDED - have not tested this, nor is it necessary UNLESS the dev server is on a different server than the prod server. Also, not sure rsync supports one remote to another.`

Arguments: src='prod', dest='local'

###`sync`

[COMMON] Synchronizes the database and un-versioned files from one environment to another. (src: prod, dest: local)

Typically this task is used to update the local environment so that it matches the production server. For more
information on either the datbase synchronization procedure, or the way it synchronizes the files, see the
"sync_db" and "sync_files" tasks. Note that this task DOES NOT copy/transfer any application code, that must be
done instead using the "deploy" task.

Example usage:

- `fab sync              # Updates local site with latest database & files from the prod site`
- `fab sync:local,dev    # NOT RECOMMENDED - have not developed/tested this functionality.`
- `fab sync:local,prod   # NOT RECOMMENDED - have not developed/tested this functionality.`

Arguments: src='prod', dest='local'

###`test`

Tests connection to a specified host. (dest: prod)

Example usage:

- `test:dev`
- `test:prod`

Arguments: dest='prod'

###`upgrade`

No docstring provided
Arguments: self


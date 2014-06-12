from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import exists
from fabric.context_managers import quiet
from contextlib import contextmanager
import time
import os
import sys
import re

env.use_ssh_config = True


# ## -------- Local Settings ------------- ###
PROJECT_NAME = 'PROJECT_NAME'

# Table prefix for the WordPress database.
WP_PREFIX = 'wp'

# Contents of these folders will be downloaded to this machine. Typically you would include at the least the uploads directory.
UNVERSIONED_FOLDERS = [
    'blog/wp-content/uploads'
]

# This controls whether the info-header is shown.
SHOW_HEADER = False
if SHOW_HEADER:
    def _print_header():
        print('** Fabfile for WEBSITE.com, contact YOUR NAVE <YOUREMAIL@EMAIL.COM> with questions.')
        print('** Use `fab -l` to list all tasks.')
        print('** Use `fab -d TASKNAME` to show documentation & usage examples for a task.')
        print('** Ex. usage: `fab deploy:dev sync:prod,dev`')
        print('** For more information on Fabric, visit http://fabfile.org.')
        print('')

    _print_header()

# Controls output of the `run()` commands. For verbose output, set this to `False`.
QUIET_COMMANDS = True


### -------- Environments --------------- ###
env['local'] = {
    'hostname': 'localhost',
    'home_url': 'http://local.website.com/',
    'wp_url': 'http://local.website.com/',
    'archive': '~/backup',
    'root': '~/www',
    'db': {
        'user': 'DB_USER',
        'password': 'DB_PASS',
        'name': 'DB_NAME',
        'host': 'DB_HOST_NAME',
    }
}

env['dev'] = {
    'hostname': 'user@server',  # Can use hosts defined in SSH config here
    'home_url': 'http://dev.website.com/',
    'wp_url': 'http://dev.website.com/',
    'archive': '~/webapps/PROJECT_NAME/archives',
    'root': '~/webapps/PROJECT_NAME/dev',
    'repo': '~/webapps/PROJECT_NAME/PROJECT_NAME.git',
    'db': {
        'user': 'DB_USER',
        'password': 'DB_PASS',
        'name': 'DB_NAME',
        'host': 'DB_HOST_NAME',
    }
}

env['prod'] = {
    'hostname': 'user@server',  # Can use hosts defined in SSH config here
    'home_url': 'http://www.website.com/',
    'wp_url': 'http://www.website.com/blog/',
    'archive': '~/webapps/PROJECT_NAME/archives',
    'root': '~/webapps/PROJECT_NAME/www',
    'repo': '~/webapps/PROJECT_NAME/PROJECT_NAME.git',
    'db': {
        'user': 'DB_USER',
        'password': 'DB_PASS',
        'name': 'DB_NAME',
        'host': 'DB_HOST_NAME',
    }
}


### --------------- Fabric Tasks --------------------- ###
@task
def deploy(dest='prod', branch='master', dest_branch='master'):
    """
    [COMMON] Deploys your local code to a remote server. (dest: prod, branch: master, dest_branch: master)

    This task pushes your local git repo to the destination server, then updates the destination's webroot via
    `git pull`. Then it executes any post-deployment tasks, like setting file permissions, as well as deleting any
    sensitive files from the webroot (.git files, Gruntfile, Vagrant configs, etc. See the `_post_deploy()` function
    for more info), restarting PHP (to flush the opcode cache), and flushing the Varnish cache.

    Example usage:

    - `fab deploy        # Most common, this pushes latest local updates to the production server.`
    - `fab deploy:prod   # Same as above, as "prod" is the default destination.`
    - `fab deploy:dev    # Deploys code to the dev server`

    """
    with lcd(env.local['root']):
        print('Pushing %s branch to %s:%s...' % (branch, dest, dest_branch))
        cmd = lambda: local('git push %s %s:%s' % (dest, branch, dest_branch))
        _filter_quiet_commands(cmd)

    with _host(dest):
        with cd(env[dest]['root']):
            # note the dependency on the remote name "origin"
            print('Updating destination from %s:%s...' % (dest, dest_branch))
            run('git reset --hard && git pull origin %s' % dest_branch, quiet=QUIET_COMMANDS)

        _post_deploy(dest)


@task
def test(env_name):
    """
    Tests connection to a specified host. (env_name)

    Example usage:

    - `test:dev`
    - `test:prod`
    """
    with _host(env_name):
        print('Executing `uname -a` on %s' % env_name)
        run('uname -a')


@task
def sync(src='prod', dest='local'):
    """
    [COMMON] Synchronizes the database and un-versioned files from one environment to another. (src: prod, dest: local)

    Typically this task is used to update the local environment so that it matches the production server. For more
    information on either the datbase synchronization procedure, or the way it synchronizes the files, see the
    "sync_db" and "sync_files" tasks. Note that this task DOES NOT copy/transfer any application code, that must be
    done instead using the "deploy" task.

    Example usage:

    - `fab sync              # Updates local site with latest database & files from the prod site`
    - `fab sync:local,dev    # NOT RECOMMENDED - have not developed/tested this functionality.`
    - `fab sync:local,prod   # NOT RECOMMENDED - have not developed/tested this functionality.`
    """
    sync_db(src, dest)
    sync_files(src, dest)


@task(name='db')
def sync_db(src='prod', dest='local'):
    """
    Copies the database from one server to another, essentially an export/import. (src: prod, dest: local)

    This involves dumping a database, downloading it to the local server if necessary, inserting it into the
    destination server, and then updating a few database entries to make WordPress work on the destination server
    (like wp_options/home, and wp_options/siteurl).

    Example usage:

    - `fab db            # Runs task with the default parameters, same as the following:`
    - `fab db:prod,local # Updates the local database with the latest database dump from the production server.`
    - `fab db:prod,dev   # This does the same as above, except the destination is to the dev server.`

    Note: using "local" as a source is not currently supported.
    """

    if src == 'local':
        print('Using the local database as a source is not currently supported.')
        return

    dump_fn = dump(src, False)
    if dest == 'local':
        fetch_result = _fetch(src, dump_fn)
        insert_dump_fn = fetch_result[0]
    else:
        insert_dump_fn = dump_fn

    insert_cmd = 'mysql -u %(user)s -p%(password)s -h %(host)s %(name)s' % env[dest]['db']
    cmd = 'gunzip < %s | %s' % (insert_dump_fn, insert_cmd)
    print('Inserting database....')

    if dest == 'local':
        _filter_quiet_commands(cmd)
    else:
        with _host(dest):
            run(cmd, quiet=QUIET_COMMANDS)
    _migrate(dest)


@task(name='rsync')
def sync_files(src='prod', dest='local'):
    """
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
    """
    for dir in UNVERSIONED_FOLDERS:
        cmd_vars = {
            'src_host': env[src]['hostname'],
            'dest_host': env[dest]['hostname'],
            'root': env[src]['root'],
            'dest_root': env[dest]['root'],
            'dir': dir,
            'extra_options': '--cvs-exclude',
        }
        if src == 'local':
            cmd = 'rsync -ravz %(extra_options)s %(root)s/%(dir)s/ %(dest_host)s:%(dest_root)s/%(dir)s' % cmd_vars
        else:
            cmd = 'rsync -ravz %(extra_options)s %(src_host)s:%(root)s/%(dir)s/ %(dest_root)s/%(dir)s' % cmd_vars
        print('Syncing unversioned files...')
        with quiet():
            local(cmd)
    pass


@task
def dump(src='prod', fetch_dump=True):
    """
    Dumps a database, then downloads it to `backup/` folder. Useful for performing back-ups. (src: prod, fetch_dump: True)

    Example usage:

    - `fab dump            # dumps the prod database, downloads it to the local `backup/` folder.`
    - `fab dump:prod,True  # same as above, these are the task defaults.`
    - `fab dump:dev,False  # dumps the dev environment's database, but does NOT download it, this just leaves it on the remote server.`

    Note that there is no "cleanup" command or anything that deletes these dump files from the remote server, so if you
    have space constraints, you'll need to manually go in and purge the `archives` directory (which is defined at the
    top of this file).
    """
    with _host(src):
        cmd_vars = env[src]['db']
        #print cmd_vars
        #return
        dump_cmd = 'mysqldump -u %(user)s -p%(password)s -h %(host)s %(name)s' % cmd_vars
        dump_fn_stem = '%s-%s.%s' % (PROJECT_NAME, time.strftime("%Y.%m.%d-%H.%M.%S"), src)
        dump_fn = '%s/%s.sql.gz' % (env[src]['archive'], dump_fn_stem)
        cmd = '%s | gzip > %s' % (dump_cmd, dump_fn)
        print('Dumping database...')
        run(cmd, quiet=QUIET_COMMANDS)

    if fetch_dump and src != 'local':
        _fetch(src, dump_fn)

    return dump_fn


@task
def restart(dest=None):
    """
    Restarts the PHP-FPM & Varnish services. (dest)

    This is typically executed as part of deploying the application code, in order to flush to PHP opcode cache, as
    well as the Varnish cache. Both of those services are controlled by supervisor, so this just involves sending a
    command to supervisorctl.

    Typically this `restart()` task is invoked by other tasks, but it can be useful to run it on its own sometimes,
    especially if updating files on the remote server manually (for whatever reason).

    Note that for high-load environments, where ZERO downtime is allowed, you'll want to look into graceful reloads,
    either with supervisor, or with your own server-land script(s).
    """
    if dest is None:
        dest = 'prod'

    with _host(dest):
        print('Restarting PHP & Varnish...')
        run('/home/PROJECT_NAME/bin/supervisorctl restart php-fpm: varnish:', quiet=QUIET_COMMANDS)


def _provision(dest):
    """
    NOT RECOMMENDED - Provisions web root & archive folders, as well as git repo.

    This task has not been hard-tested, and since it rarely needs to be done, there hasn't been much effort put into
    scripting this aspect of things, especially considering all of the error-handling that would need to go on with this.

    Instead, consider it a rough guide of things to do, in order to set up a new location for deployment.
    """
    with _host(dest):
        for dir in ['archive', 'root', 'repo']:
            try:
                run('mkdir -p %s' % env[dest][dir])
            except Exception as e:
                print('Could not make the `%s` folder: %s' % (dir, e.message))

        with cd(env[dest]['repo']):
            try:
                run('git init --bare')
            except Exception as e:
                print('Could not initialize the git repo: %s' % e.message)
                sys.exit(0)

            try:
                local('git remote add %s %s' % (dest, env[dest]['repo']))
                local('git push %s --all' % dest)
            except:
                print('Problems configuring local git remote and/or pushing it to the destination.')
                sys.exit(0)

        with cd(env[dest]['root']):
            try:
                run('git init')
                run('git remote add origin %s' % env[dest]['repo'])
                run('git pull origin master')
            except:
                print('Problems configuring destination web root.')
                sys.exit(0)


### ----- Private Functions -------- ###
def _migrate(dest='local'):
    """
    Updates WordPress database so it works on a different server (dest: local).
    Typically this task is executed immediately after inserting newer contents into a database, like as part of the
    "sync" task. It updates a couple options in WordPress to make the site run on a different hostname. See the
    `_make_update_sql()` function for more detailed information on the database commands that are executed.

    It is strongly advised that you DO NOT RUN THIS ON A PRODUCTION DATABASE. (but you could...) The normal use-case
    for this command, aside from the scenario described above, were if you were developing something that required
    you to constantly reset the database with a specific file. Rather than running the `sync()` task, you might want to
    just insert a file that's already been downloaded by a previous sync, and then just run this `_migrate()` task.
    """
    with _host(dest):
        sql = _make_update_sql(env[dest]['db']['name'], env[dest]['home_url'], env[dest]['wp_url'])
        cmd_prefix = ('mysql -u %(user)s -p%(password)s -h %(host)s %(name)s' % env[dest]['db'])

        print('Running MySQL migration commands...')
        for query in sql:
            cmd = cmd_prefix + (' -s -N -e "%s"' % query)
            run(cmd, quiet=QUIET_COMMANDS)


def _fetch(host, fn):
    """
    Fetches a remote database's dump file (src, fn), from the `archives` directory of the specified environment. There
    are no defaults for this task, you MUST provide a server to use, and a filename to download.
    """
    with _host(host):
        print('Fetching database...')
        with quiet():
            return get(fn, env['local']['archive'])


def _make_update_sql(db_name, home_url, wp_url):
    """
    Generates & returns MySQL commands to update WordPress. `site_url` and `home` need to be updated, in the wp_options
    table. However, you could write any SQL you like here, for example a search/replace for the PROD_URL and the LOCAL_URL,
    like if you wanted all attachments/images to be served from your local server, instead of the prod server. Generally
    attachments aren't much of a problem, and I tend to only update the bare minimum to make WordPress run locally.
    """
    sql = [
        ("UPDATE %s.%s_options SET option_value='%s' WHERE option_name='siteurl'" % (db_name, WP_PREFIX, wp_url)),
        ("UPDATE %s.%s_options SET option_value='%s' WHERE option_name='home'" % (db_name, WP_PREFIX, home_url)),
        # Add new commands below:
        #('UPDATE something yadda yadda.....')
    ]
    return sql


def _post_deploy(dest):
    """
    Executes a customized set of post-deployment commands, typically used to set file permissions, remove sensitive
    files, and restart any services (PHP, Varnish, etc.)

    File permissions changed:
    - 755 for the webroot & subdirectories
    - 644 for files inside of the webroot

    Files removed by this task:
    - .gitignore
    - backup/
    - bower.json
    - fabfile/
    - Gruntfile.js
    - package.json
    - puphpet/
    - Vagrantfile

    Services restarted:
    - PHP & Varnish, see the `restart()` task for more info.
    """
    with _host(dest):
        with cd(env[dest]['root']):
            # Clean up some unwanted files
            print('Cleaning up...')
            run(
                'rm -rf .gitignore bower.json package.json Gruntfile.js fabfile/ Vagrantfile puphpet/ backup/',
                quiet=QUIET_COMMANDS)
            run('find . -type d -exec chmod 755 {} \;', quiet=True)
            run('find . -type f -exec chmod 644 {} \;', quiet=True)    
        restart()


def _filter_quiet_commands(cmd):
    """
    Takes a callable of some sort, and depending on the QUIET_COMMANDS config value, it suppresses (or doesn't) the
    output of the command. Typically this is used to suppress the output of the `local()` command from fabric.api,
    which does NOT supprt the quiet=False/True parameter.

    Example usage, showing how to wrap a `local()` command in a lambda, and feed it to this function:

    - _filter_quiet_commands(lambda: local('uname -a'))
    """
    if cmd is None:
        raise ValueError('The `cmd` parameter should be a callable.')
    if QUIET_COMMANDS:
        with quiet():
            cmd()
    else:
        cmd()

def _build_docs():
    """
    This builds out documentation of the tasks for the README.md file. To re-build the docs, just open the python
    interpreter, `import fabfile`, and then run `fabfile._build_docs()`.
    """
    with lcd(os.path.dirname(__file__)):
        print('Building docs....')
        output = local('fab --shortlist', capture=True)
        tasks = output.split('\n')

        task_docs = []
        for t in tasks:
            task_doc = local('fab -d ' + t, capture=True)
            task_doc = task_doc.replace('\n    ', '\n')
            task_doc = re.sub(r'Displaying detailed information for task \'%s\':\n\n' % t, '', task_doc)
            task_docs.append(dict(task=t, doc=task_doc))

        doc_text = ''
        for td in task_docs:
            text = '###`' + td['task'] + '`'
            text += '\n\n'
            text += td['doc']
            text += '\n\n'

            doc_text += text

        with open('README.md','r+') as f:
            readme_text = f.read()
            DELIMITER = '##Information on tasks:\n\n'
            top = readme_text.split(DELIMITER)[0]
            f.seek(0)
            f.truncate()
            f.write(top + DELIMITER + doc_text)


### ----- Context Managers -------- ###
@contextmanager
def _host(src):
    """
    Typically used for wrapping `run()` commands. On entry, it sets the `env.host_string` to the hostname for the
    specified server; on exit, it sets the `env.host_string` to None.

    Example usage:

    - with _host('prod'):
    -     run('uname -a')
    -     run('date')
    """
    try:
        env.host_string = env[src]['hostname']
        yield True
    finally:
        env.host_string = None

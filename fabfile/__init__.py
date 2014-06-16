### --- Fabric/Global Imports --- ###
from __future__ import with_statement
from fabric.api import *
import os
import re

### --- Local Imports --- ###
from fabfile.core.conf import config_loader
config_loader()

if os.environ.get('FAB_CONFIG') is not None:
    import imp
    c = imp.load_source('config', os.environ.get('FAB_CONFIG'))

try:
    from config import LOCAL, DEV, PROD, PROJECT_NAME, WP_PREFIX, UNVERSIONED_FOLDERS, \
    POST_DEPLOY_COMMANDS, APP_RESTART_COMMANDS, SHOW_HEADER, HEADER_FN, QUIET_COMMANDS, \
    DATABASE_MIGRATION_COMMANDS
except ImportError as e:
    raise Exception('There was a problem loading the configuration values: ' + e.message)


### --- Configure the `env` & show/hide the header --- ###
__all__ = ['deploy', 'db_sync', 'file_sync', 'provision', 'upgrade', 'sync', 'dump', 'restart', 'test']

env.use_ssh_config = True

env['local'] = LOCAL
env['dev'] = DEV
env['prod'] = PROD

env.roledefs = {
    'prod': PROD['hosts'],
    'dev': DEV['hosts'],
    'local': LOCAL['hosts']
}

# Show the header
if SHOW_HEADER:
    HEADER_FN()
    

### --------------- Fabric Tasks --------------------- ###
from core import Deploy, DBSync, FileSync, Provision, Upgrade

deploy = Deploy()
db_sync = DBSync()
file_sync = FileSync()
provision = Provision()
upgrade = Upgrade()

@task
def sync(src='prod', dest='local'):
    """
    Synchronizes the database and un-versioned files from one environment to another. (src: prod, dest: local)

    Typically this task is used to update the local environment so that it matches the production server. For more
    information on either the datbase synchronization procedure, or the way it synchronizes the files, see the
    `DBSync` and `FileSync` tasks (under `core/`). Note that this task DOES NOT copy/transfer any application code, that must be
    done instead using the "deploy" task.

    Example usage:

    - `fab sync              # Updates local site with latest database & files from the prod site`
    - `fab sync:local,dev    # NOT RECOMMENDED - have not developed/tested this functionality.`
    - `fab sync:local,prod   # NOT RECOMMENDED - have not developed/tested this functionality.`
    """
    execute(db_sync.run, src, dest)
    execute(file_sync.run, src, dest)


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
    if fetch_dump is True:
        result = execute(db_sync.dump_fetch, src)
        print('Database dump has been downloaded to %s.' % result.popitem()[1])
    else:
        result = execute(db_sync.dump, src)
        print('Database has been dumped to to %s:%s.' % (src, result.popitem()[1][1]))


@task
def restart(dest='prod'):
    """
    Executes any commands defined in the APP_RESTART_COMMANDS config value.
    """
    execute(deploy.restart, role=dest)


@task
def test(dest='prod'):
    """
    Tests connection to a specified host. (dest: prod)

    Example usage:

    - `test:dev`
    - `test:prod`
    """
    @roles('prod')
    def run_test():
        env.host_string = env[dest]['hosts'][0]
        run('uname -a')

    execute(run_test, role=dest)


### ----- Private Functions -------- ###
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
            task_doc = task_doc.replace('Arguments: self,', 'Arguments:')
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
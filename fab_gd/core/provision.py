"""
This file contains the provision task. WARNING - this task has had little-to-zero testing/development.

USE AT YOUR OWN RISK.
"""

# Fabric/Global Imports
from fabric.api import env, run, local, cd, execute, parallel, roles, hosts, lcd
from fabric.contrib.console import confirm
from fabric.tasks import Task


class Provision(Task):
    """
    NOT RECOMMENDED - Provisions web root & archive folders, as well as git repo.
    """
    name = "provision"
    cmd_data = dict(branch=None, dest=None, dest_branch=None)

    def __init__(self, *args, **kwargs):
        super(Provision, self).__init__(*args, **kwargs)


    def run(self, dest=None, *args, **kwargs):
        """
        NOT RECOMMENDED - Provisions web root & archive folders, as well as git repo.

        This task has not been hard-tested, and since it rarely needs to be done, there hasn't been much effort put into
        scripting this aspect of things, especially considering all of the error-handling that would need to go on with this.

        Instead, consider it a rough guide of things to do, in order to set up a new location for deployment.
        """
        if True: #confirm('This will provision the %s environment. Continue?'):
            execute(self.provision, dest, role=dest)


    @roles('prod')
    def provision(self, dest):
        for dir_name in ['archive', 'root', 'repo']:
            try:
                run('mkdir -p %s' % env[dest][dir_name])
            except Exception as e:
                raise Exception('Could not make the `%s` folder: %s' % (dir_name, e.message))

        with cd(env[dest]['repo']):
            try:
                run('git init --bare')
            except Exception as e:
                raise Exception('Could not initialize the git repo: %s' % e.message)

            with lcd(env['local']['root']):
                try:
                    local('git remote add %s %s:%s' % (dest, env.host_string, env[dest]['repo']))
                    local('git push %s --all' % dest)
                except:
                    raise Exception('Problems configuring local git remote and/or pushing it to the destination.')

        with cd(env[dest]['root']):
            try:
                run('git init')
                run('git remote add origin %s' % env[dest]['repo'])
                run('git pull origin master')
            except:
                raise Exception('Problems configuring destination web root.')

"""
This file contains the deploy task.
"""
# Fabric/Global Imports
from fabric.api import env, run, local, cd, lcd, quiet, execute, parallel, roles
from fabric.tasks import Task
from fabfile.core.common import filter_quiet_commands


class Deploy(Task):
    """
    Deploys your local code to a remote server. (dest: prod, branch: master, dest_branch: master)
    """
    name = "deploy"
    cmd_data = dict(branch=None, dest=None, dest_branch=None)
    
    def __init__(self, *args, **kwargs):
        super(Deploy, self).__init__(*args, **kwargs)

        
    def run(self, dest='prod', branch='master', dest_branch='master', *args, **kwargs):
        """
        Deploys your local code to a remote server. (dest: prod, branch: master, dest_branch: master)

        This task pushes your local git repo to the destination server, then updates the destination's webroot via
        `git pull`. Then it executes any post-deployment tasks, like setting file permissions, as well as deleting any
        sensitive files from the webroot (.git files, Gruntfile, Vagrant configs, etc. See the `_post_deploy()` function
        for more info), restarting PHP (to flush the opcode cache), and flushing the Varnish cache.

        Example usage:

        - `fab deploy        # Most common, this pushes latest local updates to the production server.`
        - `fab deploy:prod   # Same as above, as "prod" is the default destination.`
        - `fab deploy:dev    # Deploys code to the dev server`
        """
        self.cmd_data = dict(branch=branch, dest=dest, dest_branch=dest_branch)
        
        execute(self.push_app)
        execute(self.update_remote, role=dest)
        
        if len(env.conf.post_deploy_commands):
            execute(self.post_deploy, role=dest)
            
        if len(env.conf.app_restart_commands):
            execute(self.restart, role=dest)
        
        
    @roles('local')
    def push_app(self):
        """
        Git-pushes the local repository to the destination (needs to correspond to a git remote)
        """
        with lcd(env.local['root']):
            print('Pushing %(branch)s branch to %(dest)s:%(dest_branch)s...' % self.cmd_data)
            cmd = lambda: local('git push %(dest)s %(branch)s:%(dest_branch)s' % self.cmd_data)
            filter_quiet_commands(cmd)
    
    
    @parallel
    @roles('prod')
    def update_remote(self):
        """ 
        Updates the remote server's application code, via git pull.
        """
        dest = self.cmd_data['dest']
        with cd(env[dest]['root']):
            # note the dependency on the remote name "origin"
            print('Updating destination from %(dest)s:%(dest_branch)s...' % self.cmd_data)
            run('git reset --hard && git pull origin %(dest_branch)s' % self.cmd_data, quiet=env.conf.quiet_commands)
        pass
    
    
    @parallel
    @roles('prod')
    def post_deploy(self):
        """
        Executes the commands defined in env.conf.post_deploy_commands, from the config.py 
        file. Typically this would be a good place to set file permissions, file  
        cleanup, etc.
        """
        dest = self.cmd_data['dest']
        with cd(env[dest]['root']):
            for cmd in env.conf.post_deploy_commands:
                run(cmd % env[dest], quiet=env.conf.quiet_commands)                


    @parallel
    @roles('prod')
    def restart(self):
        """
        Executes any commands defined in the env.conf.app_restart_commands config value.
        """
        print('Restarting application...')
        for cmd in env.conf.app_restart_commands:
            run(cmd, quiet=env.conf.quiet_commands)
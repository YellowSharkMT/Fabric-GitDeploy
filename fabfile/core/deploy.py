"""
This file contains the deploy task.
"""
# Fabric/Global Imports
from fabric.api import env, run, local, cd, lcd, quiet, execute, parallel
from fabric.tasks import Task

# Local Imports
from .common import filter_quiet_commands
from ..config import QUIET_COMMANDS, APP_RESTART_COMMANDS, POST_DEPLOY_COMMANDS


class Deploy(Task):
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
    name = "deploy"
    cmd_data = dict(branch=None, dest=None, dest_branch=None)
    
    def __init__(self, *args, **kwargs):
        pass
        
        
    def run(self, dest='prod', branch='master', dest_branch='master', *args, **kwargs):
        """
        Executes the various parts of the deployment scheme: pushing the code, updating the remote code,
        executing post-deployment commands, and finally the app-restart commands.
        """
        self.cmd_data = dict(branch=branch, dest=dest, dest_branch=dest_branch)
        
        execute(self.push_app)
        execute(self.update_remote, role=dest)
        
        if len(POST_DEPLOY_COMMANDS):
            execute(self.post_deploy, role=dest)
            
        if len(APP_RESTART_COMMANDS):
            execute(self.restart, role=dest)
        
        
    def push_app(self):
        """
        Git-pushes the local repository to the destination (which should correspond to a git remote
        """
        with lcd(env.local['root']):
            print('Pushing %(branch)s branch to %(dest)s:%(dest_branch)s...' % self.cmd_data)
            cmd = lambda: local('git push %(dest)s %(branch)s:%(dest_branch)s' % self.cmd_data)
            filter_quiet_commands(cmd)
    
    
    @parallel
    def update_remote(self):
        """ 
        Updates the remote server's application code, via git pull.
        """
        dest = self.cmd_data['dest']
        with cd(env[dest]['root']):
            # note the dependency on the remote name "origin"
            print('Updating destination from %(dest)s:%(dest_branch)s...' % self.cmd_data)
            run('git reset --hard && git pull origin %(dest_branch)s' % self.cmd_data, quiet=QUIET_COMMANDS)
        pass
    
    
    @parallel
    def post_deploy(self):
        """
        Executes the commands defined in POST_DEPLOY_COMMANDS, from the config.py 
        file. Typically this would be a good place to set file permissions, file  
        cleanup, etc.
        """
        dest = self.cmd_data['dest']
        with cd(env[dest]['root']):
            for cmd in POST_DEPLOY_COMMANDS:
                run(cmd % env[dest], quiet=QUIET_COMMANDS)                

                
    @parallel
    def restart(self):
        """
        Executes any commands defined in the APP_RESTART_COMMANDS config value.
        """
        print('Restarting application...')
        for cmd in APP_RESTART_COMMANDS:
            run(cmd, quiet=QUIET_COMMANDS)



"""
This file contains the file synchronization task.
"""
# Fabric/Global Imports
from fabric.api import env, run, local, cd, lcd, quiet, execute, parallel
from fabric.tasks import Task

# Local Imports
from .common import filter_quiet_commands
from ..config import UNVERSIONED_FOLDERS


class FileSync(Task):
    """
        Synchronizes the unversioned folders from one environment to another. (src: prod, dest: local)
    """
    name = 'rsync'
    cmd_data = dict()
    
    def __init__(self,*args, **kwargs):
        super(FileSync, self).__init__(*args, **kwargs)
        pass
        
    def run(self, src='prod', dest='local', *args, **kwargs):
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


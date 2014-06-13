from fabric.api import local
from fabric.contrib.console import confirm
from fabric.tasks import Task


class Upgrade(Task):
    name = 'upgrade'
    """
    Executes upgrade procedure: downloads tarball of master into a local temp folder,
    then copies the contents of the new `fabfile/` folder into the local `fabfile/` folder,
    and then cleans up/removes the upgrade package.
    """

    def __init__(self, *args, **kwargs):
        super(Upgrade, self).__init__(*args, **kwargs)


    def run(self):
        if confirm('This will upgrade the Fabric-GitDeploy package. Continue?'):
            local('mkdir ./fabric-upgrade')
            local('curl -L https://github.com/YellowSharkMT/Fabric-GitDeploy/tarball/master' +
                  '| tar -xz --strip-components=1 -C fabric-upgrade/')
            local('cp -r ./fabric-upgrade/fabfile/* ./fabfile/.')
            local('rm -rf ./fabric-upgrade/')

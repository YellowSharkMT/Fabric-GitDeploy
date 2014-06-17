"""
PROJECT_NAME is used in certain file-naming schemes
"""
PROJECT_NAME = 'my_project'


"""
Define the LOCAL, DEV, and PROD environments here.
"""
LOCAL = {
    'hostname': 'user@server',  # Can use hosts defined in SSH config here
    'hosts': ['user@server1', 'user@server2'],
    'home_url': 'http://local.website.com/',
    'wp_url': 'http://local.website.com/',
    'archive': '/www/_archive/%s' % PROJECT_NAME,
    'root': '/www/%s' % PROJECT_NAME,
    'db': {
        'user': 'DB_USER',
        'password': 'DB_PASS',
        'name': 'DB_NAME',
        'host': 'DB_HOST_NAME',
    }
}

DEV = {
    'hostname': 'user@server',  # Can use hosts defined in SSH config here
    'hosts': ['user@server1', 'user@server2'],
    'home_url': 'http://dev.website.com/',
    'wp_url': 'http://dev.website.com/',
    'archive': '~/webapps/PROJECT_NAME/archives',
    'root': '~/webapps/PROJECT_NAME/dev',
    'db': {
        'user': 'DB_USER',
        'password': 'DB_PASS',
        'name': 'DB_NAME',
        'host': 'DB_HOST_NAME',
    },
    # The `repo` property is optional, it is only used by the provision task, which 
    # currently is not tested enough for production use.
    'repo': '~/webapps/PROJECT_NAME/PROJECT_NAME.git',
}

PROD = {
    'hostname': 'user@server',  # Can use hosts defined in SSH config here
    'hosts': ['user@server1', 'user@server2'],
    'home_url': 'http://www.website.com/',
    'wp_url': 'http://www.website.com/',
    'archive': '~/_archive/ysmt',
    'root': '~/webapps/ysmt/public',
    'db': {
        'user': 'DB_USER',
        'password': 'DB_PASS',
        'name': 'DB_NAME',
        'host': 'DB_HOST_NAME',
    },
    # The `repo` property is optional, it is only used by the provision task, which 
    # currently is not tested enough for production use.
    'repo': '~/webapps/PROJECT_NAME/PROJECT_NAME.git',
}


"""
Table prefix for the WordPress database.
"""
WP_PREFIX = 'wp'


"""
Contents of these folders will be downloaded to this machine. Typically you would include at the 
least the uploads directory.
"""
UNVERSIONED_FOLDERS = ['wp-content/uploads']


"""
These commands will be interpolated with the environment data provided above, 
and are executed from the webroot. Example commands that can be executed:
"find %(root)s -type d -exec chmod 755 {} \;" (this already happens)
Note that the `db` dictionary data is NOT available yet, that's a TODO item.
"""
POST_DEPLOY_COMMANDS = [
    'rm -rf .gitignore bower.json package.json Gruntfile.js fabfile/ Vagrantfile puphpet/ backup/',
    'find . -type d -exec chmod 755 {} \;',
    'find . -type f -exec chmod 644 {} \;',
]


"""
These commands will be interpolated with the environment data provided above,
and are not executed from a particular location, so be sure to use absolute paths.
"""
APP_RESTART_COMMANDS = [
    # '/home/PROJECT_NAME/bin/supervisorctl restart php-fpm: varnish:',
]


"""
These commands will be interpolated with the variables listed below, and will be executed on
the destination server, via bash, after the database has been inserted.
- db_name
- db_prefix
- wp_url
- home_url
"""
DATABASE_MIGRATION_COMMANDS = [
    "UPDATE %(db_name)s.%(db_prefix)s_options SET option_value='%(wp_url)s' WHERE option_name='siteurl'",
    "UPDATE %(db_name)s.%(db_prefix)s_options SET option_value='%(home_url)s' WHERE option_name='home'",
]


"""
This controls whether the header is shown or not
"""
SHOW_HEADER = False


"""
This is the header, and will only be shown in the SHOW_HEADER value is set to True
"""
HEADER = [
    '** Fabfile for WEBSITE.com, contact YOUR NAVE <YOUREMAIL@EMAIL.COM> with questions.',
    '** Use `fab -l` to list all tasks.',
    '** Use `fab -d TASKNAME` to show documentation & usage examples for a task.',
    '** Ex. usage: `fab deploy:dev sync:prod,dev`',
    '** For more information on Fabric, visit http://fabfile.org.',
    '',
]

"""
Controls output of the `run()` commands. For verbose output, set this to `False`.
"""
QUIET_COMMANDS = True

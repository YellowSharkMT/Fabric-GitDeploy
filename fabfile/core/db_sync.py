"""
This file contains the database synchronization task.
"""
# Fabric/Global Imports
from fabric.api import env, run, quiet, execute, hosts, get
from fabric.tasks import Task
import time


class DBSync(Task):
    """
    Copies the database from one server to another, essentially an export/import. (src: prod, dest: local)
    """
    name = 'db'
    cmd_data = dict()

    def __init__(self, *args, **kwargs):
        super(DBSync, self).__init__(*args, **kwargs)


    def setup_default_hosts(self):
        default_prod_host = env['prod']['hosts'][0]
        default_local_host = env['local']['hosts'][0]

        self.insert_db = hosts(self.insert_db, default_local_host)
        self.dump_fetch = hosts(self.dump_fetch, default_prod_host)
        self.dump_fetch = hosts(self.dump_fetch, default_prod_host)
        self.fetch = hosts(self.fetch, default_prod_host)
        self.dump = hosts(self.dump, default_prod_host)
        self.migrate = hosts(self.migrate, default_local_host)
        pass


    def run(self, src='prod', dest='local', *args, **kwargs):
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
            raise ValueError('Using the local database as a source is not currently supported.')

        if dest == 'local':
            dump_result = execute(self.dump_fetch, src, hosts=env[src]['hosts'][0])
        else:
            dump_result = execute(self.dump, src, hosts=env[src]['hosts'][0])

        insert_dump_fn = dump_result.popitem()[1][0]
        execute(self.insert_db, dest, insert_dump_fn, hosts=env[dest]['hosts'][0])
        execute(self.migrate, dest, hosts=env[dest]['hosts'][0])


    @hosts([])  # default = local
    def insert_db(self, dest, insert_dump_fn):
        """
        Creates & executes the insert commands
        :param dest: refers to the environment: local, prod, dev, etc.
        :param insert_dump_fn: filename to insert (expecting a .sql.gz file)
        :return:
        """
        insert_cmd = 'mysql -u %(user)s -p%(password)s -h %(host)s %(name)s' % env[dest]['db']
        cmd = 'gunzip < %s | %s' % (insert_dump_fn, insert_cmd)
        print('Inserting database....')
        run(cmd, quiet=env.conf.quiet_commands)


    @hosts([])  # prod
    def dump_fetch(self, src):
        dump_result = execute(self.dump, src, hosts=env[src]['hosts'][0])
        _, dump_full_fn = dump_result.popitem()[1]
        fetch_result = execute(self.fetch, dump_full_fn, hosts=env[src]['hosts'][0])
        return fetch_result.popitem()[1]


    @hosts([])  # # prod
    def fetch(self, fn):
        """
        Fetches a remote database's dump file (src, fn). The default host for this command is `prod`.
        To override that, set the `role` kwarg and call this via the execute function, like so:
        
        - `execute(self.fetch, fn, role='FILL_THIS_IN')`
        :param fn: path to the dump filename on the remote server
        """
        print('Fetching database...')
        with quiet():
            return get(fn, env['local']['archive'])


    @hosts([])  # prod
    def dump(self, src='prod'):
        """
        Dumps a database, then downloads it to `backup/` folder. Useful for performing back-ups. (src: prod, fetch_dump: True)

        Example usage:

        - `fab dump            # dumps the prod database, downloads it to the local `backup/` folder.`
        - `fab dump:prod,True  # same as above, these are the task defaults.`
        - `fab dump:dev,False  # dumps the dev environment's database, but does NOT download it, this just leaves it on the remote server.`

        Note that there is no "cleanup" command or anything that deletes these dump files from the remote server, so if you
        have space constraints, you'll need to manually go in and purge the `archives` directory (which is defined at the
        top of this file).
        :param src: source server (local, prod, dev)
        """
        cmd_vars = env[src]['db']
        dump_cmd = 'mysqldump -u %(user)s -p%(password)s -h %(host)s %(name)s' % cmd_vars
        dump_fn_stem = '%s-%s.%s' % (env.conf.project_name, time.strftime("%Y.%m.%d-%H.%M.%S"), src)
        dump_fn = '%s.sql.gz' % dump_fn_stem
        dump_full_fn = '%s/%s' % (env[src]['archive'], dump_fn)
        cmd = '%s | gzip > %s' % (dump_cmd, dump_full_fn)
        print('Dumping database...')
        run(cmd, quiet=env.conf.quiet_commands)

        return dump_fn, dump_full_fn


    @hosts([])  # local
    def migrate(self, dest='local'):
        """
        Updates WordPress database so it works on a different server (dest: local).
        Typically this task is executed immediately after inserting newer contents into a database, like as part of the
        "sync" task. It updates a couple options in WordPress to make the site run on a different hostname. See the
        `_make_update_sql()` function for more detailed information on the database commands that are executed.

        It is strongly advised that you DO NOT RUN THIS ON A PRODUCTION DATABASE. (but you could...) The normal use-case
        for this command, aside from the scenario described above, were if you were developing something that required
        you to constantly reset the database with a specific file. Rather than running the `sync()` task, you might want to
        just insert a file that's already been downloaded by a previous sync, and then just run this `_migrate()` task.
        :param dest: destination server (local, prod, dev)
        """
        sql = self.make_update_sql(env[dest]['db']['name'], home_url=env[dest]['home_url'], wp_url=env[dest]['wp_url'])
        cmd_prefix = ('mysql -u %(user)s -p%(password)s -h %(host)s %(name)s' % env[dest]['db'])

        print('Running MySQL migration commands...')
        for query in sql:
            cmd = cmd_prefix + (' -s -N -e "%s"' % query)
            run(cmd, quiet=env.conf.quiet_commands)


    def make_update_sql(self, db_name, *args, **kwargs):
        """
        Generates & returns MySQL commands to migrate the database. Typically this involves things like updating hostnames, 
        and/or URLs, or any other sort of site-specific options that might be stored in the database. For example, to shift 
        a WordPress database from one hostname to another, you must update the `site_url` and `home` values in the `wp_options`
        table.
        :param db_name: database name
        :param kwargs: any kwargs will get interpolated into the SQL command string that is generated
        """
        cmd_data = dict(db_name=db_name, db_prefix=env.conf.wp_prefix, **kwargs)
        sql = [(cmd % cmd_data) for cmd in env.conf.database_migration_commands]
        return sql
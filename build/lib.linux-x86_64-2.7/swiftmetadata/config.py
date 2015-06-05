from ConfigParser import ConfigParser
from ConfigParser import NoOptionError, NoSectionError


def get_config_options():
    config = ConfigParser()
    config.read('/etc/swift/swift.conf')
    options = {}

    if 'metadata database' in config._sections:
        options['db_host'] = config.get('metadata database', 'db_host', None)
        options['db_port'] = int(config.get('metadata database', 'db_port', None))
        options['db_name'] = config.get('metadata database', 'db_name', None)
        options['col_name'] = config.get('metadata database', 'col_name', None)

    if 'swift defaults' in config._sections:
        options['default_owner'] = config.get('swift defaults', 'default_owner', None)
	options['container_name'] = config.get('swift defaults', 'container_name', None)

    return options

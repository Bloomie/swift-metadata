from swiftclient.client import Connection

from swiftmetadata.config import get_config_options
from swiftmetadata.middleware import get_id

from pymongo import MongoClient


class Client(Connection):
    '''
    Client takes argmuents for base swiftclient.client.Connection.
    Adds methods for searching metadata and delete method handling owner field
    '''
    def __init__(self, **kwargs):
	
	super(Client, self).__init__(**kwargs)
	
	self.options = get_config_options()

        client = MongoClient(self.options['db_host'], self.options['db_port'])
        self.db = client[self.options['db_name']]

    def get_objects_by_metadata(self, metadata):
	
	found_metadata = self.db[self.options['col_name']].find(metadata)
	object_ids = [x['_id'] for x in found_metadata]
	print object_ids
	found_metadata.rewind()

	return zip([self.get_object(self.options['container_name'], obj_id) for obj_id in object_ids], [x for x in found_metadata])	

    def get_objects_by_keys(self, keys, existense_flag=True):
	
	existense_dict = {k: {'$exists': existense_flag} for k in keys}
	found_metadata = self.db[self.options['col_name']].find(existense_dict)
	object_ids = [x['_id'] for x in found_metadata]
	found_metadata.rewind()

	return zip([self.get_object(self.options['container_name'], obj_id) for obj_id in object_ids], [x for x in found_metadata])	

    '''Handles object name depending on owner field'''
    def delete_object(self, container, obj, owner=None, **kwargs):
	if owner:
	    obj = get_id(obj, owner)

	super(Client, self).delete_object(container, obj, **kwargs)
	    
		


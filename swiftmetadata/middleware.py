from swift.common import wsgi
from swift.common.swob import wsgify, Response
from swift.common.utils import split_path

from pymongo import MongoClient
from hashlib import md5

from swiftmetadata.config import get_config_options

def get_id(objname, owner):
'''computes id from object name and owner'''
    return md5(objname + owner).hexdigest()


class SummitMiddleware(object):
    '''Middleware callable object'''
    def __init__(self, app, *args, **kwargs):
        self.app = app
        self.suffix = kwargs.get('suffix', '')

    	self.options = get_config_options()

    @wsgify
    def __call__(self, request):
        try:
            (version, account, container, objname) = split_path(request.path_info, 4, 4, True)
        except ValueError:
            return self.app
       
	'''Does nothing if owner is not specified'''
	if 'Metafield-Owner' not in request.headers and request.method == 'GET':
	    return self.app
 
	metadata = {k: request.headers[k] for k in request.headers.keys() if k.startswith('Metafield-')}
        owner = metadata.get('Metafield-Owner', self.options['default_owner'])
	filename = objname
	'''Swiftclient's delete_object method has no headers, so we assume objname is swift object's id'''
	if not request.method == 'DELETE':
	    objname = get_id(objname, owner) 

	request.path_info = '/%s/%s/%s/%s' % (version, account, container, objname)

	if request.method == 'GET':
	    return self.app

	metadata['_id'] = objname
	metadata['objname'] = filename

	client = MongoClient(self.options['db_host'], self.options['db_port'])
        db = client[self.options['db_name']]

        if request.method == 'PUT':
            db[self.options['col_name']].insert_one(metadata)

        elif request.method == 'POST':
	    '''Forms new metadata from union'''
            doc = db[self.options['col_name']].find({'_id': objname})[0]
            updated_doc = dict(doc.items() + metadata.items())
            db[self.options['col_name']].update(doc, updated_doc)

        elif request.method == 'DELETE':
            db[self.options['col_name']].remove({'_id': objname})
	
        return self.app


def filter_factory(global_config, **local_config):

    suffix = local_config.get('suffix')

    def factory(app):
        return SummitMiddleware(app, suffix=suffix)

    return factory



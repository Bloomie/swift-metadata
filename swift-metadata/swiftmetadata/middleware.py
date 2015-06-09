from swift.common import wsgi
from swift.common.utils import split_path

from webob import Response

from pymongo import MongoClient
from hashlib import md5

from swift.common.swob import Request, HTTPBadRequest
from swiftmetadata.config import get_config_options

def compute_id(objname, owner):
    '''Computes id from object name and owner'''
    return md5(objname + owner).hexdigest()


class SummitMiddleware(object):
    '''Middleware callable object'''
    def __init__(self, app, *args, **kwargs):
        self.app = app
        self.suffix = kwargs.get('suffix', '')

    	self.options = get_config_options()

    def __call__(self, env, start_response):
        try:
            (version, account, container, objname) = split_path(env['PATH_INFO'], 3, 4, True)

            client = MongoClient(self.options['db_host'], self.options['db_port'])
            db = client[self.options['db_name']]
        except ValueError:
            return self.app(env, start_response)
        
        metadata = {k: env[k] for k in env.keys() if k.startswith('HTTP_METAFIELD_')}
        
        #entering when get_container with SEARCH flag is called
        if not objname and env['REQUEST_METHOD'] == 'GET' and 'HTTP_SEARCH' in env: 
            objects = None

            #searching by metadata
            if env['HTTP_SEARCH'] == 'META':
                objects = [{k: str(x[k]) for k in x.keys()} for x in db[container].find(metadata)]

            #searching by key: True/False    
            elif env['HTTP_SEARCH'] == 'KEYS':
                meta_dict = {k: {'$exists': metadata[k]} for k in metadata}
                objects = [{k: str(x[k]) for k in x.keys()} for x in db[container].find(metadata)]

            return Response(json_body=objects)(env, start_response) 

        elif not objname:
            return self.app(env, start_response)

	filename = objname
        metadata['HTTP_METAFIELD_OWNER'] = metadata.get('HTTP_METAFIELD_OWNER', None) or env['HTTP_X_USER_NAME'] 
        objname = compute_id(objname, metadata.get('HTTP_METAFIELD_OWNER'))
	env['PATH_INFO'] = '/%s/%s/%s/%s' % (version, account, container, objname)

	metadata['docId'] = objname
	metadata['objname'] = filename

        if env['REQUEST_METHOD'] == 'PUT':
            #put object depends on version
            try:
                cur_doc = db[container].find({'docId': objname})[0]
                metadata['v'] = cur_doc['v'] + 1
                db['version-'+container].insert_one(cur_doc)
                db[container].insert_one(metadata)
                db[container].remove(cur_doc)
            except:
                metadata['v'] = 1
                db[container].insert_one(metadata)
            
        elif env['REQUEST_METHOD'] == 'POST':
	    '''Forms new metadata from union'''
            doc = db[container].find({'docId': objname})[0]
            updated_doc = dict(doc.items() + metadata.items())
            db[container].update(doc, updated_doc)

        elif env['REQUEST_METHOD'] == 'DELETE':
            #delete object depends on version
            try:
                doc = db['version-'+container].find({'docId': objname}).sort([('v', -1)]).limit(-1)[0]
                db[container].remove({'docId': objname})
                db['version-'+container].remove(doc)
                db[container].insert_one(doc)
            except:
                db[container].remove({'docId': objname})

	resp = Request(env).get_response(self.app)

        #revert changes if swift put fails
	if resp.status[0] != '2' and env['REQUEST_METHOD'] == 'PUT':
	    try:
		db[container].remove(metadata)
		db[container].insert_one(cur_doc)
		db['version-'+container].remove(cur_doc)
	    except:
		db[container].remove(metadata)
        return self.app(env, start_response)


def filter_factory(global_config, **local_config):

    suffix = local_config.get('suffix')

    def factory(app):
        return SummitMiddleware(app, suffix=suffix)

    return factory


import json
import logging
from wsgiref import simple_server 
import falcon
import sys
sys.path.append('/home/bluebricks/workspace/Somil/NLPEngine')
import LyntenNlpEngine

def token_is_valid(token, user_id):
    return True  # for now

def auth(req, resp, params):
    # Alternatively, do this in middleware
    token = req.get_header('X-Auth-Token')

    if token is None:
        raise falcon.HTTPUnauthorized('Auth token required',
                                      'Please provide an auth token '
                                      'as part of the request',
                                      'http://docs.example.com/auth')

    if not token_is_valid(token, params['user_id']):
        raise falcon.HTTPUnauthorized('Authentication required',
                                      'The provided auth token is '
                                      'not valid. Please request a '
                                      'new token and try again.',
                                      'http://docs.example.com/auth')


def check_media_type(req, resp, params):
    if not req.client_accepts_json:
        raise falcon.HTTPUnsupportedMediaType(
            'Media Type not Supported',
            'This API only supports the JSON media type.',
            'http://docs.examples.com/api/json')


class ContentResurfacing:

    def __init__(self):
        self.logger = logging.getLogger('contentresurfaceresource.' + __name__)
        self.nlpengine = LyntenNlpEngine.LyntenNlpEngine()

    def on_get(self, req, resp):
        results = {"desc" : "NLP Service"}

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(results)

    def on_post(self, req, resp):
        try:
            raw_json = req.stream.read()
        except Exception:
            raise falcon.HTTPError(falcon.HTTP_748,
                                   'Read Error',
                                   'Could not read the request body. Must be '
                                   'them ponies again.')

        try:
            inputdata = json.loads(raw_json, 'utf-8')
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect.')
        wcontent = 'NLP Service'
        if 'wcontent' in inputdata:
            wcontent = inputdata['wcontent']

        results = {}
        try:
            results = self.nlpengine.discovery(wcontent)
        except Exception as ex:
            self.logger.error(ex)
            description = ('NLP Failed')
            raise falcon.HTTPServiceUnavailable('Service Outage',description,30)

        resp.status = falcon.HTTP_201
        finalresult = { 'status': 'OK', 'decs': 'DISCOVERY SUCCEEDED' , 'result': results}
        resp.body =  json.dumps(finalresult)


#wsgi_app = api = falcon.API(before=[auth, check_media_type])
wsgi_app = api = falcon.API()
ess = ContentResurfacing()

api.add_route('/nlpfunc', ess) 
app = application = api

# Useful for debugging problems in your API; works with pdb.set_trace()
if __name__ == '__main__':
    httpd = simple_server.make_server('0.0.0.0', 8001, app)
    httpd.serve_forever()
#
# gunicorn ElasticWebServices:app --debug --log-level info --access-logfile ./gunicorn-access.log --error-logfile ./gunicorn-error.log
#
#

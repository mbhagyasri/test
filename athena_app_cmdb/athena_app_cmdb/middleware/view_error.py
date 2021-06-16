# Middleware to catch any sort of error from our views,
# and output it as either HTML or JSON appropriately

from django.template.loader import render_to_string
from django.core.serializers.json import DjangoJSONEncoder
from django import http
from django.db import connection
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ViewException(Exception):
    pass


class GEOS_JSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        try:
            return o.json  # Will therefore support all the GEOS objects
        except:
            pass
        return super(GEOS_JSONEncoder, self).default(o)


def output_json(out, code=200):
    if code != 200:
        out['code'] = code
    indent = None
    if settings.DEBUG:
        if isinstance(out, dict):
            out['debug_db_queries'] = connection.queries
        indent = 4

    json_dumps_params = {'ensure_ascii': False, 'indent': indent}

    if type(out) is dict:
        response = http.JsonResponse(
            out,
            status=code,
            encoder=GEOS_JSONEncoder,
            json_dumps_params=json_dumps_params)
    else:
        encoder = GEOS_JSONEncoder(**json_dumps_params)
        content = encoder.iterencode(out)

        response = http.StreamingHttpResponse(
            streaming_content=content,
            content_type='application/json',
            status=code)

    response['Cache-Control'] = 'max-age=2419200'  # 4 weeks
    response['Access-Control-Allow-Origin'] = '*'

    return response


class ViewExceptionMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response


    def process_exception(self, request, exception):
        if not isinstance(exception, ViewException):
            return None
        format, message, code = exception.args
        if format == 'html':
            types = {
                400: http.HttpResponseBadRequest,
                404: http.HttpResponseNotFound,
                500: http.HttpResponseServerError,
            }
            response_type = types.get(code, http.HttpResponse)
            return response_type(render_to_string(
                '/%s.html' % code,
                {'error': message},
                request=request
            ))
        return output_json({'error': message}, code=code)


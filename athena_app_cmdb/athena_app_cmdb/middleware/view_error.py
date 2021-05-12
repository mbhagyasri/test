# Middleware to catch any sort of error from our views,
# and output it as either HTML or JSON appropriately

from django import http
from django.template.loader import render_to_string
from athena_app_cmdb.utils.helper_methods import output_json
import logging
logger = logging.getLogger(__name__)

class ViewException(Exception):
    pass


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
        logger.info('HERE {}'.format(format))
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


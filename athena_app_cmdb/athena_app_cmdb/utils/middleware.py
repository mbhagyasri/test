# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global LLC
# Copying or reproduction without prior written approval is prohibited. 
# Copyright (c) 2021 =================================================

import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)


def is_registered(exception):
    try:
        return exception.is_an_error_response
    except AttributeError:
        return False


class ExceptionHandler(object):
    """
    Middleware that handles messages. 
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        """
        Catch all subclasses of Exception
        """
        if ('CONTENT_TYPE' in request.META and 'APPLICATION/JSON' in request.META.get('CONTENT_TYPE','').upper()) \
                or 'api' in request.get_full_path():
            if is_registered(exception):
                status = exception.status_code
                exception_dict = exception.to_dict()
            else:
                status = 500
                exception_dict = {'errorMessage': 'Unexpected Error! {}. '
                                                  'Check {}.log for details.'.format(str(exception), PROCESSOR)}
                logger.exception(exception)
            return JsonResponse(exception_dict, status=status)
        return

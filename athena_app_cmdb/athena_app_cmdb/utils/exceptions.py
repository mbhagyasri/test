# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global LLC
# Copying or reproduction without prior written approval is prohibited.
# Copyright (c) 2019 =================================================
import logging

logger = logging.getLogger(__name__)


class AppRegistryException(Exception):

    status_code = None
    error_message = None
    is_an_error_response = True

    def __init__(self, error_message=None):
        Exception.__init__(self)
        self.error_message = error_message

    def to_dict(self):
        return {'errorMessage': self.error_message}


class InvalidRequest(AppRegistryException):
    status_code = 400


class Unauthorized(AppRegistryException):
    status_code = 401


class Forbidden(AppRegistryException):
    status_code = 403


class InvalidPath(AppRegistryException):
    status_code = 404


class NotAcceptable(AppRegistryException):
    status_code = 406


class RateLimitExceeded(AppRegistryException):
    status_code = 429


class InternalServerError(AppRegistryException):
    status_code = 500


class VaultNotInitialized(AppRegistryException):
    status_code = 400


class VaultDown(AppRegistryException):
    status_code = 503


class ServerDown(AppRegistryException):
    status_code = 503


class UnexpectedError(AppRegistryException):
    status_code = 500


class ParamValidationError(AppRegistryException):
    status_code = 400

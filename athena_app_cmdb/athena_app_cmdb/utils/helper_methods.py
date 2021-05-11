# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global LLC
# Copying or reproduction without prior written approval is prohibited. 
# Copyright (c) 2019 =================================================
import socket
from uuid import UUID
import json
import logging
from . import exceptions
from libs.utility.config_parsers import get_config
from django.utils.module_loading import import_string

logger = logging.getLogger(__name__)
config = get_config()


def raise_for_error(status_code, message=None):
    """Helper method to raise exceptions based on the status code of a response received back from Vault.
    :param status_code: Status code received in a response from Vault.
    :type status_code: int
    :param message: Optional message to include in a resulting exception.
    :type message: dict | str
    :param errors: Optional errors to include in a resulting exception.
    :type errors: list | str
    """

    if status_code == 400:
        raise exceptions.InvalidRequest(message)
    elif status_code == 401:
        raise exceptions.Unauthorized(message)
    elif status_code == 403:
        raise exceptions.Forbidden(message)
    elif status_code == 404:
        raise exceptions.InvalidPath(message)
    elif status_code == 406:
        raise exceptions.NotAcceptable(message)
    elif status_code == 429:
        raise exceptions.RateLimitExceeded( message)
    elif status_code == 500:
        raise exceptions.InternalServerError(message)
    elif status_code == 503:
        raise exceptions.ServerDown(message)
    else:
        raise exceptions.UnexpectedError(message)


# validate that value provided match the input type expected
def check_value(param, value):
    input_type = param['type']
    # string
    if input_type == 'string' and isinstance(value, str):
        # check for choices
        if 'choices' in param and value not in param['choices']:
            return False
        return True
    # boolean
    elif input_type == 'boolean' and isinstance(value, (int, bool)):
        return True
    # array
    elif input_type == 'array' and isinstance(value, list):
        return True
    # hash
    elif input_type == 'hash' and isinstance(value, dict):
        return True
    # integers
    elif input_type == 'integer' and isinstance(value, int):
        # check for choices
        if 'choices' in param and value not in param['choices']:
            return False
        return True
    # uuid 4
    elif input_type == 'uuid':
        try:
            UUID(value, version=4)
            return True
        except ValueError:
            return None
    # ip address
    elif input_type == 'ip_address':
        try:
            socket.inet_pton(socket.AF_INET, value)
        except AttributeError:
            try:
                socket.inet_aton(value)
            except socket.error:
                return False
            return value.count('.') == 3
        except socket.error:
            return False
        return True
    elif input_type == 'password':
        return True
    # failed
    return False


def remove_dups_value_in_array(data):
    if isinstance(data, dict):
        for k in data:
            value = remove_dups_value_in_array(data[k])
            data[k] = value
    elif isinstance(data, list):
        seen = set()
        for num, item in enumerate(data):
            if isinstance(item, dict) or isinstance(item, dict):
                value = remove_dups_value_in_array(item)
                data[num] = value
            else:
                if item in seen:
                    data.remove(item)
                seen.add(item)
    return data


class JsonUUIDEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, UUID):
            return o.hex
        return json.JSONEncoder.default(self, o)


class ObjDict(dict):
    def __getattribute__(self, item):
        try:
            val = self[item]
            if isinstance(val, str):
                val = import_string(val)
            elif isinstance(val, (list, tuple)):
                val = [import_string(v) if isinstance(v, str) else v for v in val]
            self[item] = val
        except KeyError:
            val = super(ObjDict, self).__getattribute__(item)

        return val

# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global LLC
# Copying or reproduction without prior written approval is prohibited. 
# Copyright (c) 2019 =================================================
import socket
from uuid import UUID
import json
import logging
from django import http
from django.db import connection
from django.conf import settings
from libs.utility.config_parsers import get_config
from django.utils.module_loading import import_string
from django.core.serializers.json import DjangoJSONEncoder


logger = logging.getLogger(__name__)
config = get_config()


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




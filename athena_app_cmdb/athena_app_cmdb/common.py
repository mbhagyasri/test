# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global
# Copying or reproduction without prior written approval is prohibited.
# Copyright (c) 2021 =================================================

import logging
import re
from . import models, serializers
from .utils.helper_methods import check_value
from .middleware import ViewException

logger = logging.getLogger(__name__)

FORMAT = 'json'
IGNORE_FILTERS = ['page_size', 'page', 'order_by']
FILTER_FIELDS = {"environment_name": "environment.name", "location_name": "location.name",
                 }


def get_model(objname, raise_exception=True):

    if objname not in models.models_class_lookup:
        resp = "%s table can not be found." % objname
        if raise_exception:
            raise ViewException(FORMAT, resp, 404)
        else:
            return None
    obj = models.models_class_lookup[objname]

    return obj


def get_model_all(request, objname, obj):
    if objname == 'tasks' or 'HTTP_X_INCLUDE_DELETED' in request.META or 'history' in objname:
        obj = obj.raw_objects.all()
    else:
        obj = obj.objects.all()
    return obj

def get_item(request, obj, item, raise_exception=True):
    """
    For backward compatible with old App Registry id, we will search both uuid format and old format
    :param request: request object
    :param obj: model object
    :param item: id to search
    :param raise_exception: exit on error or not
    :return: data object
    """
    got_data = False
    data = None

    if check_value({'type': 'uuid'}, item):
        if obj.objects.objects.filter(id=item).exists():
            data = obj.objects.get(id=item)
            got_data = True
    elif hasattr(obj, 'refid') and obj.objects.filter(refid=item).exists():
        data = obj.objects.get(refid=item)
        got_data = True
    if not got_data and raise_exception:
        raise ViewException(FORMAT, '{} not found.'.format(item), 404)
    return data


def filter_get_request(request, data, page_size):
    order_by = None
    # parsing filters
    for query in request.query_params:
        query_value = request.GET.getlist(query)
        if query == 'page_size':
            # set page_size to user param
            page_size = query_value[0]
        if query in IGNORE_FILTERS:
            continue
        if query == 'exclude':
            for q in query_value:
                ex = {}
                if '=' in q:
                    array = q.split('=')
                    key = array[0]
                    key_list = key.split('.')
                    for num, name in enumerate(key_list):
                        if name in FILTER_FIELDS:
                            key_list[num] = FILTER_FIELDS[name]
                    key = '.'.join(key_list)
                    qf = re.sub(r'\.', "__", key)
                    ex[qf] = array[1]
                    if ex[qf].lower() == "true":
                        ex[qf] = True
                    elif ex[qf].lower() == "false":
                        ex[qf] = False
                    elif key_list[-1] == "in":
                        values_list = array[1].split(',')
                        ex[qf] = values_list
                    try:
                        data = data.exclude(**ex)
                    except Exception as e:
                        logger.exception(e)
                        raise ViewException(FORMAT, 'Invalid filter request', 400)
                else:
                    qf = re.sub(r'\.', "__", q)
                    # noinspection PyArgumentList
                    try:
                        logger.debug('exclude: {}'.format(qf))
                        data = data.exclude(**qf)
                    except Exception as e:
                        logger.exception(e)
                        raise ViewException(FORMAT, 'Invalid filter request', 400)

        else:
            for q in query_value:
                ft = {}
                key = query
                key_list = key.split('.')
                for num, name in enumerate(key_list):
                    if name in FILTER_FIELDS:
                        key_list[num] = FILTER_FIELDS[name]
                key = '.'.join(key_list)
                qf = re.sub(r'\.', "__", key)
                ft[qf] = q
                if ft[qf].lower() == "true":
                    ft[qf] = True
                elif ft[qf].lower() == "false":
                    ft[qf] = False
                elif key_list[-1] == "in":
                    values_list = q.split(',')
                    ft[qf] = values_list
                try:
                    logger.debug(ft)
                    data = data.filter(**ft)
                except Exception as e:
                    logger.exception(e)
                    raise ViewException(FORMAT, "Invalid filter request.", 400)
    return data, page_size


def common_item_processing(request, objname, data, method):
    name = data['id'] if 'id' in data else None
    try:
        valid, errors = models.validate_json(objname, data, raise_exception=False)
        if not valid:
            return valid, {}, {'item': name, 'errors': errors}
        serializer_class = serializers.serializer_class_lookup[objname]
        if method == 'post':
            serializer = serializer_class(data=data)
        else:
            obj = get_model(objname)
            item = data.get('id', '')
            obj = get_item(request, obj, item, raise_exception=False)
            if not obj:
                return False, {}, {'item': name, 'errors': 'Item {} not found.'.format(item)}
            serializer = serializer_class(obj, data=data)
        if serializer.is_valid():
            serializer.save()
            return_data = serializer.data
        else:
            return False, {}, serializer.errors

    except Exception as e:
        logger.exception(e)
        pass
        return False, {}, {'item': name, 'errors': 'Invalid Request'}

    return True, return_data, None


def process_product(request, data, method):
    objname = 'products'
    valid, return_data, errors = common_item_processing(request, objname, data, method)
    if not valid:
        return valid, return_data, errors
    # now let's process environments





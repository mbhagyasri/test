# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global
# Copying or reproduction without prior written approval is prohibited.
# Copyright (c) 2021 =================================================

import re
import os
import logging
import jsonpatch
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta


from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import never_cache


from django.utils.decorators import method_decorator
from rest_framework import exceptions as rest_exceptions
from rest_framework.decorators import api_view
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt import authentication

from rest_framework.response import Response
from . import models, serializers
from .operators import Validators
from .paginator import MyPaginationMixin
from .middleware import ViewException
from .utils.helper_methods import check_value
from libs.utility.config_parsers import get_config
from copy import deepcopy

logger = logging.getLogger(__name__)
config = get_config()

FORMAT = 'json'
IGNORE_FILTERS = ['page_size', 'page', 'order_by']
CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

FILTER_FIELDS = {"environment_name": "environment.name", "location_name": "location.name",
                 }
# Allow to turn Auth on or off in Dev environment
AUTH_CLASS = [authentication.JWTAuthentication]
PERM_CLASS = [IsAuthenticated]
if int(os.getenv('ENABLE_AUTH', 1)) == 0 and os.getenv('DJANGO_SETTINGS_MODULE',
                                                       'app_registry.settings.prod') == 'CDBApp.settings.dev':
    AUTH_CLASS = []
    PERM_CLASS = []


@api_view(['GET'])
def monitor(request):
    json_str = {'Health': 'OK'}
    return Response(json_str, content_type='application/json', status=200)

@api_view(['GET'])
def redirect(request):
    response = HttpResponseRedirect('/')
    response.status_code = 302
    return response


@api_view(['GET'])
def api_root(request, format=None):
    athena_app_cmdb_api_root = reverse('home', request=request, format=format)
    json_str = {'ROOT': reverse('home', request=request, format=format)}
    return Response({'home': reverse('home', request=request, format=format)})


def get_model(objname):

    if objname not in models.models_class_lookup:
        resp = "%s table can not be found." % objname
        logger.error(resp)
        raise ViewException(FORMAT, resp, 404)
    obj = models.models_class_lookup[objname]

    return obj


def reformat_properties(data):
    return_list = []
    logger.info('I GOT HERE')
    for item in data:
        logger.info('HERE \n {}'.format(item))
        if 'properties' in item:
            new_dict = deepcopy(item)
            properties = new_dict.pop('properties')
            for key in new_dict:
                if key in properties:
                    properties.pop(key)
            if not properties:
                logger.info ('EMPTY')
                item.pop('properties')
            else:
                item['properties'] = properties
        return_list.append(item)
    return return_list


def get_item(objname, obj, item):
    """
    For backward compatible with old App Registry id, we will search both uuid format and old format
    :param objname: string value of the uri resource
    :param obj: model object
    :param item: id to search
    :return: data object
    """
    got_data = False
    data = None
    valid = check_value({'type': 'uuid'}, item)
    if not valid:
        q = {'properties__old_version_id': item}
        data = obj.filter(**q)
        if data.count() > 0:
            got_data = True
            data = data[:1].get()
    elif obj.filter(id=item).exists:
        data = obj.get(id=item)
        got_data = True
    if not got_data:
        logger.info('NOT FOUND')
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


# -------------------------  View Classes ---------------------------------------


# noinspection PyMethodMayBeStatic
@method_decorator(never_cache, name='dispatch')
class athena_app_cmdbList(APIView, MyPaginationMixin):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    path = '/'

    def get(self, request, objname):
        page_size = api_settings.PAGE_SIZE

        obj = get_model(objname)
        if objname == 'tasks' or 'HTTP_X_INCLUDE_DELETED' in request.META or 'history' in objname:
            data = obj.objects.all()
        else:
            data = obj.objects.exclude(deleted=1)
        data, page_size = filter_get_request(request, data, page_size)
        try:
            if data:
                pass
            else:
                raise ViewException(FORMAT, "No {} found.".format(objname), 404)
        except Exception as e:
            logger.exception(e)
            raise ViewException(FORMAT, "No {} found.".format(objname), 404)
        serializer_class = serializers.serializer_class_lookup_read[objname]
        # do not show pagination if query result is less than page size
        logger.debug('count %s' % data.count())

        try:
            if data.count() <= int(page_size):
                self.pagination_class = None
            page = self.paginate_queryset(data, self.request)
            if page is not None:
                obj_serializer = serializer_class(page, many=True)
                decrypt_data = obj_serializer.data
                return self.get_paginated_response(reformat_properties(decrypt_data), objname)
            else:
                obj_serializer = serializer_class(data, many=True)
                decrypt_data = obj_serializer.data
                return Response(reformat_properties(decrypt_data))
        except rest_exceptions.NotFound:
            raise ViewException(FORMAT, 'Not found.', 404)
        except Exception as e:
            logger.exception(e)
            raise ViewException(FORMAT, 'Server Exception', 500)

    def post(self, request, objname):
        path = '/%s' % objname
        logger.info("Processing POST for %s" % objname)
        # check to make sure the model exists
        obj = get_model( objname)
        # pulling mappings config
        method = 'post'
        logger.debug('path %s method: %s request: %s' % (path, method, request.data))
        data = Validators().parse_mappings(path=path, method=method, data=request.data)
        # payload is valid .
        serializer_class = serializers.serializer_class_lookup[objname]
        if 'associations' in data:
            del data['associations']
        serializer = serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=400)
        content = serializer.data
        return Response(content, status.HTTP_201_CREATED)


@method_decorator(never_cache, name='dispatch')
class athena_app_cmdbListDetail(APIView, MyPaginationMixin):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    path = ''

    def get(self, request, objname):
        page_size = api_settings.PAGE_SIZE

        obj = get_model(objname)
        if 'HTTP_X_INCLUDE_DELETED' in request.META or 'history' in objname:
            data = obj.objects.all()
        else:
            data = obj.objects.exclude(deleted=1)
        data, page_size = filter_get_request(request, data, page_size)
        try:
            if data:
                pass
            else:
                raise ViewException(FORMAT, "No {} found.".format(objname), 404)
        except Exception as e:
            logger.exception(e)
            raise ViewException(FORMAT, "No {} found.".format(objname), 404)
        serializer_class = serializers.serializer_class_lookup_read[objname]
        if objname in serializers.serializer_class_lookup_detail:
            serializer_class = serializers.serializer_class_lookup_detail[objname]
        # do not show pagination if query result is less than page size
        logger.info('count %s' % data.count())

        try:
            if data.count() <= int(page_size):
                self.pagination_class = None
            page = self.paginate_queryset(data, self.request)
            if page is not None:
                obj_serializer = serializer_class(page, many=True)
                decrypt_data = obj_serializer.data
                return self.get_paginated_response(decrypt_data, objname)
            else:
                obj_serializer = serializer_class(data, many=True)
                decrypt_data = obj_serializer.data
                return Response({objname: decrypt_data})
        except rest_exceptions.NotFound:
            raise ViewException(FORMAT, 'Not found.', 404)
        except Exception as e:
            logger.exception(e)
            raise ViewException(FORMAT, 'Server Exception', 500)


@method_decorator(never_cache, name='dispatch')
class athena_app_cmdbItem(APIView):

    def perform_update(self, serializer):
        serializer.save(last_changed=timezone.now())

    def get(self, request, objname, item):
        obj = get_model(objname)
        if objname == 'tasks' or 'HTTP_X_INCLUDE_DELETED' in request.META or 'history' in objname:
            obj = obj.objects.all()
        else:
            obj = obj.objects.exclude(deleted=1)
        data = get_item(objname, obj, item)
        serializer_class = serializers.serializer_class_lookup_read[objname]
        obj_serializer = serializer_class(data)
        decrypt_data = obj_serializer.data
        return Response(decrypt_data)

    def delete(self, request, objname, item):
        obj = get_model(objname)
        data = get_item(objname, obj, item)
        serializer_class = serializers.serializer_class_lookup_read[objname]
        obj_serializer = serializer_class(data)
        if 'HTTP_X_FORCE_DELETE' in request.META and \
                request.META['HTTP_X_FORCE_DELETE'].lower() == 'true':
            logger.info('Deleting %s against %s' % (item, objname))
            try:
                data.delete()
            except Exception as e:
                logger.exception(e)
                raise ViewException(FORMAT, "Invalid request.", 400)
        else:
            data.name = '{} DELETED {}'.format(data.name, timezone.now())
            data.deleted = True
            data.deleted_at = datetime.now()
            data.save()
        return Response("Done", status.HTTP_204_NO_CONTENT)

    def put(self, request, objname, item):
        path = '/{0}'.format(objname)
        obj = get_model(objname)
        if objname == 'tasks' or 'HTTP_X_INCLUDE_DELETED' in request.META or 'history' in objname:
            obj = obj.objects.all()
        else:
            obj = obj.objects.exclude(deleted=1)
        obj = get_item(objname, obj, item)
        method = 'post'
        logger.debug('path %s method: %s request: %s' % (path, method, request.data))
        data = Validators().parse_mappings(data=request.data, path=path, method=method)
        # payload is valid .
        serializer_class = serializers.serializer_class_lookup[objname]
        if 'associations' in data:
            del data['associations']
        serializer = serializer_class(obj, data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            raise ViewException(FORMAT, serializer.errors, 400)
        return Response(serializer.data, status.HTTP_200_OK)

    def patch(self, request, objname, item):
        
        logger.info('Processing method: PATCH for {} with id: {}'.format(objname, item))
        # We don't support patch against deployment data
        if objname == 'deployments':
            raise ViewException(FORMAT, 'PATCH method is not supported.', 405)
        if request.META['CONTENT_TYPE'] != 'application/json-patch+json':
            raise ViewException(FORMAT, 'PATCH method expects application/json-patch+json Content-Type.', 406)
        obj = get_model(objname)
        if objname == 'tasks' or 'HTTP_X_INCLUDE_DELETED' in request.META or 'history' in objname:
            obj = obj.objects.all()
        else:
            obj = obj.objects.exclude(deleted=1)
        obj = get_item(objname, obj, item)
        serializer_class = serializers.serializer_class_lookup[objname]
        obj_serializer = serializer_class(obj)
        current_data = obj_serializer.data
        # Exclude association data
        if 'associations' in current_data:
            del current_data['associations']
        merge_data = None
        try:
            merge_data = jsonpatch.apply_patch(current_data, request.body)
        except Exception as e:
            raise ViewException(FORMAT, "Invalid request. {}".format(e), 400)
        serializer = serializer_class(obj, data=merge_data, partial=False)
        if serializer.is_valid():
            serializer.update(obj, validated_data=serializer.validated_data)
            serializer.save()
        else:
            raise ViewException(FORMAT, serializer.errors, 400)
        return Response(serializer.data, status.HTTP_200_OK)


@method_decorator(never_cache, name='dispatch')
class athena_app_cmdbItemDetail(APIView):

    def get(self, request, objname, item):
        obj = get_model(objname)
        if 'HTTP_X_INCLUDE_DELETED' in request.META or 'history' in objname:
            data = obj.objects.all()
        else:
            data = obj.objects.exclude(deleted=1)
        data = get_object_or_404(data, id=item)
        serializer_class = serializers.serializer_class_lookup_detail[objname]
        obj_serializer = serializer_class(data)
        decrypt_data = obj_serializer.data
        return Response(decrypt_data)


@method_decorator(never_cache, name='dispatch')
class athena_app_cmdbAssociationsList(APIView):
    def get(self, request, parentobjname, parent,):
        parentobj = get_model(parentobjname)
        path = '/%s/:id/associations' % parentobjname
        childobj_list = Validators().get_associations(path, parentobjname)
        pdata = parentobj.objects.exclude(deleted=1)
        pdata = get_object_or_404(pdata, id=parent)
        parent_serializer_class = serializers.serializer_class_lookup_associations[parentobjname]
        parent_serializer = parent_serializer_class(pdata)
        data = parent_serializer.data
        associations = []
        if childobj_list:
            for childobjname in childobj_list:
                childobj = get_model(childobjname)
                cdata = childobj.objects.exclude(deleted=1)
                pfiltername = '%s__id' % parentobjname
                cfilter = {pfiltername: pdata.id}
                cdata = cdata.filter(**cfilter)
                child_serializer_class = serializers.serializer_class_lookup_associations[childobjname]
                child_serializer = child_serializer_class(cdata, many=True)
                associations.append({childobjname: child_serializer.data})
        data['associations'] = associations
        return Response(data, status.HTTP_200_OK)


@method_decorator(never_cache, name='dispatch')
class athena_app_cmdbAssociationsChildList(APIView):
    def get(self, request, parentobjname, parent, childobjname):
        parentobj = get_model( parentobjname)
        childobj = get_model( childobjname)
        pdata = parentobj.objects.exclude(deleted=1)
        pdata = get_object_or_404(pdata, id=parent)
        parent_serializer_class = serializers.serializer_class_lookup_associations[parentobjname]
        parent_serializer = parent_serializer_class(pdata)
        data = parent_serializer.data
        cdata = childobj.objects.exclude(deleted=1)
        pfiltername = '%s__id' % parentobjname
        cfilter = {pfiltername: pdata.id}
        cdata = cdata.filter(**cfilter)
        child_serializer_class = serializers.serializer_class_lookup_associations[childobjname]
        child_serializer = child_serializer_class(cdata, many=True)
        data['associations'] = {childobjname: child_serializer.data}
        return Response(data, status.HTTP_200_OK)


@method_decorator(never_cache, name='dispatch')
class athena_app_cmdbAssociationsChildCreateDestroy(APIView):
    parentobj = None
    childobj = None

    def post(self, request, parentobjname, parent, childobjname, child):
        self.parentobj = get_model(parentobjname)
        self.childobj = get_model(childobjname)
        path = '/%s/:id/associations/%s/:id' % (parentobjname, childobjname)
        method = 'post'
        logger.debug('path %s method: %s request: %s' % (path, method, request.data))
        Validators().parse_mappings(path=path, method=method, data=request.data)
        pdata = self.parentobj.objects.exclude(deleted=1)
        pdata = get_object_or_404(pdata, id=parent)
        cdata = self.childobj.objects.exclude(deleted=1)
        cdata_item = get_object_or_404(cdata, id=child)
        cdata_item.__getattribute__(parentobjname).add(pdata)
        cdata_item.save()
        pfiltername = '%s__id' % parentobjname
        cfilter = {pfiltername: pdata.id}
        cdata = cdata.filter(**cfilter)
        child_serializer_class = serializers.serializer_class_lookup_associations[childobjname]
        child_serializer = child_serializer_class(cdata, many=True)
        parent_serializer_class = serializers.serializer_class_lookup_associations[parentobjname]
        parent_serializer = parent_serializer_class(pdata)
        data = parent_serializer.data
        data['associations'] = {childobjname: child_serializer.data}
        return Response(data, status.HTTP_200_OK)

    def delete(self, request, parentobjname, parent, childobjname, child):
        self.parentobj = get_model( parentobjname)
        self.childobj = get_model( childobjname)
        # Validation to make sure parent and child exists
        get_model(parentobjname)
        get_model(childobjname)
        pdata = self.parentobj.objects.all()
        pdata = get_object_or_404(pdata, id=parent)
        cdata = self.childobj.objects.all()
        cdata_item = get_object_or_404(cdata, id=child)
        cdata_item.__getattribute__(parentobjname).remove(pdata)
        cdata_item.save()
        return Response("Done", status.HTTP_204_NO_CONTENT)


@method_decorator(never_cache, name='dispatch')
class athena_app_cmdbItemHistory(APIView, MyPaginationMixin):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    path = ''

    def get(self, request, objname, item, detail=None):
        page_size = api_settings.PAGE_SIZE

        history_objname = '{0}_history'.format(objname)
        obj = get_model(history_objname)
        if history_objname not in models.models_name_lookup:
            raise ViewException(FORMAT, "This model {} does not store history.".format(objname), 404)
        model_name = models.models_name_lookup[objname]
        kwarg = {model_name: item}
        data = obj.objects.all()
        data = data.filter(**kwarg)
        data, page_size = filter_get_request(request, data, page_size)
        if not data.exists():
            raise ViewException(FORMAT, "No {} found.".format(history_objname), 404)
        serializer_class = serializers.serializer_class_lookup_read[history_objname]
        if detail and detail == 'detail':
            serializer_class = serializers.serializer_class_lookup_detail[history_objname]
        # do not show pagination if query result is less than page size
        logger.info('count %s' % data.count())

        try:
            if data.count() <= int(page_size):
                self.pagination_class = None
            page = self.paginate_queryset(data, self.request)
            if page is not None:
                obj_serializer = serializer_class(page, many=True)
                decrypt_data = obj_serializer.data
                return self.get_paginated_response(decrypt_data, objname)
            else:
                obj_serializer = serializer_class(data, many=True)
                decrypt_data = obj_serializer.data
                return Response({history_objname: decrypt_data})
        except Exception as e:
            logger.exception(e)
            raise ViewException(FORMAT, 'Server Exception', 500)


@method_decorator(never_cache, name='dispatch')
class athena_app_cmdbItemHistoryDetail(APIView):

    def get(self, request, objname, history_item):
        obj = get_model('{}_history'.format(objname))
        data = obj.objects.all()
        data = get_object_or_404(data, id=history_item)
        serializer_class = serializers.serializer_class_lookup_read['{}_history'.format(objname)]
        obj_serializer = serializer_class(data)
        return Response(obj_serializer.data)

    def delete(self, request, objname, history_item):
        logger.info('DELETE {} history: {}'.format(objname, history_item))
        obj = get_model('{}_history'.format(objname))
        data = get_object_or_404(obj, id=history_item)
        data.delete()
        return Response("Done", status.HTTP_204_NO_CONTENT)


@method_decorator(never_cache, name='dispatch')
class athena_app_cmdbItemHistorySync(APIView):
    def post(self, request, objname, history_item):
        obj = get_model('{}_history'.format(objname))
        data = get_object_or_404(obj, id=history_item)
        logger.info('Setting Sync_status to True for {}'.format(history_item))
        data.sync_status = True
        data.save()
        return Response(status.HTTP_200_OK)

    def delete(self, request, objname, history_item):
        obj = get_model('{}_history'.format(objname))
        data = get_object_or_404(obj, id=history_item)
        logger.info('Setting Sync_status to True for {}'.format(history_item))
        data.sync_status = False
        data.save()
        return Response(status.HTTP_200_OK)


@method_decorator(never_cache, name='dispatch')
class athena_app_cmdbBulkSyncUpdate(APIView):
    def post(self, request, objname):
        obj = get_model('{}_history'.format(objname))
        data = request.data
        try:
            if isinstance(data, list):
                for i in data:
                    if obj.objects.filter(id=i).exists():
                        logger.info('Updating {} sync update for {} to True'.format(objname, i))
                        robj = obj.objects.get(id=i)
                        robj.sync_status = True
                        robj.save()
                    else:
                        logger.info('{} does not exist.  Skipping sync update'.format(i))
                # need to clean out old data if any
                self.clean_old_data(objname)
                return Response("Done", status.HTTP_204_NO_CONTENT)
            else:
                logger.exception("Data to update history sync status is not an array.")
                raise ViewException(FORMAT, {"error":"Expect a list of id to update."}, 400)
        except Exception as e:
            logger.exception(e)
            raise ViewException(FORMAT, "Failed to perform Sync Update", 400)

    def delete(self, request, objname):
        obj = get_model('{}_history'.format(objname))
        data = request.data
        try:
            if isinstance(data, list):
                for i in data:
                    if obj.objects.filter(id=i).exists():
                        robj = obj.objects.get(id=i)
                        robj.sync_status = False
                        robj.save()
                    else:
                        logger.info('{} does not exist.  Skipping sync update'.format(i))
                return Response("Done", status.HTTP_204_NO_CONTENT)
            else:
                logger.exception("Data to update history sync status is not an array.")
                raise ViewException(FORMAT, {"error":"Expect a list of id to update."}, 400)
        except Exception as e:
            logger.exception(e)
            raise ViewException(FORMAT, "Failed to perform Sync Update", 400)

    def clean_old_data(self, objname):
        obj = get_model('{}_history'.format(objname))
        time_threshold = datetime.now() + relativedelta(months=int(config.get('global',
                                                                              'sync_history_retention_months')))
        if obj.objects.filter(created_at__lt=time_threshold).filter(sync_status=True).exists():
            query = obj.objects.filter(created_at__lt=time_threshold).filter(sync_status=True)
            logger.info('Cleaning up old {}_history records.'.format(objname))
            try:
                for row in query:
                    logger.info('Deleting {}'.format(row.id))
                    row.delete()
                query.save()
            except Exception as e:
                logger.exception(e)
                pass
        return


class athena_app_cmdbBulkUpdate(APIView, MyPaginationMixin):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def patch(self, request):
        return_data = {}
        request_data = None
        if request.META['CONTENT_TYPE'] == 'application/json-patch+json':
            request_data = json.loads(request.body)
        else:
            request_data = request.data
        for objname, content in request_data.items():
            return_content = []
            # We don't support patch against deployment data
            if objname == 'deployments':
                raise ViewException(FORMAT, 'PATCH method is not supported.', 405)

            obj = get_model(objname)
            obj = obj.objects.all()
            serializer_class = serializers.serializer_class_lookup[objname]
            if not isinstance(content, list):
                raise ViewException(FORMAT, {"error": "Expect a list of resources"}, 406)
            for each in content:
                item = each.get('id', None)
                if not item:
                    raise ViewException(FORMAT, {"error": "No id found in the data list for update"}, 400)
                robj = get_object_or_404(obj, id=item)
                obj_serializer = serializer_class(robj)
                merge_data = None
                try:
                    merge_data = jsonpatch.apply_patch(obj_serializer.data, json.dumps(each['patch_data']))
                except Exception as e:
                    raise ViewException(FORMAT, "Invalid request. {}".format(e), 400)
                serializer = serializer_class(robj, data=merge_data)
                if serializer.is_valid():
                    serializer.save()
                    return_content.append(serializer.data)
                else:
                    raise ViewException(FORMAT, serializer.errors, 400)
            return_data[objname] = return_content
        return Response(return_data, status.HTTP_200_OK)

    def post(self, request):
        return_data = {}
        for objname, content in request.data.items():
            return_content = []
            path = '/{0}'.format(objname)
            obj = get_model(objname)
            return_content = []
            for each in content:
                try:
                    method = 'post'
                    logger.debug('path %s method: %s request: %s' % (path, method, request.data))
                    data = Validators().parse_mappings(data=each, path=path, method=method)
                    serializer_class = serializers.serializer_class_lookup[objname]
                    serializer = serializer_class(data=data)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        return Response(serializer.errors, status=400)
                    # We now need to encrypt vault data and save it back
                    content = serializer.data
                except Exception as e:
                    logger.exception(e)
                    raise ViewException(FORMAT, "Invalid request.", 400)
            return_data[objname] = content
        return Response(return_data, status.HTTP_201_CREATED)

    def put(self, request):
        return_data = {}
        for objname, content in request.data.items():
            return_content = []
            path = '/{0}/:id'.format(objname)
            obj = get_model(objname)
            return_content = []
            for each in content:
                try:
                    item = each.get('id', None)
                    if not item:
                        raise ViewException(FORMAT, {"error": "No id found in the data list for update"}, 400)
                    robj = get_object_or_404(obj, id=item)
                    method = 'put'
                    logger.debug('path %s method: %s request: %s' % (path, method, request.data))
                    data = Validators().parse_mappings(data=each, path=path, method=method)
                    # payload is valid .
                    serializer_class = serializers.serializer_class_lookup[objname]
                    serializer = serializer_class(robj, data=data)
                    if serializer.is_valid():
                        serializer.save()
                        return_content.append(serializer.data)
                    else:
                        raise ViewException(FORMAT, serializer.error, 400)
                except Exception as e:
                    logger.exception(e)
                    raise ViewException(FORMAT, "Invalid request.", 400)
            return_data[objname] = return_content
        return Response({objname: return_data}, status.HTTP_200_OK)


@method_decorator(never_cache, name='dispatch')
class AssetEnvironments(APIView, MyPaginationMixin):

    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    path = ''
#    authentication_classes = AUTH_CLASS
#    permission_classes = PERM_CLASS

    def get(self, request, objname, item):
        page_size = api_settings.PAGE_SIZE
        obj = get_model('tasks')
        kwarg = {'model': objname, 'item': item}
        data = obj.objects.all()
        data = data.filter(**kwarg)
        data, page_size = filter_get_request(request, data, page_size)
        if not data.exists():
            raise_for_error(404, "No tasks for {} {} found.".format(objname, item))
        serializer_class = serializers.serializer_class_lookup_read['tasks']
        # do not show pagination if query result is less than page size
        logger.info('count %s' % data.count())

        try:
            if data.count() <= int(page_size):
                self.pagination_class = None
            page = self.paginate_queryset(data, self.request)
            if page is not None:
                obj_serializer = serializer_class(page, many=True)
                decrypt_data = obj_serializer.data
                if 'HTTP_X_SKIP_DECRYPT_DATA' not in request.META or \
                        request.META['HTTP_X_SKIP_DECRYPT_DATA'] != "true":
                    decrypt_data = VaultProcessing().read(decrypt_data)


                return self.get_paginated_response(decrypt_data, objname)
            else:
                obj_serializer = serializer_class(data, many=True)
                decrypt_data = obj_serializer.data
                if 'HTTP_X_SKIP_DECRYPT_DATA' not in request.META or \
                        request.META['HTTP_X_SKIP_DECRYPT_DATA'] != "true":
                    decrypt_data = VaultProcessing().read(decrypt_data)
                return Response({'tasks': decrypt_data})
        except Exception as e:
            logger.exception(e)
            raise_for_error(500, 'Server Exception')

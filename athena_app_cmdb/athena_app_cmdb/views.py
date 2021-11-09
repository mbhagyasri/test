# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global
# Copying or reproduction without prior written approval is prohibited.
# Copyright (c) 2021 =================================================

import re
import os
import logging
import jsonpatch
import json
import itertools
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
from . import models, serializers, common
from .operators import Validators
from .paginator import MyPaginationMixin
from .middleware import ViewException
from .utils.helper_methods import check_value, validateAssetId
from copy import deepcopy

logger = logging.getLogger(__name__)

FORMAT = 'json'
CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


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


# -------------------------  View Classes ---------------------------------------


# noinspection PyMethodMayBeStatic
@method_decorator(never_cache, name='dispatch')
class athena_app_cmdbList(APIView, MyPaginationMixin):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    path = '/'

    def get(self, request, objname):
        page_size = api_settings.PAGE_SIZE

        obj = common.get_model(objname)
        obj = common.get_model_all(request, objname, obj)
        data, page_size = common.filter_get_request(request, obj, page_size)
        if 'HTTP_X_PAGE-SIZE' in request.META:
            page_size = request.META['HTTP_X_PAGE-SIZE']
        if not data:
            raise ViewException(FORMAT, "No {} found.".format(objname), 404)
        serializer_class = serializers.serializer_class_lookup_read[objname]
        # do not show pagination if query result is less than page size
        try:
            if data.count() <= int(page_size):
                self.pagination_class = None
            page = self.paginate_queryset(data, self.request)
            if page is not None:
                obj_serializer = serializer_class(page, many=True)
                decrypt_data = obj_serializer.data
                return self.get_paginated_response(decrypt_data)
            else:
                obj_serializer = serializer_class(data, many=True)
                decrypt_data = obj_serializer.data
                return Response(decrypt_data)
        except rest_exceptions.NotFound:
            raise ViewException(FORMAT, 'Not found.', 404)
        except Exception as e:
            logger.exception(e)
            raise ViewException(FORMAT, 'Server Exception', 500)

    def post(self, request, objname):
        # check to make sure the model exists
        common.get_model(objname, request)
        data = request.data
        # Validation
        models.validate_json(objname, data)
        if objname == 'products':
            new_dict = deepcopy(data)
            for key in ['created_at', 'deleted', 'deleted_at', 'created_by', 'updated_at', 'updated_by']:
                if key in new_dict:
                    del new_dict[key]
            data = {'id': new_dict['id'], 'properties': new_dict}
        # validate asset master id if doing a post to /assets
        if objname == 'assets':
            new_dict = deepcopy(data)
            if 'assetMasterId' in new_dict: 
                amid = new_dict['assetMasterId']
                checkid = validateAssetId(amid)
                if checkid == False:
                    raise ViewException(FORMAT, 'Error Validating Asset Master Id: {}'.format(amid), 500)
        # validate resources on owner and location, if doing a post to /resources
        if objname == 'resources':
            spec = data.get('spec', {})
            platform=spec.get('platform')
            owner=spec.get('owner')
            if not models.Location.objects.filter(refid=platform).exists():
                raise ViewException(FORMAT, 'Platform: {} does not exists'.format(platform), 400)
            if not models.Team.objects.filter(refid=owner).exists():
                raise ViewException(FORMAT, 'Owner: {} does not exists'.format(owner), 400)
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
        obj = common.get_model(objname)
        obj = common.get_model_all(request, objname, obj)
        data, page_size = common.filter_get_request(request, obj, page_size)
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
        try:
            if (hasattr(data, 'count') and data.count() <= int(page_size)) or (data.objects.count() <= int(page_size)):
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
        obj = common.get_model(objname)
        serializer_class = serializers.serializer_class_lookup_read[objname]
        if objname == 'assetsByEnvironment':
            data = common.get_model_all(request, objname, obj)
            data = data.filter(asset__refid=item)
            if not data:
                raise ViewException(FORMAT, "No {} found.".format(objname), 404)
            obj_serializer = serializer_class(data, many=True)
        else:
            data = common.get_item(request, obj, item)
            obj_serializer = serializer_class(data)

        decrypt_data = obj_serializer.data
        return Response(decrypt_data)

    def delete(self, request, objname, item):
        obj = common.get_model(objname)
        data = common.get_item(request, obj, item)
        # check if there are attaches
        if objname == 'resources':
            attaches = data.assetEnvironments.all()
            if attaches:
                raise ViewException(FORMAT, "Failed to delete {}.  There are still assets being attached.".format(item),
                                    400)
        if 'HTTP_X_FORCE_DELETE' in request.META and request.META['HTTP_X_FORCE_DELETE'].lower() == 'true':
            try:
                data.hard_delete()
            except Exception as e:
                logger.exception(e)
                raise ViewException(FORMAT, "Invalid request.", 400)
        else:
            logger.info('HERE SOFT DELETE')
            try:
                data.delete()
            except Exception as e:
                logger.exception(e)
                raise ViewException(FORMAT, "Invalid request.", 400)
        return Response("Done", status.HTTP_204_NO_CONTENT)

    def put(self, request, objname, item):
        obj = common.get_model(objname)
        obj = common.get_item(request, obj, item)
        data = request.data
        models.validate_json(objname, data)
        if objname == 'assets':
            new_dict = deepcopy(data)
            if 'assetMasterId' in new_dict: 
                amid = new_dict['assetMasterId']
                checkid = validateAssetId(amid)
                if checkid == False:
                    raise ViewException(FORMAT, 'Error Validating Asset Master Id {}'.format(amid), 500)
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
        # We don't support patch against deployment data
        if request.META['CONTENT_TYPE'] != 'application/json-patch+json':
            raise ViewException(FORMAT, 'PATCH method expects application/json-patch+json Content-Type.', 406)
        obj = common.get_model(objname)
        data = common.get_item(request, obj, item)
        serializer_class = serializers.serializer_class_lookup[objname]
        obj_serializer = serializer_class(data)
        current_data = obj_serializer.data
        # Exclude association data
        if 'associations' in current_data:
            del current_data['associations']
        merge_data = None
        try:
            merge_data = jsonpatch.apply_patch(current_data, request.body)
        except Exception as e:
            raise ViewException(FORMAT, "Invalid request. {}".format(e), 400)
        models.validate_json(objname, merge_data)
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
        obj = common.get_model(objname)
        data = get_object_or_404(obj, id=item)
        serializer_class = serializers.serializer_class_lookup_detail[objname]
        obj_serializer = serializer_class(data)
        decrypt_data = obj_serializer.data
        return Response(decrypt_data)


@method_decorator(never_cache, name='dispatch')
class athena_app_cmdbAssociationsList(APIView):
    def get(self, request, parentobjname, parent,):
        parentobj = common.get_model(parentobjname)
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
                childobj = common.get_model(childobjname)
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
class athena_app_cmdbAttachesList(APIView):
    request_type = 'default'

    def get(self, request, item, env,):
        parentobjname = 'assetsByEnvironment'
        parentobj = common.get_model(parentobjname)

        pdata = common.get_model_all(request, parentobjname, parentobj)
        if pdata.filter(asset__refid=item, refid=env).exists():
            pdata = pdata.get(asset__refid=item, refid=env)
        else:
            raise ViewException(FORMAT, "No {} found.".format(parentobjname), 404)
        serializer_class = serializers.serializer_class_lookup_associations[parentobjname]
        serializer = serializer_class(pdata, many=True)
        return Response(serializer.data, status.HTTP_200_OK)


@method_decorator(never_cache, name='dispatch')
class athena_app_cmdbAttachesCreateDestroy(APIView):

    def post(self, request, item, env, resource):
        parentobjname = 'assetsByEnvironment'
        parentobj = common.get_model(parentobjname)

        pdata = common.get_model_all(request, parentobjname, parentobj)
        if pdata.filter(asset__refid=item, refid=env).exists():
            pdata = pdata.get(asset__refid=item, refid=env)
        else:
            raise ViewException(FORMAT, "No {} found.".format(parentobjname), 404)
        childobjname = 'resources'
        childobj = common.get_model(childobjname)
        cdata_item = common.get_item(request, childobj, resource)
        cdata_item.assetEnvironments.add(pdata)
        cdata_item.save()
        return Response("Done", status.HTTP_200_OK)

    def delete(self, request, item, env, resource):
        parentobjname = 'assetsByEnvironment'
        parentobj = common.get_model(parentobjname)

        pdata = common.get_model_all(request, parentobjname, parentobj)
        if pdata.filter(asset__refid=item, refid=env).exists():
            pdata = pdata.get(asset__refid=item, refid=env)
        else:
            raise ViewException(FORMAT, "No {} found.".format(parentobjname), 404)
        childobjname = 'resources'
        childobj = common.get_model(childobjname)
        cdata_item = common.get_item(request, childobj, resource)
        cdata_item.assetEnvironments.remove(pdata)
        cdata_item.save()
        return Response("Done", status.HTTP_204_NO_CONTENT)


@method_decorator(never_cache, name='dispatch')
class athena_app_cmdbItemHistory(APIView, MyPaginationMixin):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    path = ''

    def get(self, request, objname, item, detail=None):
        page_size = api_settings.PAGE_SIZE

        history_objname = '{0}_history'.format(objname)
        obj = common.get_model(history_objname)
        if history_objname not in models.models_name_lookup:
            raise ViewException(FORMAT, "This model {} does not store history.".format(objname), 404)
        model_name = models.models_name_lookup[objname]
        kwarg = {model_name: item}
        data = obj.objects.all()
        data = data.filter(**kwarg)
        data, page_size = common.filter_get_request(request, data, page_size)
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
        obj = common.get_model('{}_history'.format(objname))
        data = obj.objects.all()
        data = get_object_or_404(data, id=history_item)
        serializer_class = serializers.serializer_class_lookup_read['{}_history'.format(objname)]
        obj_serializer = serializer_class(data)
        return Response(obj_serializer.data)

    def delete(self, request, objname, history_item):
        logger.info('DELETE {} history: {}'.format(objname, history_item))
        obj = common.get_model('{}_history'.format(objname))
        data = get_object_or_404(obj, id=history_item)
        data.delete()
        return Response("Done",status.HTTP_204_NO_CONTENT)


@method_decorator(never_cache, name='dispatch')
class athena_app_cmdbItemHistorySync(APIView):
    def post(self, request, objname, history_item):
        obj = common.get_model('{}_history'.format(objname))
        data = get_object_or_404(obj, id=history_item)
        logger.info('Setting Sync_status to True for {}'.format(history_item))
        data.sync_status = True
        data.save()
        return Response(status.HTTP_200_OK)

    def delete(self, request, objname, history_item):
        obj = common.get_model('{}_history'.format(objname))
        data = get_object_or_404(obj, id=history_item)
        logger.info('Setting Sync_status to True for {}'.format(history_item))
        data.sync_status = False
        data.save()
        return Response(status.HTTP_200_OK)


class athena_app_cmdbBulkChange(APIView, MyPaginationMixin):
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

            obj = common.get_model(objname)

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
            errors = []
            success = []
            return_content = []
            valid = common.get_model(objname, raise_exception=False)
            if not valid:
                errors.append("Table {} not found ".format(objname))
                continue
            if objname == 'assets' and 'HTTP_X_ETAG' in request.META and request.META['HTTP_X_ETAG'] == 'v1':
                content = self.asset_v1_processing(request, content)
            for each in content:
                name = each['id'] if 'id' in each else None
                try:
                    if objname == 'assets' and 'HTTP_X_ETAG' in request.META and request.META['HTTP_X_ETAG'] == 'v1':
                        pass
                    else:
                        models.validate_json(objname, each)
                    serializer_class = serializers.serializer_class_lookup[objname]
                    # create/update
                    itemobj = None
                    if name:
                        itemobj = common.get_item(request, valid, name, raise_exception=False)
                    if itemobj:
                        serializer = serializer_class(itemobj, data=each)
                    else:
                        serializer = serializer_class(data=each)
                    if serializer.is_valid():
                        serializer.save()
                        data = serializer.data
                    else:
                        errors.append({'item': name, 'errors': serializer.errors})
                        continue
                except Exception as e:
                    logger.exception(e)
                    pass
                    errors.append({'item': name, 'errors': 'Invalid Request'})
                    continue

                # We now need to encrypt vault data and save it back
                return_content.append(data)
                success.append({'item': name, 'status': 'Item created successfully.'})
            if errors:
                return_data[objname] = {"code": 400, "errors": errors, 'succeed': success}
            else:
                return_data[objname] = return_content
        return Response(return_data, status.HTTP_201_CREATED)

    def put(self, request):
        return_data = {}
        for objname, content in request.data.items():
            errors = []
            success = []
            obj = common.get_model(objname)
            return_content = []
            for each in content:
                item_id = None
                name = each['id'] if 'id' in each else None
                try:
                    if objname in models.UUID_MODELS:
                        if 'refid' not in each and 'id' in each and not check_value({'type':'uuid'}, each['id']) :
                            # remap id to refid
                            each['refid'] = each['id']
                            del each['id']
                            item_id = each['refid']
                    else:
                        item_id = id
                    robj = common.get_item(request, obj, item_id, raise_exception=False)
                    if not robj:
                        errors.append({'item': name, 'errors': 'Item not found.'})
                    serializer_class = serializers.serializer_class_lookup[objname]
                    serializer = serializer_class(robj, data=each)
                    if serializer.is_valid():
                        # payload is valid .
                        serializer.save()
                    else:
                        errors.append({'item': name, 'errors': serializer.errors})
                    # We now need to encrypt vault data and save it back
                    return_content.append(serializer.data)
                    success.append({'item': name, 'status': 'Item created successfully.'})
                except Exception as e:
                    logger.exception(e)
                    pass
                    errors.append({'item': name, 'errors': 'Invalid Request'})
            if errors:
                return_data[objname] = {"code": 400, "errors": errors, 'succeed': success}
            else:
                return_data[objname] = return_content
        return Response(return_data, status.HTTP_200_OK)

    def asset_v1_processing(self, request, data):
        """
        Special processing to merge v1 data load into v2.
        :param request:
        :param data:
        :return:
        """

        return_data = []
        for item in data:
            obj = common.get_model('products')
            serializer_class = serializers.serializer_class_lookup_read['products']
            refid = item.get('product')
            data = common.get_item(request, obj, refid)
            obj_serializer = serializer_class(data)
            asset_data = obj_serializer.data
            env_list = []
            for env in asset_data.get('environments', []):
                if 'id' in env:
                    env_list.append(env.get('id'))
            if env_list:
                for i in ["consumes", "security", "istio", "internal"]:
                    if i in item:
                        tmp_data = []
                        for each in env_list:
                            tmp_hash = {"environment": each, "entries": item[i]}
                            tmp_data.append(tmp_hash)
                        item[i] = tmp_data
            return_data.append(item)
        return return_data

@method_decorator(never_cache, name='dispatch')
class AssetEnvironmentItem(APIView):
    request_type = 'environment'
#    authentication_classes = AUTH_CLASS
#    permission_classes = PERM_CLASS

    def get(self, request, item, env=None):
        obj = common.get_model('assets')
        serializer_class = serializers.serializer_class_lookup_read['assetsEnvironments']
        data = common.get_item(request, obj, item)
        obj_serializer = serializer_class(data)
        asset_data = obj_serializer.data
        return_data = asset_data
        if not env and self.request_type == 'environment':
            # List environments
            return_data = return_data.get('environments')
            return Response(return_data)
        found = False
        for each in asset_data.get('environments'):
            if isinstance(each, dict) and each.get('id', "") == env:
                return_data = each
                found = True
                break
        if not found:
            raise ViewException(FORMAT, '{} for {} not found.'.format(env, item), 404)
        if self.request_type == 'deploymentLocation':
            loc_obj = common.get_model('locations')
            data = common.get_item(request, loc_obj, return_data.get('location', ''))
            serializer_class = serializers.serializer_class_lookup_read['locations']
            obj_serializer = serializer_class(data)
            return_data = obj_serializer.data
        elif self.request_type == 'securityConfiguration':
            aobj = common.get_model('assetsByEnvironment')
            aobj = common.get_model_all(request, 'assetsByEnvironment', aobj)
            if aobj.filter(refid=str(env), asset=asset_data['id']).exists():
                data = aobj.get(refid=str(env), asset=asset_data['id'])
            serializer_class = serializers.serializer_class_lookup_read['assetsByEnvironment']
            obj_serializer = serializer_class(data)
            asset_data = obj_serializer.data
            product_obj = common.get_model('products')
            product_data = common.get_item(request, product_obj, asset_data.get('product', ''))
            product_serializer_class = serializers.serializer_class_lookup_read['products']
            prod_serializer = product_serializer_class(product_data)
            prod_data = prod_serializer.data
            securityConfiguration = []
            if 'security' in prod_data:
                securityConfiguration.append(prod_data['security'])
            if 'security' in asset_data:
                securityConfiguration.append(asset_data['security'])
            return_data = itertools.chain.from_iterable(securityConfiguration)  #Merge list of lists into a single list
        return Response(return_data)


@method_decorator(never_cache, name='dispatch')
class AssetUrlsItem(APIView):

    #    authentication_classes = AUTH_CLASS
    #    permission_classes = PERM_CLASS

    def get(self, request, item, ):
        obj = common.get_model('assets')
        serializer_class = serializers.serializer_class_lookup_read['assetsUrls']
        data = common.get_item(request, obj, item)
        obj_serializer = serializer_class(data)
        decrypt_data = obj_serializer.data
        return_data = decrypt_data.get('urls')
        return Response(return_data)



@method_decorator(never_cache, name='dispatch')
class AssetsByEnvironmentItem(APIView):

    #    authentication_classes = AUTH_CLASS
    #    permission_classes = PERM_CLASS

    def get(self, request, item, env):

        objname = 'assetsByEnvironment'
        obj = common.get_model(objname)
        data = common.get_model_all(request, objname, obj)
        if data.filter(asset__refid=item, refid=env).exists():
            data = data.get(asset__refid=item, refid=env)
        else:
            raise ViewException(FORMAT, "No {} found.".format(objname), 404)
        serializer_class = serializers.serializer_class_lookup_read[objname]
        obj_serializer = serializer_class(data)
        return_data = obj_serializer.data
        return Response(return_data)

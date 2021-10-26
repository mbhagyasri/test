# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global LLC
# Copying or reproduction without prior written approval is prohibited. 
# Copyright (c) 2019 =================================================
import socket
from uuid import UUID
import json
import requests
import logging
import os
from django.utils.module_loading import import_string
from django.conf import settings
from requests.auth import HTTPBasicAuth
from .api_adapters import API
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from .. import models 
logger = logging.getLogger(__name__)


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


def trigger_bamboo_plan(plan_key, project_key='NGIP', stage_name='JOB1',
                        username=os.getenv('bamboo_username', ''), password=os.getenv('bamboo_password', '')):
    """
    Calling Bamboo queue job.
    :param plan_key:
    :type plan_key: str
    :param project_key:
    :type project_key: str
    :param stage_name:
    :type stage_name: str
    :param username:
    :type username: str
    :param password:
    :type password: str
    :return:
    """
    bamboo_url = 'https://bamboo.cdk.com/rest/api/latest'
    headers = {'Accept': 'application/json'}
    adapter = API(base_uri=bamboo_url, headers=headers)
    kwarg = {'auth': HTTPBasicAuth(username, password), 'raise_exception': False}
    uri = '/queue/{}-{}?{}&executeAllStages'.format(project_key, plan_key, stage_name)
    return adapter.post(url=uri, **kwarg)


def trigger_apsink():
    plan_key = 'APSINK'
    if os.getenv('environment', '') == 'us-prod':
        response = trigger_bamboo_plan(plan_key)
        if response.status_code >= 300:
            logger.exception(response.text)
    return True


def trigger_external_secrets_plan():
    plan_key = os.getenv('bamboo_resources_secret_plan', '')
    if os.getenv('environment', '') == 'us-prod':
        response = trigger_bamboo_plan(plan_key)
        if response.status_code >= 300:
            logger.exception(response.text)
    return True


def trigger_resource_plan():
    plan_key = os.getenv('bamboo_resources_plan', '')
    if os.getenv('environment', '') == 'us-prod':
        response = trigger_bamboo_plan(plan_key)
        if response.status_code >= 300:
            logger.exception(response.text)
    return True

def validateAssetId(amid):
    # gather token initially for validation request
    url = getattr(settings, "AMIDURL", DEFAULT_TIMEOUT)
    tokenurl = url + '/token' 
    logger.info('Validating asset master id : {}'.format(str(amid)))
    credentials = getattr(settings, "AMIDCREDENTIALS", DEFAULT_TIMEOUT)
    # sometimes the request comes back as a bad request (400 error code). 
    # workaround to keep retrying until status code returns 200 (successfull)
    # limit retrys to 5
    token = requests.post(tokenurl, json=credentials)
    maxretrys = 5
    retrys = 0
    while (token.status_code != 200 and retrys < maxretrys):
        token = requests.post(tokenurl, json=credentials)
        retrys += 1
    tokenjson = json.loads(token.content)
    auth = 'bearer ' + str(tokenjson["token"])
    #make validation request, we can tell if the asset is existent or not by checking length of reply body.
    requesturl = url + '/assetById?key=' + str(amid)
    valid = requests.get(requesturl, headers={'Authorization': auth})
    result  = json.loads(valid.content)
    if (result and len(result) > 0):
        return True
    else:
        return False

def validateAttaches(resourcelist):
    for i in resourcelist:
        resourcename = i['name']
        logger.info('Validating existence of resource: {}...'.format(resourcename))
        resourcecount = models.Resource.objects.filter(refid=resourcename).count()
        if resourcecount != 1:
            logger.info('Failed to validate resource: {}'.format(resourcename))
            return False
        else: 
            logger.info('Resource Validated: {}'.format(resourcename))
    return True
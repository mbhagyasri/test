# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global
# Copying or reproduction without prior written approval is prohibited.
# Copyright (c) 2021 =================================================
import os
import pydash
import yaml
import yaql
import re
import uuid
import jsonpatch
import logging

from .models import models_class_lookup
from django.forms.models import model_to_dict
from django.conf import settings
from .utils.helper_methods import check_value
from .middleware import ViewException
from django.views.decorators.cache import cache_page
from libs.utility.config_parsers import get_config

logger = logging.getLogger(__name__)
config = get_config()
FORMAT = 'json'

class CacheMixin(object):
    cache_timeout = 5

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        return cache_page(self.get_cache_timeout())(super(CacheMixin, self).dispatch)(*args, **kwargs)


class Validators(object):
    def __init__(self):
        self.mappings = self.load_mappings()
        if not self.mappings:
            raise ViewException(FORMAT, {'Validation errors': 'Failed to load api mapping configuration.'}, 400)
        self.errors = {}

    def get_associations(self, path, parentobjname):
        childobj_list = []
        pattern = path + r'/([a-zA-Z0-9_-]+)/'
        for p in self.mappings['paths']:
            if re.match(pattern, p):
                match = re.match(pattern, p)
                childobj_list.append(match[1])
        return childobj_list

    def parse_mappings(self, path, method, data, raise_exception=True):
        name = data.get('name', None)
        errors = {"name": name, "path": path}
        if path in self.mappings['paths'] and method in self.mappings['paths'][path]:
            mapping = self.mappings['paths'][path][method]
            modelname = self.mappings['paths'][path]['model']
            # validate required_inputs
            invalid_inputs = []
            missing_inputs = []
            invalid_inputs_hash = {}
            field_types_to_check = ['optional_inputs', 'required_inputs']
            # convert any uuid value to str
            for k in data:
                if isinstance(data[k], uuid.UUID):
                    data[k] = str(data[k])
            try:
                # Checking for each field type in order
                for input_type in field_types_to_check:
                    bad_fields = []
                    if input_type in mapping:
                        for parameter in mapping[input_type]:
                            mapping_param = mapping[input_type][parameter]
                            if pydash.objects.has(data, parameter) and pydash.objects.get(data, parameter):
                                check = False
                                error = None
                                current_value = pydash.objects.get(data, parameter)
                                # Foreign Keys
                                if mapping_param['type'].lower() == 'lookup_field':
                                    try:
                                        obj = models_class_lookup[mapping_param['model']]
                                        qf = re.sub(r'\.', "__", mapping_param['lookup_key'])
                                        fq = {qf: current_value}
                                        obj_data = obj.objects.filter(**fq)
                                        if obj_data.exists():
                                            obj_dict = model_to_dict(obj_data.first())
                                            source_key = 'id'
                                            if 'src_key' in mapping_param:
                                                source_key = mapping_param['src_key']
                                            value = str(pydash.objects.get(obj_dict, source_key))
                                            if 'dst_key' in mapping_param:
                                                fieldname = mapping_param['dst_key']
                                                # add the foreign key id to the data set to the field name path
                                                pydash.objects.set_(data, fieldname, value)
                                                # delete the reference item from data set
                                                if mapping_param['dst_key'] != parameter:
                                                    item_path = re.sub(r'\.', "/", parameter)
                                                    item_path = '/{}'.format(item_path)
                                                    patch = [{'op': 'remove', 'path': item_path}]
                                                    data = jsonpatch.apply_patch(data, patch=patch)
                                                    continue
                                            else:
                                                # replace value with id
                                                pydash.objects.set_(data, parameter, value)
                                            check = True
                                        elif 'ignore_failure' in mapping_param and \
                                                mapping_param['ignore_failure'] == "True":
                                            # Remove this value
                                            logger.info('Lookup value does not exist. ignore_failure is set to True.'
                                                        '  continuing')
                                            pydash.objects.unset(data, parameter)
                                            continue
                                        else:
                                            error = '%s with value %s does not exist.' % (mapping_param['model'],
                                                                                          pydash.objects.get(data,
                                                                                                             parameter))
                                            logger.error(error)
                                            if parameter in invalid_inputs_hash:
                                                continue
                                            invalid_inputs_hash[parameter] = 1
                                            bad_fields.append({parameter: error})

                                    except Exception as e:
                                        logger.error('Failed to check for foreign key relationship for %s' % parameter)
                                        logger.exception(e)
                                elif mapping_param['type'].lower() == 'related_field' \
                                        and pydash.objects.has(data, mapping_param['related_field_key']) and \
                                        pydash.objects.get(data, mapping_param['related_field_key']) in \
                                        mapping_param['set_value']:
                                    if current_value != \
                                            pydash.objects.get(data, mapping_param['set_value']
                                                               [pydash.objects.get(data,
                                                                                mapping_param['related_field_key'])]):
                                        # setting the values to be the related key value mapping under set_value set

                                        pydash.objects.set_(data, parameter, mapping_param['set_value']
                                                            [pydash.objects.get(data,
                                                                                mapping_param['related_field_key'])])
                                        check = True
                                elif mapping_param['type'].lower() == 'unique':
                                    obj = models_class_lookup[modelname]
                                    qf = re.sub(r'\.', "__", parameter)
                                    fq = {qf: pydash.objects.get(data, parameter)}
                                    obj_data = obj.objects.filter(**fq)
                                    if obj_data.exists():
                                        error = 'value for {} is not unique.'.format(parameter)
                                        if parameter in invalid_inputs_hash:
                                            continue
                                        invalid_inputs_hash[parameter] = 1
                                        bad_fields.append({parameter: error})
                                    else:
                                         check = True
                                elif mapping_param['type'].lower() == 'array' and pydash.objects.has(data, parameter):
                                    if isinstance(current_value, list):
                                        check = True
                                    elif isinstance(current_value, str):
                                        # remove original entry
                                        pydash.objects.unset(data, parameter)
                                        value_list = current_value.split(',')
                                        value_list = [v.strip() for v in value_list]
                                        # set the new value list
                                        pydash.objects.set_(data, parameter, value_list)
                                        check = True
                                else:
                                    check = check_value(mapping_param, current_value)
                                # check uniqueness
                                if 'unique' in mapping_param:
                                    obj = models_class_lookup[mapping_param['model']]
                                if not check:
                                    if parameter in invalid_inputs_hash:
                                        continue
                                    logger.error('Failed checking for parameter {} for item {} against {} with value.'
                                                 ' '.format(parameter, name, path, current_value))
                                    invalid_inputs_hash[parameter] = 1
                                    if error:
                                        bad_fields.append({parameter: error})

                                    else:
                                        bad_fields.append({parameter: 'Expect field to be type %s' %
                                                                      mapping_param['type']})
                            elif mapping_param['type'].lower() == 'related_field' \
                                    and pydash.objects.has(data, mapping_param['related_field_key']):
                                if pydash.objects.get(data, mapping_param['related_field_key']) in \
                                        mapping_param['set_value']:
                                    # setting the value to be the related key value mapping under set_value set
                                    value = mapping_param['set_value'][pydash.objects.get(data,
                                                                                mapping_param['related_field_key'])]

                                else:
                                    # setting the value to be the same value from the related key
                                    value = pydash.objects.get(data, mapping_param['related_field_key'])
                                pydash.objects.set_(data, parameter, value)
                            elif 'default' in mapping_param:
                                pydash.objects.set_(data, parameter, mapping_param['default'])
                            elif input_type == 'required_inputs':

                                missing_inputs.append(parameter)
                    if bad_fields:
                        invalid_inputs.append({input_type: bad_fields})
                if missing_inputs:
                    self.errors["Missing Required Fields"] = missing_inputs
                if invalid_inputs:
                    self.errors["Invalid Fields"] = invalid_inputs
                if self.errors:
                    errors["Validation Errors"] = self.errors
                    logger.error(errors)
                    if raise_exception:
                        ViewException(FORMAT, errors, 400)
                    else:
                        return errors
            except Exception as e:
                logger.exception(e)
                if raise_exception:
                    ViewException(FORMAT, str(e), 400)
            return data

        else:
            logger.error('path %s not valid.' % path)
            errors["Validation Errors"] = "Method is not supported."
            if raise_exception:
                ViewException(FORMAT, errors, 405)
            else:
                return errors

    def load_mappings(self):
        data = {}
        mapping_dir = os.path.join(settings.PROJECT_DIR, config.get('global', 'mapping_dir'))
        for filename in os.listdir(mapping_dir):
            content = {}
            logger.debug('Reading %s' % filename)
            try:
                with open(os.path.join(mapping_dir, filename)) as f:
                    content = yaml.safe_load(f)
            except Exception as e:
                logger.error("Failed to read file %s" % filename)
                logger.exception(e)
                pass
            if content:
                if data:
                    data['paths'].update(content['paths'])
                else:
                    data.update(content)
        return data


class YaqlReplacement(dict):

    def process_data(self, data):
        pass

    def yaql_replace(data, expression_key):
        engine = yaql.factory.YaqlFactory().create()
        expression = engine(expression_key)
        try:
            value = expression.evaluate(data=data)
            return value
        except Exception as e:
            logger.exception(e)
            return False



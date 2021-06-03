# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global
# Copying or reproduction without prior written approval is prohibited.
# Copyright (c) 2021 =================================================

import yaql
import logging
from django.views.decorators.cache import cache_page


logger = logging.getLogger(__name__)
FORMAT = 'json'


class CacheMixin(object):
    cache_timeout = 5

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        return cache_page(self.get_cache_timeout())(super(CacheMixin, self).dispatch)(*args, **kwargs)


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



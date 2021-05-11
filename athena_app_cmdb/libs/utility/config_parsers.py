# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global LLC
# Copying or reproduction without prior written approval is prohibited. 
# Copyright (c) 2021 =================================================

import configparser

from django.conf import settings
import os

class APPConfigParser(object):
    def __init__(self):
        self._cf = configparser.RawConfigParser()
        self._cf.read(os.path.normpath(os.path.join(settings.PROJECT_DIR, '../etc/config.conf')))

    def get_config(self):
        return self._cf

_api_config_parser = APPConfigParser()


def get_config():
    return _api_config_parser.get_config()


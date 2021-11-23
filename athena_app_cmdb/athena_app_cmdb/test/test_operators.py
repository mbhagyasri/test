from django.test import TestCase
from django.views.decorators import cache
from athena_app_cmdb import common
from athena_app_cmdb.operators import Validators, CacheMixin, YaqlReplacement
from django.views.decorators.cache import cache_page
from unittest import mock
from libs.utility.commands import Execute
from libs.utility.config_parsers import get_config

EXE = Execute()

class CacheMixinTestCases(TestCase):

  def setUp(self) -> None:
    return super().setUp()

  def test_get_cache_timeout(self):
    cache = CacheMixin()
    cache_timeout = cache.get_cache_timeout()
    self.assertEqual(cache_timeout, 5)


class YaqlReplacementTestCases(TestCase):
  
  def setUp(self) -> None:
    return super().setUp()

  def test_process_data(self):
    data = YaqlReplacement().process_data('testdata')
    self.assertEqual(data, None)

  def test_yaql_replace(self):
    data = YaqlReplacement().yaql_replace('key')
    self.assertEqual(data, 'key')
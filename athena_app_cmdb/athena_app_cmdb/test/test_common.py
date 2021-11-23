from django.test import TestCase
from django.test.client import RequestFactory
from athena_app_cmdb import common
from athena_app_cmdb.middleware.view_error import ViewException
from athena_app_cmdb.models import Team
from rest_framework.test import APIRequestFactory

class CommonTestCase(TestCase):

  def setUp(self) -> None:
    
    Team.objects.create(refid='test_team_id', name='team-test', properties='{"ad-group":["test group"]}')
    return super().setUp()

  def test_get_model(self):
    model = common.get_model('teams')
    self.assertEqual(model.__name__, 'Team')
    
    with self.assertRaises(ViewException):
      common.get_model('notfound')
    
    model = common.get_model('notfound', False)
    self.assertEqual(model, None)

  def test_get_model_all(self):
    objname     = 'teams'
    get_request = RequestFactory().get('/'+objname)
    obj         = common.get_model(objname)
    all_models  = common.get_model_all(get_request, objname, obj)
    self.assertEqual(all_models[0].refid, 'test_team_id')

    all_models  = common.get_model_all(get_request, 'tasks', obj)
    self.assertEqual(all_models[0].refid, 'test_team_id')

  def test_get_item(self):
    request = RequestFactory().get('/teams')
    obj     = common.get_model('teams')
    item    = common.get_item(request, obj, 'test_team_id')
    self.assertEqual(item.refid, 'test_team_id')

    with self.assertRaises(ViewException):
      common.get_item(request, obj, 'test_team_id1', True)

  def test_filter_get_request(self):
    request = APIRequestFactory().get('/teams', {'page_size': 2000, 'name': 'team-test'})
    request.query_params = ['page_size', 'name']
    obj     = common.get_model('teams')
    obj     = common.get_model_all(request, 'teams', obj)
    
    data, page_size = common.filter_get_request(request, obj, 2000)
    self.assertEqual(page_size, '2000')
    self.assertEqual(data[0].refid, 'test_team_id')

    # exlude keyword in query_string
    request = APIRequestFactory().get('/teams', {'page_size': 2000, 'name': 'test', 'exclude': {'deleted':'False'}})
    request.query_params = ['page_size', 'name', 'exclude']
    obj     = common.get_model('teams')
    obj     = common.get_model_all(request, 'teams', obj)
    data, page_size = common.filter_get_request(request, obj, 2000)
    self.assertEqual(page_size, '2000')
    self.assertEquals(len(data), 0)

  def test_common_item_processing(self):
    params  = {'id': 'team_id', 'name': 'team_test_name', 'email': ['user@example.com'], 'description': 'test description', 'notification': [{'email': 'test@example.com'}], 'ad-group': ['test ad group']}
    request = APIRequestFactory().post('/teams')

    # If the data is invalid then the process would return False with exception
    item = common.common_item_processing(request, 'teams', params, 'post')
    self.assertFalse(item[0])
    self.assertIn("Failed validating 'pattern' in schema['properties']['id']", item[2]['errors'])

    # # If the data is valid then process the item
    params['id']    = 'team-id'
    params['name']  = 'team-name'
    item            = common.common_item_processing(request, 'teams', params, 'post')
    self.assertTrue(item[0])
    self.assertEqual(item[1]['id'], 'team-id')

    # If the method is not post then return the data
    params  = {'id': 'team-abc', 'name': 'team-abc', 'email': ['user@example.com'], 'description': 'test description', 'notification': [{'email': 'test@example.com'}], 'ad-group': ['test ad group']}
    item    = common.common_item_processing(request, 'teams', params, 'get')
    self.assertFalse(item[0])
    self.assertEqual(item[2]['errors'], 'Item team-abc not found.')

  def test_process_product(self):
    params  = {'id': 'product-id', 'name': 'product-name', 'environments':[{'id': 'us-dev', 'type': 'dev', 'prefix': 'dev', 'location': 'location-us-dev'}], 'external-ids': {'iqr_product_id': 1234}, 'bamboo-projects': [{'id': 'EXAMPLE'}]}
    request = APIRequestFactory().post('/teams')
    products = common.process_product(request, params, 'post')
    
    self.assertFalse(products[0])
    self.assertIn("'security' is a required property", products[2]['errors'])
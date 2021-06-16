# Copyright Notice ===================================================
# This file contains proprietary information of CDK Global
# Copying or reproduction without prior written approval is prohibited. 
# Copyright (c) 2021 =================================================

import requests
import logging
# noinspection PyUnresolvedReferences
from athena_app_cmdb.middleware import ViewException

logger = logging.getLogger(__name__)
FORMAT = 'json'

class API(object):

    def __init__(self, base_uri, verify=True, timeout=30, proxies=None, session=None, headers=None):
        """Create a new request adapter instance.
        :param base_uri: Base URL for the Vault instance being addressed.
        :type base_uri: str
        :param verify: Either a boolean to indicate whether TLS verification should be performed when sending requests to Vault,
            or a string pointing at the CA bundle to use for verification. See http://docs.python-requests.org/en/master/user/advanced/#ssl-cert-verification.
        :type verify: Union[bool,str]
        :param timeout: The timeout value for requests sent to Vault.
        :type timeout: int
        :param proxies: Proxies to use when preforming requests.
            See: http://docs.python-requests.org/en/master/user/advanced/#proxies
        :type proxies: dict
        :param session: Optional session object to use when performing request.
        :type session: request.Session
        :param headers: Optional headers object to use when performing requeset.
        :type headers: dict
        """
        if not session:
            session = requests.Session()
        self.session = session
        self.base_uri = base_uri
        self.headers = headers
        self._kwargs = {
            'verify': verify,
            'timeout': timeout,
            'proxies': proxies,
        }

    @staticmethod
    def urljoin(*args):
        """Joins given arguments into a url. Trailing and leading slashes are stripped for each argument.
        :param args: Multiple parts of a URL to be combined into one string.
        :type args: str | unicode
        :return: Full URL combining all provided arguments
        :rtype: str | unicode
        """

        return '/'.join(map(lambda x: str(x).strip('/'), args))

    def close(self):
        """Close the underlying Requests session.
        """
        self.session.close()

    def get(self, url, **kwargs):
        """Performs a GET request.
        :param url: Partial URL path to send the request to. This will be joined to the end of the instance's base_uri
            attribute.
        :type url: str | unicode
        :param kwargs: Additional keyword arguments to include in the requests call.
        :type kwargs: dict
        :return: The response of the request.
        :rtype: requests.Response
        """
        return self.request('get', url, **kwargs)

    def post(self, url, **kwargs):
        """Performs a POST request.
        :param url: Partial URL path to send the request to. This will be joined to the end of the instance's base_uri
            attribute.
        :type url: str | unicode
        :param kwargs: Additional keyword arguments to include in the requests call.
        :type kwargs: dict
        :return: The response of the request.
        :rtype: requests.Response
        """
        return self.request('post', url, **kwargs)

    def put(self, url, **kwargs):
        """Performs a PUT request.
        :param url: Partial URL path to send the request to. This will be joined to the end of the instance's base_uri
            attribute.
        :type url: str | unicode
        :param kwargs: Additional keyword arguments to include in the requests call.
        :type kwargs: dict
        :return: The response of the request.
        :rtype: requests.Response
        """
        return self.request('put', url, **kwargs)

    def delete(self, url, **kwargs):
        """Performs a DELETE request.
        :param url: Partial URL path to send the request to. This will be joined to the end of the instance's base_uri
            attribute.
        :type url: str | unicode
        :param kwargs: Additional keyword arguments to include in the requests call.
        :type kwargs: dict
        :return: The response of the request.
        :rtype: requests.Response
        """
        return self.request('delete', url, **kwargs)

    def list(self, url, **kwargs):
        """Performs a LIST request.
        :param url: Partial URL path to send the request to. This will be joined to the end of the instance's base_uri
            attribute.
        :type url: str | unicode
        :param kwargs: Additional keyword arguments to include in the requests call.
        :type kwargs: dict
        :return: The response of the request.
        :rtype: requests.Response
        """
        return self.request('list', url, **kwargs)

    def head(self, url, **kwargs):
        """Performs a HEAD request.
        :param url: Partial URL path to send the request to. This will be joined to the end of the instance's base_uri
            attribute.
        :type url: str | unicode
        :param kwargs: Additional keyword arguments to include in the requests call.
        :type kwargs: dict
        :return: The response of the request.
        :rtype: requests.Response
        """
        return self.request('head', url, **kwargs)

    def request(self, method, url, headers=None, raise_exception=True, **kwargs):
        """Main method for routing HTTP requests to the configured Vault base_uri. Intended to be implement by subclasses.
        :param method: HTTP method to use with the request. E.g., GET, POST, etc.
        :type method: str
        :param url: Partial URL path to send the request to. This will be joined to the end of the instance's base_uri
            attribute.
        :type url: str | unicode
        :param headers: Additional headers to include with the request.
        :type headers: dict
        :param kwargs: Additional keyword arguments to include in the requests call.
        :type kwargs: dict
        :param raise_exception: If True, raise an exception via utils.raise_for_error(). Set this parameter to False to
            bypass this functionality.
        :type raise_exception: bool
        :return: The response of the request.
        :rtype: requests.Response
        """
        if '//' in url:
            # Vault CLI treats a double forward slash ('//') as a single forward slash for a given path.
            # To avoid issues with the requests module's redirection logic, we perform the same translation here.
            url = url.replace('//', '/')

        url = self.urljoin(self.base_uri, url)

        xheaders = self.headers.copy()
        if headers:
            xheaders.update(headers)
        _kwargs = self._kwargs.copy()
        _kwargs.update(kwargs)

        response = self.session.request(
            method=method,
            url=url,
            headers=xheaders,
            **_kwargs
        )

        if raise_exception and 400 <= response.status_code < 600:
            text = errors = None
            if response.headers.get('Content-Type') == 'application/json':
                errors = response.json().get('errors')
            if errors is None:
                errors = response.text
            raise ViewException(FORMAT, errors, response.status_code)

        return response

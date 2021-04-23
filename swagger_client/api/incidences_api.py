# coding: utf-8

"""
    Kantonsservice GR

    Canton Service GR  # noqa: E501

    OpenAPI spec version: 1.0.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

import re  # noqa: F401

# python 2 and python 3 compatibility library
import six

from swagger_client.api_client import ApiClient


class IncidencesApi(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    Ref: https://github.com/swagger-api/swagger-codegen
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def incidences_bfs_nr_get(self, bfs_nr, **kwargs):  # noqa: E501
        """Liefert die Inzidenz für eine spezifische Gemeinde  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.incidences_bfs_nr_get(bfs_nr, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param int bfs_nr: bfsNr (required)
        :param str date_from: dateFrom - Startdatum inklusive. Falls nicht definiert, alle Datensätze seit Beginn
        :param str date_to: dateTo - Enddatum inklusive. Falls nicht definiert, alle Datensätze bis heute
        :return: list[Incidence]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.incidences_bfs_nr_get_with_http_info(bfs_nr, **kwargs)  # noqa: E501
        else:
            (data) = self.incidences_bfs_nr_get_with_http_info(bfs_nr, **kwargs)  # noqa: E501
            return data

    def incidences_bfs_nr_get_with_http_info(self, bfs_nr, **kwargs):  # noqa: E501
        """Liefert die Inzidenz für eine spezifische Gemeinde  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.incidences_bfs_nr_get_with_http_info(bfs_nr, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param int bfs_nr: bfsNr (required)
        :param str date_from: dateFrom - Startdatum inklusive. Falls nicht definiert, alle Datensätze seit Beginn
        :param str date_to: dateTo - Enddatum inklusive. Falls nicht definiert, alle Datensätze bis heute
        :return: list[Incidence]
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['bfs_nr', 'date_from', 'date_to']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method incidences_bfs_nr_get" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'bfs_nr' is set
        if self.api_client.client_side_validation and ('bfs_nr' not in params or
                                                       params['bfs_nr'] is None):  # noqa: E501
            raise ValueError("Missing the required parameter `bfs_nr` when calling `incidences_bfs_nr_get`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'bfs_nr' in params:
            path_params['bfsNr'] = params['bfs_nr']  # noqa: E501

        query_params = []
        if 'date_from' in params:
            query_params.append(('dateFrom', params['date_from']))  # noqa: E501
        if 'date_to' in params:
            query_params.append(('dateTo', params['date_to']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/incidences/{bfsNr}/', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='list[Incidence]',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def incidences_get(self, **kwargs):  # noqa: E501
        """Liefert alle vorhandenen Datensätze aller Gemeinden  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.incidences_get(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str date_from: dateFrom - Startdatum inklusive. Falls nicht definiert, alle Datensätze seit Beginn
        :param str date_to: dateTo - Enddatum inklusive. Falls nicht definiert, alle Datensätze bis heute
        :return: list[Incidence]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.incidences_get_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.incidences_get_with_http_info(**kwargs)  # noqa: E501
            return data

    def incidences_get_with_http_info(self, **kwargs):  # noqa: E501
        """Liefert alle vorhandenen Datensätze aller Gemeinden  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.incidences_get_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str date_from: dateFrom - Startdatum inklusive. Falls nicht definiert, alle Datensätze seit Beginn
        :param str date_to: dateTo - Enddatum inklusive. Falls nicht definiert, alle Datensätze bis heute
        :return: list[Incidence]
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['date_from', 'date_to']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method incidences_get" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'date_from' in params:
            query_params.append(('dateFrom', params['date_from']))  # noqa: E501
        if 'date_to' in params:
            query_params.append(('dateTo', params['date_to']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/incidences/', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='list[Incidence]',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)
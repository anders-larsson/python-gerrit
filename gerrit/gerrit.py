"""
Gerrit
======

Set up connection to gerrit
"""

import requests
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth
from requests.utils import get_netrc_auth

from gerrit.changes.revision import Revision
from gerrit.error import (
    CredentialsNotFound,
    UnhandledError,
    AlreadyExists,
)
from gerrit.projects.project import Project
from gerrit.groups.group import Group


class Gerrit(object):
    """Set up connection to gerrit"""

    def __init__(self, url, auth_type=None, **kwargs):
        """
        :param url: URL to the gerrit server
        :type url: str
        :param auth_type: Authentication method preferred
        :type auth_type: str
        """

        # HTTP REST API HEADERS
        self._requests_headers = {
            'content-type': 'application/json',
        }

        self._url = url.rstrip('/')

        self._auth = None

        if auth_type:
            if auth_type == 'http':
                self._http_auth(**kwargs)
            else:
                raise NotImplementedError(
                    "Authorization type '%s' is not implemented" %
                    auth_type)
        else:
            self._http_auth(**kwargs)

    def _netrc_auth(self):
        if get_netrc_auth(self._url):
            netrc_id, netrc_pw = get_netrc_auth(self._url)
        else:
            raise CredentialsNotFound(
                "No Credentials for %s found in .netrc" %
                self._url)
        return netrc_id, netrc_pw

    def _http_auth(self, **kwargs):
        # Assume netrc file if no auth_id or auth_pw was given.
        if 'auth_id' in kwargs and 'auth_pw' in kwargs:
            auth_id = kwargs['auth_id']
            auth_pw = kwargs['auth_pw']
        elif 'auth_id' not in kwargs and 'auth_pw' not in kwargs:
            auth_id, auth_pw = self._netrc_auth()
        else:
            raise CredentialsNotFound(
                'Supply both auth_id and auth_pw or neither')

        if 'auth_method' not in kwargs:
            self._http_basic_auth(auth_id, auth_pw)
        elif kwargs['auth_method'] == 'basic':
            self._http_basic_auth(auth_id, auth_pw)
        elif kwargs['auth_method'] == 'digest':
            self._http_digest_auth(auth_id, auth_pw)
        else:
            raise NotImplementedError(
                "Authorization method '%s' for auth_type 'http' is not implemented" %
                kwargs['auth_method'])

    def _http_basic_auth(self, auth_id, auth_pw):
        # We got everything as we expected, create the HTTPBasicAuth object.
        self._auth = HTTPBasicAuth(auth_id, auth_pw)

    def _http_digest_auth(self, auth_id, auth_pw):
        # We got everything as we expected, create the HTTPDigestAuth object.
        self._auth = HTTPDigestAuth(auth_id, auth_pw)

    def call(self, request='get', r_endpoint=None, r_payload=None, r_headers=None):
        """
        Send request to gerrit.
        :param request: The type of http request to perform
        :type request: str
        :param r_endpoint: The gerrit REST API endpoint to hit
        :type r_endpoint: str
        :param r_payload: The data to send to the specified API endpoint
        :type r_payload: dict

        :return: The http request
        :rtype: requests.packages.urllib3.response.HTTPResponse
        """

        if r_headers is None:
            r_headers = self._requests_headers

        request_do = {
            'get': requests.get,
            'put': requests.put,
            'post': requests.post,
            'delete': requests.delete
        }
        req = request_do[request](
            url=self._url + r_endpoint,
            auth=self._auth,
            headers=r_headers,
            json=r_payload
        )
        return req

    def get_revision(self, change_id, revision_id=None):
        """
        Get a revision
        :param change_id: The Change-Id to fetch from gerrit
        :type change_id: str
        :param revision_id: The optional patch set for the change
        :type revision_id: str

        :return: Review object
        :rtype: gerrit.changes.Revision
        """

        return Revision(self, change_id, revision_id)

    def create_project(self, name, options=None):
        """
        Create a project
        :param name: Name of the project
        :type name: str
        :param options: Additional options
        :type options: dict

        :return: Project if successful
        :rtype: gerrit.projects.Project
        :exception: AlreadyExists, UnhandledError
        """

        r_endpoint = "/a/projects/%s" % name

        if options is None:
            options = {}

        req = self.call(
            request='put',
            r_endpoint=r_endpoint,
            r_payload=options,
        )

        result = req.content.decode('utf-8')

        if req.status_code == 201:
            return self.get_project(name)
        elif req.status_code == 409:
            raise AlreadyExists(result)
        else:
            raise UnhandledError(result)

    def get_project(self, name):
        """
        Get a project
        :param name: Project name to get
        :type name: str

        :return: Project object
        :rtype: gerrit.projects.Project
        """

        return Project(self, name)

    def create_group(self, name, options=None):
        """
        Create a group
        :param name: Name of the group
        :type name: str
        :param options: Additonal options
        :type options: dict

        :return: Group object if successful
        :rtype gerrit.Group
        :exception: AlreadyExists, UnhandledError
        """

        return Groups.create_group(self, name, options)

    def get_group(self, name):
        """
        Get a group
        :param name: Group name to get
        :type name: str

        :return Group object if successful
        :rtype gerrit.Group
        :exception
        """

        return Groups(self, name)

#    def has_include_group(self, group_name, included_group):
#        """
#        Check if included_group is included in group
#        :param group_name: name of group to check for member
#        :type group_name: str
#        :param included_group: name of group to find
#        :type included_group: str
#        """
#        group_data = self.get_group(group_name, ['id'])
#        if not group_data:
#            return None
#
#        group_id = group_data.get('id')
#        included_group_encode = urllib.parse.quote_plus(included_group)
#
#        r_endpoint = '/a/groups/%s/groups/%s' % (
#            group_id, included_group_encode)
#
#        req = self._gerrit_con.call(request='get',
#                                    r_endpoint=r_endpoint,
#                                   )
#
#        status_code = req.status_code
#        result = req.content.decode('utf-8')
#
#        if status_code == 404:
#            return False
#        elif status_code != 200:
#            raise UnhandledError(result)
#
#        return True

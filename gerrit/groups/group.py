"""
Group
======

Manage gerrit group endpoint
"""

from gerrit.error import (
    AlreadyExists,
    UnhandledError,
)

from gerrit.helper import decode_json


class Group(object):
    """Manage gerrit groups"""

    def __init__(self, gerrit_con, name):
        """
        :param gerrit_con: The connection object to gerrit
        :type gerrit_con: gerrit.Connection
        :param name: Group name
        :type name: str
        """

        if not name:
            raise KeyError('Group name Required')

        self._gerrit_con = gerrit_con

    def list_groups(self):
        """
        Get all visible groups
        """
        r_endpoint = '/a/groups/'

        req = self._gerrit_con.call(request='get',
                                    r_endpoint=r_endpoint,
                                    )

        status_code = req.status_code
        result = req.content.decode('utf-8')

        if status_code == 404:
            raise ValueError(result)
        elif status_code != 200:
            raise UnhandledError(result)

        json_result = decode_json(result)

        return json_result

    def get_group(self, group_name, fields=None):
        """
        Get all or specific fields for a group
        :param group_name: name of group
        :type group_name: str
        :param fields: fields to return
        :type group_name: list
        """
        groups = self.list_groups()

        group_data = groups.get(group_name, None)
        if not group_data:
            return None

        if fields is None:
            group_info = group_data
        elif fields and isinstance(fields, list):
            group_info = dict()
            for field in fields:
                group_info[field] = group_data[field]
        else:
            return None

        return group_info

    def create_group(self, group_name, options=None):
        """
        Create a group
        :param group_name: name of the group (not encoded)
        :type group_name: str
        :param options: Additional options (optional)
        :type description: dict
        """

        if not group_name:
            raise KeyError('Group name required')

        r_endpoint = "/a/groups/%s" % group_name

        if options is None:
            options = dict()

        req = self._gerrit_con.call(
            requests='put',
            r_endpoint=r_endpoint,
            r_payload=options,
        )

        result = req.content.decode('utf-8')

        if req.status_code == 201:
            return self.get_group(group_name)
        elif req.status_code == 409:
            raise AlreadyExists(result)
        else:
            raise UnhandledError(result)

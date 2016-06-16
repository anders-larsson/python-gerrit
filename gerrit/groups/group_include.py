    def list_included_groups(self, group_name):
        """
        Get all included group of a group
        :param group_name: name of group
        :type group_name: str
        """
        group_data = self.get_group(group_name, ['id'])
        if not group_data:
            return None

        group_id = group_data.get('id')

        r_endpoint = '/a/groups/%s/groups/' % group_id

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

    def include_groups(self, group_name, include_groups=None):
        """
        Add group as an included group
        :param group_name: name of group to add group to
        :type group_name: str
        :param include_group: groups to be added
        :type include_groups: list
        """
        if not include_groups or not isinstance(include_groups, list):
            return False

        group_name_encode = urllib.parse.quote_plus(group_name)

        r_endpoint = '/a/groups/%s/groups' % group_name_encode

        r_payload = dict()
        r_payload['groups'] = include_groups

        req = self._gerrit_con.call(request='post',
                                    r_endpoint=r_endpoint,
                                    r_payload=r_payload,
                                   )

        status_code = req.status_code
        result = req.content.decode('utf-8')

        if status_code == 201:
            return True
        elif status_code == 200:
            return True
        else:
            raise UnhandledError(result)



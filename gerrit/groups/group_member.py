    def list_group_members(self, group_name):
        """
        Get all members of a group
        :param group_name: name of group
        :type group_name: str
        """
        group_data = self.get_group(group_name, ['id'])
        if not group_data:
            return None

        group_id = group_data.get('id')

        r_endpoint = '/a/groups/%s/members/' % group_id

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



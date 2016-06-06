USERS = {'sample': 'sample',
         '100331437297045048506': '100331437297045048506'}
GROUPS = {'sample': ['group:sample'],
        '100331437297045048506': ['group:100331437297045048506'],
        }


def groupfinder(userid, request):
    if userid in USERS:
        return GROUPS.get(userid, [])

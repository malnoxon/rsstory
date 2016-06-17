from pyramid.security import Allow, Everyone, Deny


class Root(object):
    __acl__ = [(Allow, Everyone, 'public'),
            (Allow, 'group:logged_in', 'logged_in')]

    def __init__(self, request):
        pass

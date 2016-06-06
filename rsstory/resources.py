from pyramid.security import Allow, Everyone, Deny


class Root(object):
    __acl__ = [(Allow, Everyone, 'public'),
            (Allow, 'group:100331437297045048506', 'edit')]

    def __init__(self, request):
        pass

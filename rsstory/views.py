import rsstory.rss as rss
from pyramid.response import Response
from pyramid.view import view_config


# First view, available at http://localhost:6543/
@view_config(route_name='home', renderer='index.pt')
def home(request):
    return {}

@view_config(route_name='feed', renderer='json')
def feed(request):
    if request.json_body['url'] == '':
        return {"rss": "Error"}
    s = rss.archive_to_rss(request.json_body['url'])
    return {"rss": "/static/feeds/" + s + ".xml"}

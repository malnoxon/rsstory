import rsstory.rss as rss
from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name='home', renderer='index.pt')
def home(request):
    return {}

@view_config(route_name='feed', renderer='json')
def feed(request):
    if request.json_body['url'] == '':
        return {"rss": "Error"}
    s = rss.archive_to_rss(request.json_body['url'], request.json_body['time'], request.json_body['title'])
    return {"rss": "/static/feeds/" + s + ".xml"}

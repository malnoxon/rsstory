import rsstory.rss as rss
from pyramid.response import Response
from pyramid.view import view_config
import logging

log = logging.getLogger(__name__)

@view_config(route_name='home', renderer='index.pt')
def home(request):
    return {}

@view_config(route_name='feed', renderer='json')
def feed(request):
    if request.json_body['url'] == '':
        return {"rss": "Error"}
    xml_feed, preview_page = rss.archive_to_rss(request.json_body['url'], request.json_body['time'], request.json_body['title'], request.json_body['captcha'], request.remote_addr)
    return {"rss": "/static/feeds/" + xml_feed + ".xml", "preview": "/static/previews/" + preview_page}

@view_config(route_name='archive_fails', renderer='archive_fails.pt')
def archive_fails(request):
    # rss.report_archive_fail(request.json_body['url'], request.json_body['comments'])
    return {}
    # return {"success": True}

@view_config(route_name='report_archive_fails', renderer='json')
def report_archive_fails(request):
    if rss.report_archive_fail(request.json_body['url'], request.json_body['comments'], request.remote_addr, request.json_body['captcha']):
        return {"success": True}
    else:
        return {"rss": "Error"}

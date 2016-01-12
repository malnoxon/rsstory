import rsstory.rss as rss
from pyramid.response import Response
from pyramid.view import view_config
import logging

#####################
# import cgi
# import re
# from docutils.core import publish_parts
#
# from pyramid.httpexceptions import (
#         HTTPFound,
#         HTTPNotFound,
#         )
##############################

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Feed,
    )

#####################
# regular expression used to find WikiWords
# wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")
#
# @view_config(route_name='view_wiki')
# def view_wiki(request):
#     return HTTPFound(location = request.route_url('view_page',
#                                                   pagename='FrontFeed'))
#
# @view_config(route_name='view_page')
# def view_page(request):
#     pagename = request.matchdict['pagename']
#     page = DBSession.query(Feed).filter_by(name=pagename).first()
#     if page is None:
#         return HTTPNotFound('No such page')
#
#     def check(match):
#         word = match.group(1)
#         exists = DBSession.query(Feed).filter_by(name=word).all()
#         if exists:
#             view_url = request.route_url('view_page', pagename=word)
#             return '<a href="%s">%s</a>' % (view_url, cgi.escape(word))
#         else:
#             add_url = request.route_url('add_page', pagename=word)
#             return '<a href="%s">%s</a>' % (add_url, cgi.escape(word))
#
#     content = publish_parts(page.data, writer_name='html')['html_body']
#     content = wikiwords.sub(check, content)
#     edit_url = request.route_url('edit_page', pagename=pagename)
#     return dict(page=page, content=content, edit_url=edit_url)
#
# @view_config(route_name='add_page')
# def add_page(request):
#     pagename = request.matchdict['pagename']
#     if 'form.submitted' in request.params:
#         body = request.params['body']
#         page = Feed(name=pagename, data=body)
#         DBSession.add(page)
#         return HTTPFound(location = request.route_url('view_page',
#                                                       pagename=pagename))
#     save_url = request.route_url('add_page', pagename=pagename)
#     page = Feed(name='', data='')
#     return dict(page=page, save_url=save_url)
#
# @view_config(route_name='edit_page')
# def edit_page(request):
#     pagename = request.matchdict['pagename']
#     page = DBSession.query(Feed).filter_by(name=pagename).one()
#     if 'form.submitted' in request.params:
#         page.data = request.params['body']
#         DBSession.add(page)
#         return HTTPFound(location = request.route_url('view_page',
#                                                       pagename=pagename))
#     return dict(
#         page=page,
#         save_url = request.route_url('edit_page', pagename=pagename),
#         )

@view_config(route_name='home', renderer='index.pt')
def home(request):
    return {}

@view_config(route_name='feed', renderer='json')
def feed(request):
    if request.json_body['url'] == '':
        return {"rss": "Error"}
    xml_feed, preview_page, invalid_input = rss.archive_to_rss(request.json_body['url'], request.json_body['time'], request.json_body['title'], request.json_body['captcha'], request.remote_addr)
    if invalid_input:
        return {"rss": "Error", "error_msg": "Error: A bad input value was entered. Be sure that the archive url is correct and that the time between posts is entered as a whole number of days (not as a decimal). If the values are actually correct, please leave a bug report at https://github.com/Daphron/rsstory"}
    if xml_feed == False and preview_page == False:
        return {"rss": "Unknown Error"}
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

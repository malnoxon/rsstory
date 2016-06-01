import rsstory.rss as rss
from pyramid.response import Response
from pyramid.view import view_config
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from authomatic import Authomatic
from authomatic.adapters import WebObAdapter

import logging
import os
import binascii
import random
import string

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

from config import CONFIG

authomatic = Authomatic(config=CONFIG, secret=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(4096)))

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

@view_config(route_name='login_page', renderer='index.pt')
def login_page(request):
    return Response('''
        Login with <a href="login/google">Google</a>.<br />
        Unsupported: <form action="login/oi">
            <input type="text" name="id" value="me.yahoo.com" />
            <input type="submit" value="Authenticate With OpenID">
        </form>
    ''')


@view_config(route_name='login', renderer='index.pt')
def login(request):
    # Useful:
    # https://peterhudec.github.io/authomatic/examples/pyramid-simple.html
    response = Response()
    provider_name = request.matchdict.get('provider_name')
    result = authomatic.login(WebObAdapter(request, response), provider_name)
    
    # Do not write anything to the response if there is no result!
    if result:
        # If there is result, the login procedure is over and we can write to response.
        response.write('<a href="..">Home</a>')
        # from pprint import pprint
        # pprint (vars(your_object))
        
        if result.error:
            import pdb; pdb.set_trace();
            response.write(u'<h2>ERROR in login: {0}</h2>'.format(result.error.message))
        
        elif result.user:
            # OAuth 2.0 and OAuth 1.0a provide only limited user data on login,
            # We need to update the user to get more info.
            if not (result.user.name and result.user.id):
                result.user.update()
            
            response.write(u'<h1>Hi {0}</h1>'.format(result.user.name))
            response.write(u'<h2>Your id is: {0}</h2>'.format(result.user.id))
            response.write(u'<h2>Your email is: {0}</h2>'.format(result.user.email))

    return response

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

import rsstory.rss as rss
import rsstory.user
from pyramid.response import Response
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from authomatic import Authomatic
from authomatic.adapters import WebObAdapter

import logging
import os
import binascii
import random
import string
import transaction
import datetime

from pyramid.httpexceptions import (
        HTTPFound,
        HTTPNotFound,
        )

from pyramid.security import (
        remember,
        forget,
        )

from pyramid.view import (
        view_config,
        view_defaults,
        forbidden_view_config,
        )

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Feed,
    User,
    Page,
    )

from config import CONFIG

log = logging.getLogger(__name__)

authomatic = Authomatic(config=CONFIG, secret=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(4096)))

@view_config(route_name='home', renderer='index.pt')
def home(request):
    user = DBSession.query(User).filter_by(id=request.authenticated_userid).first()
    user_email = None
    if user:
        user_email = user.email
    return dict(logged_in=(request.authenticated_userid != None),
                user_email=user_email)

@view_config(route_name='login_page', renderer='index.pt')
@forbidden_view_config(renderer='index.pt')
def login_page(request):
    return Response('''
        Login with <a href="login/google">Google</a>.<br />
    ''')

@view_config(route_name='logout', renderer='index.pt')
def logout(request):
    headers = forget(request)
    url = request.route_url('home')
    return HTTPFound(location=url, headers=headers)

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
            response.write(u'<h2>ERROR in login: {0}</h2>'.format(result.error.message))
        
        elif result.user:
            # OAuth 2.0 and OAuth 1.0a provide only limited user data on login,
            # We need to update the user to get more info.
            if not (result.user.name and result.user.id):
                result.user.update()

            row = DBSession.query(User).filter_by(google_id=result.user.id).first()
            if not row:
                user_id = DBSession.query(User).count()
                row = User(id=user_id, google_id=result.user.id, name="TMP", email=result.user.email)
                DBSession.add(row)
                transaction.commit()
            else:
                user_id = row.id

            headers = remember(request, user_id)
            log.debug("user id: {}".format(user_id))
            response.headerlist.extend(headers)
            # response.write(u'<h1>Hi {0}</h1>'.format(result.user.name))
            # response.write(u'<h2>Your id is: {0}</h2>'.format(result.user.id))
            # response.write(u'<h2>Your email is: {0}</h2>'.format(result.user.email))

            url = request.route_url('home')
            return HTTPFound(location=url, headers=headers)

    return response

@view_config(route_name='howdy', permission='edit')
def howdy(request):
    response = Response()
    response.write('HELLO THERE')
    return response

@view_config(route_name='my_feeds', renderer='feed_management.pt')
def my_feeds(request):
    feeds = rsstory.user.get_user_feeds(request.authenticated_userid)
    titles = []
    archive_urls = []
    time_created = []
    time_between_posts = []
    urls = []
    preview_feeds = []
    ids = []
    current_articles = []
    for f in feeds:
        titles.append(f.name)
        archive_urls.append(f.archive_url)
        time_created.append(datetime.datetime.fromtimestamp(f.time_created).strftime("%Y-%m-%d %H:%M:%S"))
        time_between_posts.append(f.time_between_posts // 60) # display in minutes
        urls.append("/static/feeds/" + f.id + ".xml")
        preview_feeds.append("/static/previews/preview" + f.id + ".txt")
        ids.append(f.id)
    user = DBSession.query(User).filter_by(id=request.authenticated_userid).first()
    user_email = None
    if user:
        user_email = user.email
    return dict(logged_in=(request.authenticated_userid != None),
                user_email=user_email,
                feeds=zip(titles, archive_urls, time_created, time_between_posts, urls, preview_feeds, ids))

@view_config(route_name='change_current_article', renderer='change_current_article.pt')
def change_current_article(request):
    user = DBSession.query(User).filter_by(id=request.authenticated_userid).first()
    user_email = None
    if user:
        user_email = user.email

    id = request.GET['id']
    feed = DBSession.query(Feed).filter_by(id=id).first()
    pages = DBSession.query(Page).filter_by(archive_url=feed.archive_url)
    page_titles = []
    page_urls = []
    page_ids = []
    for p in pages:
        page_ids.append(p.id)
        page_titles.append(p.name)
        page_urls.append(p.page_url)

    if not feed or feed.user != request.authenticated_userid:
        return dict(logged_in=(request.authenticated_userid != None),
                user_email=user_email,
                id=None,
                feed_url=None,
                feed_preview=None,
                archive_url=None,
                time_created=None,
                time_between_posts=None,
                pages=None,
                )

    return dict(logged_in=(request.authenticated_userid != None),
            user_email=user_email,
            feed_id=feed.id,
            feed_url="/static/feeds/" + feed.id + ".xml",
            feed_preview="/static/previews/preview" + feed.id + ".txt",
            archive_url=feed.archive_url,
            time_created=feed.time_created,
            time_between_posts=feed.time_between_posts,
            most_recent_page=feed.most_recent_page,
            pages=zip(page_ids, page_titles, page_urls)
            )

@view_config(route_name='update_place_in_feed', renderer='json')
def update_place_in_feed(request):
    rsstory.user.update_place_in_feed(request.json_body['feed_id'], request.json_body['page_id'], request.authenticated_userid)
    return {}

@view_config(route_name='delete_feed')
def delete_feed(request):
    rsstory.user.delete_feed(request.GET['id'], request.authenticated_userid)
    url = request.route_url('my_feeds')
    return HTTPFound(location=url)

@view_config(route_name='update_feed', renderer='json')
def update_feed(request):
    rsstory.user.update_user_feeds(request.json_body['feed_id'], request.json_body['title'], request.json_body['time_between'], request.authenticated_userid)
    return {"title": request.json_body['title']}

@view_config(route_name='feed', renderer='json')
def feed(request):
    if request.json_body['url'] == '':
        return {"rss": "Error"}
    xml_feed, preview_page, invalid_input = rss.archive_to_rss(request.json_body['url'], request.json_body['time'], request.json_body['time_units'], request.json_body['title'], request.json_body['captcha'], request.authenticated_userid, request.remote_addr)
    if invalid_input:
        return {"rss": "Error", "error_msg": "Error: A bad input value was entered. Be sure that the archive url is correct and that the time between posts is entered as a whole number of days (not as a decimal). If the values are actually correct, please leave a bug report at https://github.com/malnoxon/rsstory"}
    if xml_feed == False and preview_page == False:
        return {"rss": "Unknown Error"}
    return {"rss": "/static/feeds/" + xml_feed + ".xml", "preview": "/static/previews/" + preview_page}

@view_config(route_name='archive_fails', renderer='archive_fails.pt')
def archive_fails(request):
    # rss.report_archive_fail(request.json_body['url'], request.json_body['comments'])
    user = DBSession.query(User).filter_by(id=request.authenticated_userid).first()
    user_email = None
    if user:
        user_email = user.email
    return dict(logged_in=(request.authenticated_userid != None),
            user_email=user_email)
    # return {"success": True}


@view_config(route_name='report_archive_fails', renderer='json')
def report_archive_fails(request):
    if rss.report_archive_fail(request.json_body['url'], request.json_body['comments'], request.remote_addr, request.json_body['captcha']):
        return {"success": True}
    else:
        return {"rss": "Error"}

from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.settings import asbool
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from apscheduler.schedulers.background import BackgroundScheduler
import rsstory.rss as rss

from .models import (
    DBSession,
    Base,
    )

def main(global_config, **settings):
    debug_settings = asbool(settings.get(
        'debug_settings', 'false'
        ))
    settings['debug_settings'] = debug_settings
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings, root_factory='.resources.Root')
    config.include('pyramid_chameleon')

    # Security
    authn_policy = AuthTktAuthenticationPolicy(
            settings['rsstory.secret'],
            hashalg='sha512'
            )
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    rss.recreate_jobs()

    # config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('feed', '/feed')
    config.add_route('archive_fails', '/archive-fails')
    config.add_route('report_archive_fails', '/archive-fails/report')
    config.add_route('login', '/login/{provider_name}')
    config.add_route('login_page', '/login')
    config.add_route('logout', '/logout')
    config.add_route('howdy', '/howdy')
    config.add_route('my_feeds', '/my-feeds')
    config.add_route('update_feed', '/my-feeds/update-feed')
    config.add_route('change_current_article', '/my-feeds/change-current-article')
    config.add_route('update_place_in_feed', '/my-feeds/change-current-article/update-place-in-feed')
    config.add_route('delete_feed', '/my-feeds/delete-feed')
    # config.add_route('view_wiki', '/')
    # config.add_route('view_page', '/{pagename}')
    # config.add_route('add_page', '/add_page/{pagename}')
    # config.add_route('edit_page', '/{pagename}/edit_page')
    config.add_static_view(name='static', path='rsstory:static')
    # config.add_static_view(name='private_static', path='rsstory:static')
    config.scan('.views')
    return config.make_wsgi_app()

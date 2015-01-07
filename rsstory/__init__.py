from pyramid.config import Configurator
import load

def main(global_config, **settings):
    load.reload_global_index()
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_route('home', '/')
    config.add_route('feed', '/feed')
    config.add_static_view(name='static', path='rsstory:static')
    config.scan('.views')
    return config.make_wsgi_app()

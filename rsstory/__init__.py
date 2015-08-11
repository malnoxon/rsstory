from pyramid.config import Configurator
def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_route('home', '/')
    config.add_route('feed', '/feed')
    config.add_route('archive_fails', '/archive_fails')
    config.add_route('report_archive_fails', '/archive_fails/report')
    config.add_static_view(name='static', path='rsstory:static')
    config.scan('.views')
    return config.make_wsgi_app()

import importlib
from tld import get_tld
import rsstory.scrapers.page as page
import rsstory.scrapers.rest as rest
import rsstory.scrapers.monthly_sidebar as monthly_sidebar
import rsstory.scrapers.sites as sites

def scrape(url):
    try:
        if url in sites.get_site_dict():
            mod = importlib.import_module("rsstory.scrapers.siteRules.{}".format(sites.get_site_dict()[url]))
            method = getattr(mod, 'scrape')
            return method(url)

        elif get_tld(url) == "wordpress.com":
            mod = importlib.import_module("rsstory.scrapers.siteRules.wordpress")
            method = getattr(mod, 'scrape')
            return method(url)

        else:
            page_type = None # Is the archive a 'page', a 'sidebar', 'nested sidebar'...
            page_type = 'page' #TODO: currently we just assume a page, in future, ask user or figure it out dynamically

            if page_type == 'page':
                return page.scrape(url)
            elif page_type == 'monthly_sidebar':
                return monthly_sidebar.scrape(url)
            else:
                return rest.scrape(url)

    except RuntimeError as e:
        print(e)

def pl(h):
    for i in h:
        print(i.attrs['href'])

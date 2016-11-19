import importlib
from tld import get_tld
import rsstory.scrapers.page as page
import rsstory.scrapers.rest as rest
import rsstory.scrapers.next as next
import rsstory.scrapers.monthly_sidebar as monthly_sidebar
import rsstory.scrapers.sites as sites
import rsstory.scrapers.siteRules.wordpress as wordpress
import logging

log = logging.getLogger(__name__)

def scrape(url):
    try:
        if url in sites.get_site_dict():
            mod = importlib.import_module("rsstory.scrapers.siteRules.{}".format(sites.get_site_dict()[url]))
            method = getattr(mod, 'scrape')
            return method(url)

        elif wordpress.is_wordpress(url):
            mod = importlib.import_module("rsstory.scrapers.siteRules.wordpress")
            method = getattr(mod, 'scrape')
            log.info("Wordpress heuristics will be used")
            return method(url)

        elif get_tld(url) == "blogspot.com":
            mod = importlib.import_module("rsstory.scrapers.siteRules.blogspot")
            method = getattr(mod, 'scrape')
            log.info("Blogspot heuristics will be used")
            return method(url)

        else:
            page_type = None # Is the archive a 'page', a 'sidebar', 'nested sidebar'...
            page_type = 'next' #TODO: currently we just assume a page, in future, ask user or figure it out dynamically

            if page_type == 'page':
                log.info("Single page archive heuristics will be used")
                return page.scrape(url)
            elif page_type == 'monthly_sidebar':
                log.info("Monthly sidebar archive heuristics will be used")
                return monthly_sidebar.scrape(url)
            elif page_type == 'next':
                return next.scrape(url)
            else:
                return rest.scrape(url)

    except RuntimeError as e:
        print(e)

def pl(h):
    for i in h:
        print(i.attrs['href'])

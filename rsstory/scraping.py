import rsstory.scrapers.page as page
import rsstory.scrapers.rest as rest

def scrape(url):
    try:
        page_type = None # Is the archive a 'page', a 'sidebar', 'nested sidebar'...
        page_type = 'page' #TODO: currently we just assume a page, in future, ask user or figure it out dynamically

        if page_type == 'page':
            return page.scrape_page(url)
        else:
            return rest.scrape_rest(url)

    except RuntimeError as e:
        print(e)

def pl(h):
    for i in h:
        print(i.attrs['href'])

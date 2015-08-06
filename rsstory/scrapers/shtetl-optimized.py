import rsstory.scrapers.page as page

def scrape(url):
    links = page.scrape_page(url)
    first = links[:44]
    last = links[44:]
    first.reverse()
    return first + last

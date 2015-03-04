import urllib3
from bs4 import BeautifulSoup
import rsstory.scrapers.tools as tools

http = urllib3.PoolManager()

def scrape_page(url):
    '''Used if scraping a one page archive (eg https://xkcd.com/archive/ )'''
    r = http.request('GET', url)
    soup = BeautifulSoup(r.data) #TODO different parser?
    links = soup.find_all('a', href=True)
    arst = tools.filterArchiveLinks(links, url)
    sorted_links = tools.sort_links(arst)

    return sorted_links

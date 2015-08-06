import urllib3
from bs4 import BeautifulSoup
import rsstory.scrapers.tools as tools
import certifi

http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where(),
        )

def scrape(url):
    '''Used if scraping a one page archive (eg https://xkcd.com/archive/ )'''
    try:
        r = http.request('GET', url)
    except urllib3.exceptions.SSLError as e:
        print(e)
    soup = BeautifulSoup(r.data) #TODO different parser?
    links = soup.find_all('a', href=True)
    arst = tools.filterArchiveLinks(links, url)
    sorted_links = tools.sort_links(arst)

    return sorted_links

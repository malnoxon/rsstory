import urllib3, re, arrow, sys
from bs4 import BeautifulSoup
import rsstory.scrapers.tools as tools

http = urllib3.PoolManager()

''' Grabs the monthly archive links from a sidebar and returns them'''
def scrape(url):
    sys.setrecursionlimit(10000)
    month_links = set([])
    r = http.request('GET', url)
    soup = BeautifulSoup(r.data)
    #looking for anything with the header matching re archive
    # EG, if on a blog such as http://terrytao.wordpress.com/ where no 
    # separate archive page exists but instead a sidebar
    archive = soup.find_all(id=re.compile("archive", re.I))
    if not len(archive) == 0:
        for i in map(lambda x: x.find_all('a', href=True), archive):
            for j in i:
                month_links.add(j)
    #find all things with dates in content
    # import pdb; pdb.set_trace()
    links = soup.find_all('a', href=True)
    for i in filter(lambda x: tools.containsDate(x.contents) or tools.dictContainsDate(x.attrs), links):
    # for i in filter(lambda x: tools.date_of_url(x) is not None, links):
        month_links.add(i)
    #make sure it comes from same url
    def same(x):
        #Same function fails on xkcd <= 999
        try:
            att = x.attrs['href']
            return not arrow.get(att) == None or att[0:len(url)] == url or att[0] == '/'
        except Exception:
            return False
    # month_links = list(filter(same, month_links))
    month_links = tools.filterArchiveLinks(month_links, url)
    month_links = tools.sort_by_date(month_links)

    return month_links

import urllib3, re, arrow, sys
from bs4 import BeautifulSoup
import rsstory.scrapers.tools as tools
import certifi

http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where(),
        )

def scrape(url):
    sys.setrecursionlimit(10000)
    arst = set([])
    try:
        r = http.request('GET', url)
    except urllib3.exceptions.SSLError as e:
        print(e)
    soup = BeautifulSoup(r.data)
    #looking for anything with the header matching re archive
    # EG, if on a blog such as http://terrytao.wordpress.com/ where no 
    # separate archive page exists but instead a sidebar
    archive = soup.find_all(id=re.compile("archive", re.I))
    if not len(archive) == 0:
        for i in map(lambda x: x.find_all('a', href=True), archive):
            for j in i:
                arst.add(j)
    #find all things with dates in content
    links = soup.find_all('a', href=True)
    for i in filter(lambda x: tools.containsDate(x.contents) or tools.dictContainsDate(x.attrs), links):
        arst.add(i)
    #make sure it comes from same url
    def same(x):
        #Same function fails on xkcd <= 999
        try:
            att = x.attrs['href']
            return not arrow.get(att) == None or att[0:len(url)] == url or att[0] == '/'
        except Exception:
            return False
    # arst = list(filter(same, arst))
    arst = tools.filterArchiveLinks(arst, url)
    arst = tools.sort_by_date(arst)

    return arst

import urllib3, re, pdb
from urllib.parse import urlparse
from bs4 import BeautifulSoup

http = urllib3.PoolManager()

def iterlen(itr):
    l = 0
    for i in itr:
        l += 1
    return l
def firstMatchingID(soup, reg):
    def recur(soup, reg, ans):
        print(type(soup))
        if soup.has_attr('id') and (not re.match(reg, soup.attrs["id"]) == None):
            return soup
        if iterlen(soup.children) == 0:
            return []
        for i in soup.children:

            c = recur(i, reg, ans)
            if not c == []:
                return c
        return []
    recur(soup, reg, [])

def containsDate(strng):
    if isinstance(strng, list):
        return any(map(lambda x: containsDate(x), strng))
    match = False
    if isinstance(strng, str):
        strng = strng.lower()
        for i in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
                  'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'november', 'december']:
            match = match or not strng.find(i) == -1
    return match
def dictContainsDate(dic):
    match = False
    for i in dic.values():
        match = match or containsDate(i)
    return match
def isRelativeLink(st):
    return urlparse(st).netloc == '' and not urlparse(st).path == ''
def isAbsoluteLink(st):
    return not urlparse(st).netloc == ''

def scrape3(url):
    ll = set([])
    r = http.request('GET', url)
    soup = BeautifulSoup(r.data)
    #looking for anything with the header matching re archive
    archive = soup.find_all(id=re.compile("archive", re.I))
    if not len(archive) == 0:
        for i in map(lambda x: x.find_all('a', href=True), archive):
            for j in i:
                ll.add(j)
    links = soup.find_all('a', href=True)
    for i in filter(lambda x: containsDate(x.contents) or dictContainsDate(x.attrs), links):
        ll.add(i)
    def same(x):
        try:
            return x.attrs['href'][0:len(url)] == url
        except:
            return False

    ll = list(filter(same, ll))
    return ll

def pl(h):
    for i in h:
        print(i.attrs['href'])

import urllib3, re, arrow
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import numpy as np
import Pycluster
import dateutil.parser
import datetime

http = urllib3.PoolManager()

def iterlen(itr):
    l = 0
    for i in itr:
        l += 1
    return l
def firstMatchingID(soup, reg):
    def recur(soup, reg, ans):
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
    if isinstance(strng, str):
        template = ["YYYY-MM-DD","YYYY-M-DD", "YYYY-MM-D", "YYYY-M-D", "dddd-MMM-YYYY",
                    "dddd-MMMM-YYYY", "MMMM-dddd-YYYY", "MMMM-DD-YYYY", "YYYY-MMMM", "YYYY-MMM", "YYYY-MM",
                    'YYYY', 'MMMM', "MMM"]
        for i in template:
            try:
                arrow.get(strng, i)
                return True
            except Exception:
                pass
    return False
def dictContainsDate(dic):
    match = False
    for i in dic.values():
        match = match or containsDate(i)
    return match
def isRelativeLink(st):
    return urlparse(st).netloc == '' and not urlparse(st).path == ''
def isAbsoluteLink(st):
    return not urlparse(st).netloc == ''
def tests():
    urls = [("http://freegamer.blogspot.com/",),
            ("http://www.mode7games.com/blog/",),
            ("http://xkcd.com/archive/",),
            "http://www.joelonsoftware.com/backIssues-2000-03.html"]

class Feature():
    number = 0
    word = 1
    other = 2
def classify(chunk):
    if chunk.isalpha():
        return Feature.word
    elif chunk.isdigit():
        return Feature.number
    return Feature.other
def freq(array, num):
    return sum([1 for i in array if i == num])
def feature(url):
    fv = re.split(re.compile('[-_/.//]'), str(url))
    fv = filter(lambda x: not x == '', fv)
    fv = map(lambda x: classify(x), fv)
    return {'number': freq(fv, Feature.number),
            'word': freq(fv, Feature.word),
            'other': freq(fv, Feature.other),
            'url': url}
def filterArciveLinks(all_links): 
    features = np.zeros(shape=(len(all_links),3))
    for i, link in enumerate(all_links):
        f = feature(link)
        features[i][0] = f['number']
        features[i][1] = f['word']
        features[i][2] = f['other']
    if len(features) > 1:
        labels, error, nfound = Pycluster.kcluster(features,2)
    else:
        return all_links
    group1 = []
    group2 = []
    for i,link in enumerate(all_links):
        if labels[i] == 1:
            group1.append(link)
        else:
            group2.append(link)

    if len(group1) > len(group2):
        return group1
    else:
        return group2

def sort_by_date(urls):
    urls = list(filter(lambda x: date_of_url(x) is not None, urls))
    urls.sort(key=lambda x: date_of_url(x))
    import pdb; pdb.set_trace()
    return urls

def date_of_url(link):
    #TODO: test with yearfirst first, than monthfirst
    d = None
    try:
        d = _date_of_url(link, False, False)
    except:
        d= None

    return d

def _date_of_url(link, df, yf):
    #TODO: compare by comparing date using 2 different defaults
    parsed_exactness = []
    parsed_dates = []
    parsed = None
    if link.attrs.keys is not None:
        for attr in link.attrs.keys():
            if attr is not None:
                p1 = dateutil.parser.parse(link.attrs[attr], default=datetime.datetime.max, fuzzy=True, dayfirst=df, yearfirst=yf)
                p2 = dateutil.parser.parse(link.attrs[attr], default=datetime.datetime.min, fuzzy=True, dayfirst=df, yearfirst=yf)
                num_same = 0
                if p1.year == p2.year:
                    num_same += 1
                if p1.month == p2.month:
                    num_same += 1
                if p1.day == p2.day:
                    num_same += 1
                parsed_exactness.append(num_same)
                parsed_dates.append(p1)
    p1 = dateutil.parser.parse(link.string, fuzzy=True, dayfirst=df, yearfirst=yf, default=datetime.datetime.max)
    p2= dateutil.parser.parse(link.string, fuzzy=True, dayfirst=df, yearfirst=yf, default=datetime.datetime.min)
    num_same = 0
    if p1.year == p2.year:
        num_same += 1
    if p1.month == p2.month:
        num_same += 1
    if p1.day == p2.day:
        num_same += 1
    parsed_exactness.append(num_same)
    parsed_dates.append(p1)

    index = parsed_exactness.index(max(parsed_exactness))
    parsed = parsed_dates[index]

    return parsed

def scrape(url):
    try:
        import sys
        sys.setrecursionlimit(10000)
        arst = set([])
        r = http.request('GET', url)
        soup = BeautifulSoup(r.data)
        #looking for anything with the header matching re archive
        archive = soup.find_all(id=re.compile("archive", re.I))
        if not len(archive) == 0:
            for i in map(lambda x: x.find_all('a', href=True), archive):
                for j in i:
                    arst.add(j)
        #find all things with dates in content
        links = soup.find_all('a', href=True)
        for i in filter(lambda x: containsDate(x.contents) or dictContainsDate(x.attrs), links):
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
        arst = filterArciveLinks(arst)
        arst = sort_by_date(arst)

        return arst
    except RuntimeError as e:
        print(e)

def pl(h):
    for i in h:
        print(i.attrs['href'])

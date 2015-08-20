import urllib3, re, arrow
from tld import get_tld
from urllib.parse import urlparse
import numpy as np
import Pycluster
import dateutil.parser
import collections
import datetime
import certifi

http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where()
        )

def iterlen(itr):
    l = 0
    for i in itr:
        l += 1
    return l

def clean_url(url):
    '''Removes protocol from url and ensures a trailing slash exists'''
    url = url.replace("http://", "").replace("https://", "")
    if url[-1] != "/":
        url.append("/")

    return url

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

def containsDate(in_date):
    if isinstance(in_date, list):
        return any(map(lambda x: containsDate(x), in_date))
    if isinstance(in_date, str):
        template = ["YYYY-MM-DD","YYYY-M-DD", "YYYY-MM-D", "YYYY-M-D", "dddd-MMM-YYYY",
                    "dddd-MMMM-YYYY", "MMMM-dddd-YYYY", "MMMM-DD-YYYY", "YYYY-MMMM", "YYYY-MMM", "YYYY-MM", "MMMM YYYY", "MMMM YY", "MMM YYYY", "MMM YY"]#, "MMMM", "MMM", "YYYY"]
        for i in template:
            try:
                arrow.get(in_date, i)
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

def feature_attrs(url, all_attrs):
    features = {}
    for key in all_attrs:
        if key in url.attrs:
            features[key] = 1
        else:
            features[key] = 0

    return features

def feature(url):
    fv = re.split(re.compile('[-_/.//]'), str(url))
    fv = filter(lambda x: not x == '', fv)
    fv = map(lambda x: classify(x), fv)
    return {'number': freq(fv, Feature.number),
            'word': freq(fv, Feature.word),
            'other': freq(fv, Feature.other),
            'url': url}

def filterArchiveLinks(all_links, page_url): 
    '''Filters the links by splitting them up into two clusters and throwing 
    out the cluster that looks least like an archive. Note that this is most 
    effective if the page is essencially archive links, and other boilerplate
    stuff, i.e. a one page full archive. It is much less likely to work on
    Sidebar and drop-down archives'''

    #First remove all links to a different domain (broken links allowed as they
    # may actually be relative links)
    domain = get_tld(page_url)
    all_links = [url for url in all_links if get_tld(url['href'], fail_silently=True) in (domain, None)]

    # Cluster based on attributes of the links, largest is likely the archive
    all_attrs = set()
    for link in all_links:
        for key in link.attrs.keys():
            all_attrs.add(key)

    features = np.zeros(shape=(len(all_links), len(all_attrs)))
    for i, link in enumerate(all_links):
        f = feature_attrs(link, all_attrs)
        j = 0
        for key in all_attrs:
            features[i][j] = f[key]
            j += 1

    #TODO: maybe create these features in addition to the attrs of the links?
    # features = np.zeros(shape=(len(all_links),3))
    # for i, link in enumerate(all_links):
    #     f = feature(link)
    #     features[i][0] = f['number']
    #     features[i][1] = f['word']
    #     features[i][2] = f['other']

    # Check that all columns are different in features, if not we return all links
    # since we can't determine clusters
    _, num_cols = features.shape
    col = None
    diff_cols = False
    for i in range(0, num_cols):
        if col is None:
            col = features[:,i]
        else:
            if np.array_equal(col, features[:,i]):
                diff_cols = True
                break

    if not diff_cols:
        return all_links

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

def date_of_url_arrow(link):
    template = ["YYYY-MM-DD","YYYY-M-DD", "YYYY-MM-D", "YYYY-M-D", "dddd-MMM-YYYY", "dddd-MMMM-YYYY", "MMMM-dddd-YYYY", "MMMM-DD-YYYY", "YYYY-MMMM", "YYYY-MMM", "YYYY-MM", "MMMM YYYY", "MMMM YY", "MMM YYYY", "MMM YY"]#, "MMMM", "MMM", "YYYY"]
    if link.attrs.keys() is not None:
        for attr in link.attrs.keys():
            attribute = link.attrs[attr]
            for i in template:
                try:
                    date = arrow.get(attribute,i)
                    return date
                except:
                    pass

    for i in template:
        try:
            date = arrow.get(link.text, i)
            return date
        except Exception:
            pass
    return None

def sort_by_date(urls):
    #If date_of_url fails on some dates, use arrow
    if any(filter(lambda x: date_of_url(x) is None, urls)):
        urls = list(filter(lambda x: date_of_url_arrow(x) is not None, urls))
        urls.sort(key=lambda x: date_of_url_arrow(x))
    else:
        urls = list(filter(lambda x: date_of_url(x) is not None, urls))
        urls.sort(key=lambda x: date_of_url(x))
    return urls

def date_of_url(link):
    d = None
    try:
        d = _date_of_url(link, True, True)
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
            attribute = link.attrs[attr]
            parse_date(link, df, yf, attribute, parsed_exactness, parsed_dates)
    parse_date(link, df, yf, link.string, parsed_exactness, parsed_dates)

    index = parsed_exactness.index(max(parsed_exactness))
    parsed = parsed_dates[index]

    return parsed

def parse_date(link, df, yf, attribute, parsed_exactness, parsed_dates):
    if isinstance(attribute, str):
        p1 = dateutil.parser.parse(attribute, default=datetime.datetime.max, fuzzy=True, dayfirst=df, yearfirst=yf)
        p2 = dateutil.parser.parse(attribute, default=datetime.datetime.min, fuzzy=True, dayfirst=df, yearfirst=yf)
        num_same = 0
        if p1.year == p2.year:
            num_same += 1
        if p1.month == p2.month:
            num_same += 1
        if p1.day == p2.day:
            num_same += 1
        parsed_exactness.append(num_same)
        parsed_dates.append(p1)
    elif isinstance(attribute, collections.Iterable):
        for subattribute in attribute:
            parse_date(link, df, yf, subattribute, parsed_exactness, parsed_dates)

def sort_links(links):
    # links.reverse()
    sorted_links = sort_by_date(links)
    return sorted_links

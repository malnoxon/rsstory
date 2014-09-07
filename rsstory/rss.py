import datetime, PyRSS2Gen, sys, pdb, hashlib
from scraping import *

def gen_pages(items, data_list):
    data = data_list.pop(0)
    items.append( PyRSS2Gen.RSSItem(
        title = data[1],
        link = data[0],
        description = "tmp",
        guid = PyRSS2Gen.Guid(data[0]),
        pubDate = datetime.datetime.now()
        ))

def write_rss(rss_items, url):
    rss = PyRSS2Gen.RSS2(
            title = "Test RSS feed",
            link = "http://127.0.0.1:8000/sample.html",
            description = "TEST",
            lastBuildDate = datetime.datetime.now(),
            items = rss_items
                )
    s = hashlib.sha224(bytes(url, 'utf-8')).hexdigest()
    f = open("/home/gabe/Projects/rsstory/rsstory/static/feeds/" + s + ".xml", "w+")
    rss.write_xml(f)
    return s

def archive_to_rss(url):
    last_update = datetime.datetime.now()
    time_between = datetime.timedelta(seconds=30)
    rss_items = []
    url_data = []
    links = scrape(url)
    for i in links:
        # import pdb; pdb.set_trace()
        ln = i.attrs['href']
        try:
            if not ln[0:len(url)] == url:
                ln = url + ln
        except e:
            ln = url + ln
        if len(i.contents) > 0:
            ti = str(i.contents[0])
        else:
            ti = "Unknown"

        url_data.append((ln, ti))

    #have to add delay maybe.
    gen_pages(rss_items, url_data)
    last_update = datetime.datetime.now()
    return write_rss(rss_items, url)


if __name__ == "__main__":
    archive_to_rss(str(sys.argv[1]))

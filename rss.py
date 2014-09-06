import datetime, PyRSS2Gen, sys, pdb
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

def write_rss(rss_items):
    rss = PyRSS2Gen.RSS2(
            title = "Test RSS feed",
            link = "http://127.0.0.1:8000/sample.html",
            description = "TEST",
            lastBuildDate = datetime.datetime.now(),
            items = rss_items
                )

    rss.write_xml(open("pyrss2gen.xml", "w"))


def archive_to_rss(url):
    last_update = datetime.datetime.now()
    time_between = datetime.timedelta(seconds=30)
    rss_items = []
    links = scrape(url)
    for i in links:
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
        rss_items.append(
            PyRSS2Gen.RSSItem(
                title = ti,
                link = ln,
                description = "None",
                guid = PyRSS2Gen.Guid("http://www.smbc-comics.com/index.php?id=281rdtra"),
                pubDate = datetime.datetime.now()
            )
        )
    url_data = [(i.link, i.title) for i in rss_items]
    write_rss(rss_items)
    #have to add delay maybe.
    gen_pages(rss_items, url_data)
    last_update = datetime.datetime.now()
    write_rss(rss_items)


if __name__ == "__main__":
    archive_to_rss(str(sys.argv[1]))

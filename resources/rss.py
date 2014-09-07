import datetime, PyRSS2Gen, sys, pdb
from scraping import *
import urllib.parse

def gen_pages(items, data_list, time_between):
    curr_time = datetime.datetime.now()
    while data_list:
        data = data_list.pop(0)
        items.append( PyRSS2Gen.RSSItem(
            title = data[1],
            link = data[0],
            description = "tmp",
            guid = PyRSS2Gen.Guid(data[0]),
            pubDate = curr_time
            ))
        curr_time += time_between

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
    time_between = datetime.timedelta(days=1)
    rss_items = []
    url_data = []
    links = scrape(url)
    #TODO: instead of future dating, release the feeds in the future
    for i in links:
        # import pdb; pdb.set_trace()
        ln = i.attrs['href']
        ln = urllib.parse.urljoin(url, ln)
        if len(i.contents) > 0:
            ti = str(i.contents[0])
        else:
            ti = "Unknown"
        print(ln)
        print(ti)

        url_data.append((ln, ti))

    #have to add delay maybe.
    gen_pages(rss_items, url_data, time_between)
    last_update = datetime.datetime.now()
    write_rss(rss_items)
    print("Done")


if __name__ == "__main__":
    archive_to_rss(str(sys.argv[1]))

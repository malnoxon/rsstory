import datetime
import PyRSS2Gen



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


def main():
    last_update = datetime.datetime.now()
    time_between = datetime.timedelta(seconds=30)
    rss_items = [
                PyRSS2Gen.RSSItem(
                    title = "blah0",
                    link = "http://127.0.0.1:8000/sample.html",
                    description = "desc0",
                    guid = PyRSS2Gen.Guid("http://127.0.0.1:8000/sample.html"),
                    pubDate = datetime.datetime(2014,9,3)),
                PyRSS2Gen.RSSItem(
                    title = "blah1",
                    link = "http://www.smbc-comics.com/index.php?id=280",
                    description = "desc1",
                    guid = PyRSS2Gen.Guid("http://www.smbc-comics.com/index.php?id=280"),
                    pubDate = datetime.datetime(2014,9,3)),
                PyRSS2Gen.RSSItem(
                    title = "blah2",
                    link = "http://www.smbc-comics.com/index.php?id=280",
                    description = "desc2",
                    guid = PyRSS2Gen.Guid("http://www.smbc-comics.com/index.php?id=281rdtra"),
                    pubDate = datetime.datetime(2014,9,5))
                ]

    url_data = [("http://www.smbc-comics.com/index.php?id=284", "Num 1"),( "http://www.smbc-comics.com/index.php?id=285", "Num 2")]

    write_rss(rss_items)
    while True:
        if last_update + time_between < datetime.datetime.now() and url_data:
            gen_pages(rss_items, url_data)
            last_update = datetime.datetime.now()

            write_rss(rss_items)


if __name__ == "__main__":
    main()

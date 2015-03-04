import datetime, PyRSS2Gen, sys, pickle
from rsstory.scraping import *
import rsstory.periodic as periodic
import urllib.parse
import os
import rsstory.global_vars as global_vars

def gen_pages(items, data_list, time_between):
    curr_time = datetime.datetime.now()
    while data_list:
        data = data_list.pop(0)
        items.append(PyRSS2Gen.RSSItem(
            title = data[1],
            link = data[0],
            description = data[0],
            guid = PyRSS2Gen.Guid(data[0]),
            pubDate = curr_time
            ))
        curr_time += time_between

    #End of archive message
    items.append(PyRSS2Gen.RSSItem(
        title = "Archive End",
        description = "This RSStory archive feed has ended. You have now seen all the posts that were contained in the website's archive when you created this archive feed. Thank you for using RSStory. If you wish to report an issue or help develop RSStory you can do so at https://github.com/Daphron/rsstory",
        link = "https://github.com/Daphron/rsstory",
        guid = PyRSS2Gen.Guid("https://github.com/Daphron/rsstory"),
        pubDate = curr_time
        ))

def write_rss(rss_items, url, page_num=None, title=None):
    if page_num == None:
        page_num = global_vars.global_index
    if title == None or title == "":
        title = "RSStory: {}".format(url)
    description = "RSStory feed for {}".format(url)
        
    # import pdb; pdb.set_trace()
    rss = PyRSS2Gen.RSS2(
            title = title,
            link = url,
            description = description,
            lastBuildDate = datetime.datetime.now(),
            items = filter(lambda x: x.pubDate < datetime.datetime.now(), rss_items)
                )
    s = str(page_num)
    f = open(os.path.join(os.path.abspath(os.path.dirname(__file__)),'static', 'feeds', s+".xml"), "w+")
    rss.write_xml(f)
    return s

def write_preview_feed(rss_items, url, title):
    fname = "preview{}.txt".format(global_vars.global_index)
    fpath = os.path.join(os.getcwd(), 'rsstory', 'static', 'previews', fname)
    f = open(fpath, 'w')
    f.write("Title: {}\n".format(title))
    f.write("URL: {}\n".format(url))
    f.write("ITEMS: \n")
    for i, item in enumerate(rss_items):
        f.write(str(i) + ":\t" + item.title + " " + item.link + "\n")

    f.close()
    return fname
    

def archive_to_rss(url, time_between_posts, title):
    time_between = datetime.timedelta(minutes=int(time_between_posts))
    rss_items = []
    url_data = []
    links = scrape(url)
    for i in links:
        ln = i.attrs['href']
        ln = urllib.parse.urljoin(url, ln)
        if len(i.contents) > 0:
            ti = str(i.contents[0])
        else:
            ti = "Unknown"

        url_data.append((ln, ti))

    #have to add delay maybe.
    gen_pages(rss_items, url_data, time_between)
    fname = "rssitems{}.p".format(global_vars.global_index)
    fpath = os.path.join(os.getcwd(), 'rsstory', 'static', 'rssitems', fname)
    pickle.dump((rss_items, url, title), open(fpath, "wb"))
    rss_feed_filename = write_rss(rss_items, url, title=title)
    periodic.setup_cron(fpath, time_between)
    preview_feed_filename = write_preview_feed(rss_items, url, title)
    global_vars.global_index += 1
    return (rss_feed_filename, preview_feed_filename)


if __name__ == "__main__":
    archive_to_rss(str(sys.argv[1]), str(sys.argv[2]), str(sys.argv[3]))

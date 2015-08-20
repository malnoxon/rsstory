import datetime, PyRSS2Gen, sys, pickle
from rsstory.scraping import *
import rsstory.periodic as periodic
import urllib.parse
import os
from norecaptcha3.captcha import submit
from random import SystemRandom
import logging

log = logging.getLogger(__name__)

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

def write_rss(rss_items, url, archive_id, title=None):
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
    s = str(archive_id)
    f = open(os.path.join(os.path.abspath(os.path.dirname(__file__)),'static', 'feeds', s+".xml"), "w+")
    rss.write_xml(f)
    return s

def write_preview_feed(rss_items, url, title, feed_id):
    fname = "preview{}.txt".format(feed_id)
    fpath = os.path.join(os.getcwd(), 'rsstory', 'static', 'previews', fname)
    f = open(fpath, 'w')
    f.write("Title: {}\n".format(title))
    f.write("URL: {}\n".format(url))
    f.write("ITEMS: \n")
    for i, item in enumerate(rss_items):
        f.write(str(i) + ":\t" + item.title + " " + item.link + "\n")

    f.close()
    return fname

def archive_to_rss(url, time_between_posts, title, recaptcha_answer, ip):
    log.info("Beginning archive_to_rss()")
    key = ""
    try:
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'secret', 'recaptcha_key_secret.key'), 'r') as f:
            key = f.readline()
    except:
        log.error("The file containing the secret key was not located")
        return (False, False)
        
    captcha_response = submit(remote_ip=ip, secret_key=key, response=recaptcha_answer)
    log.debug("recaptcha_answer is: {}".format(recaptcha_answer))
    if captcha_response.is_valid:
        log.info("Captcha response verified as valid")
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
        archive_id = SystemRandom().getrandbits(512)
        fname = "rssitems{}.p".format(archive_id)
        fpath = os.path.join(os.getcwd(), 'rsstory', 'static', 'rssitems', fname)
        pickle.dump((rss_items, url, title), open(fpath, "wb"))
        rss_feed_filename = write_rss(rss_items, url, archive_id, title=title)
        periodic.setup_cron(fpath, time_between)
        preview_feed_filename = write_preview_feed(rss_items, url, title, archive_id)
        return (rss_feed_filename, preview_feed_filename)
    else:
        log.error("Invalid captcha entered")
        return (False, False)

def report_archive_fail(url, comments, ip, recaptcha_answer):
    log.info("Beginning report_archive_fail")
    key = ""
    try:
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'secret', 'recaptcha_key_secret.key'), 'r') as f:
            key = f.readline()
    except:
        log.error("The file containing the secret key was not located")
        return False
        
    captcha_response = submit(remote_ip=ip, secret_key=key, response=recaptcha_answer)
    log.debug("recaptcha_answer is: {}".format(recaptcha_answer))
    if captcha_response.is_valid:
        log.info("Captcha response verified as valid")
        fname = "failed_urls.txt"
        fpath = os.path.join(os.getcwd(), 'rsstory', fname)
        f = open(fpath, 'a')
        f.write("URL: {}\n".format(url))
        f.write("COMMENTS: {} \n".format(comments))
        f.close()
        return True
    else:
        log.error("Captcha invalid")
        return False

if __name__ == "__main__":
    archive_to_rss(str(sys.argv[1]), str(sys.argv[2]), str(sys.argv[3]))

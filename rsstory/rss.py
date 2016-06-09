import datetime, PyRSS2Gen, sys, pickle
from rsstory.scraping import *
import rsstory.periodic as periodic
import pyramid.threadlocal
import urllib.parse
import os
from norecaptcha3.captcha import submit
from random import SystemRandom
import logging
import time
import transaction

from .models import (
        DBSession,
        Feed,
        Page,
        )

log = logging.getLogger(__name__)

''' Gets the row of the table, creating it first if it doesn't exit'''
def get_or_create_row(table, **kwargs):
    row = DBSession.query(table).filter_by(**kwargs).first()
    if row:
        return (row, False)
    else:
        row = table(**kwargs)
        DBSession.add(row)
        transaction.commit() # TODO: can we do this less frequently?
        return (row, True)

def gen_pages(items, data_list, time_between, archive_url):
    #TODO: way to deal with changes to parsing engine!!!!!
    curr_time = datetime.datetime.now()
    index = 0
    while data_list:
        data = data_list.pop(0)
        page, created = get_or_create_row(Page, id=index, name=data[1], page_url=data[0], archive_url=archive_url)

        items.append(PyRSS2Gen.RSSItem(
            title = page.name,
            link = page.page_url,
            description = page.page_url,
            guid = PyRSS2Gen.Guid(page.page_url),
            pubDate = curr_time
            ))
        curr_time += time_between
        index += 1

''' Takes the given rss_data urls and page titles and writes to the page 
for the given feed object. rss_data is assumed to be ORDERED'''
def write_rss(feed, rss_data):
    # import pdb; pdb.set_trace();
    if feed.name == None or feed.name == "":
        feed.name = "RSStory: {}".format(feed.archive_url)
    description = "RSStory feed for {}".format(feed.archive_url)

    # curr_time = datetime.datetime.now()
    curr_time = datetime.datetime.fromtimestamp(feed.time_created)
    time_between = datetime.timedelta(feed.time_between_posts)
    rss_items = []
    index = 0
    while rss_data:
        data = rss_data.pop(0)
        page = DBSession.query(Page).filter_by(id=index, name=data[1], page_url=data[0], archive_url=feed.archive_url).first()

        rss_items.append(PyRSS2Gen.RSSItem(
            title = page.name,
            link = page.page_url,
            description = page.page_url,
            guid = PyRSS2Gen.Guid(page.page_url),
            pubDate = curr_time
            ))
        curr_time += time_between
        index += 1

    #TODO: add end of archive message when we've checked and seen the archive is done instead of now
    # End of archive message
    # last_item = PyRSS2Gen.RSSItem(
    #     title = "Archive End",
    #     description = "This RSStory archive feed has ended. You have now seen all the posts that were contained in the website's archive when you created this archive feed. Thank you for using RSStory. If you wish to report an issue or help develop RSStory you can do so at https://github.com/Daphron/rsstory",
    #     link = "https://github.com/Daphron/rsstory",
    #     guid = PyRSS2Gen.Guid("https://github.com/Daphron/rsstory"),
    #     pubDate = curr_time
    #     )
    # rss_items.append(last_item)
        
    rss = PyRSS2Gen.RSS2(
            title = feed.name,
            link = feed.archive_url,
            description = feed.archive_url,
            lastBuildDate = datetime.datetime.now(),
            items = rss_items
            )
    s = str(feed.id)
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

def archive_to_rss(archive_url, time_between_posts, title, recaptcha_answer, ip):
    try:
        # import pdb; pdb.set_trace();
        log.info("Beginning archive_to_rss()")
        key = ""
        try:
            with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'secret', 'secrets.keys'), 'r') as f:
                key = f.readline().split(",")[1]
        except:
            log.error("The file containing the secret key was not located")
            return (False, False, False)
            
        captcha_response = submit(remote_ip=ip, secret_key=key, response=recaptcha_answer)
        log.debug("recaptcha_answer is: {}".format(recaptcha_answer))
        registry = pyramid.threadlocal.get_current_registry()

        if captcha_response.is_valid or registry.settings['debug_settings']:
            if captcha_response.is_valid:
                log.info("Captcha response verified as valid")
            elif registry.settings['debug_settings']:
                log.info("Captcha response not needed due to debug_settings=True")
            time_between = datetime.timedelta(days=int(time_between_posts))
            rss_items = []
            url_data = []
            links = scrape(archive_url)
            for i in links:
                ln = i.attrs['href']
                ln = urllib.parse.urljoin(archive_url, ln)
                if len(i.contents) > 0:
                    ti = str(i.contents[0])
                else:
                    ti = "Unknown"

                url_data.append((ln, ti))
            log.info("Starting gen_pages()")

            #have to add delay maybe.
            gen_pages(rss_items, url_data[:], time_between, archive_url)
            archive_id = SystemRandom().getrandbits(512)
            # fname = "rssitems{}.p".format(archive_id)
            # fpath = os.path.join(os.getcwd(), 'rsstory', 'static', 'rssitems', fname)
            # log.info("Starting pickle dump")
            # pickle.dump((rss_items, archive_url, title), open(fpath, "wb"))
            with transaction.manager:
                feed = Feed(id=str(archive_id), name=title, archive_url=archive_url, time_between_posts=time_between.days, time_created=int(time.time()), user=None)
                DBSession.add(feed)
                # DBSession.commit()
                transaction.commit()
                log.info("Transaction committed")
            rss_feed_filename = write_rss(feed, url_data[:1])
            # log.info("rss_feed_filename is: {}".format(rss_feed_filename))
            # periodic.setup_cron(fpath, time_between)
            preview_feed_filename = write_preview_feed(rss_items, archive_url, title, archive_id)
            log.info("preview feed written")
            return (rss_feed_filename, preview_feed_filename, False)
        else:
            log.error("Invalid captcha entered")
            return (False, False, False)
    except ValueError as e:
        log.error("archive_to_rss ValueError:: {}".format(str(e)))
        return (False, False, True)
    except Exception as e:
        log.error("Archive to RSS had an error:: {}".format(str(e)))
        print(sys.exc_info()[0], os.path.split(sys.exc_info()[2].tb_frame.f_code.co_filename)[1], sys.exc_info()[2].tb_lineno)
        import pdb; pdb.post_mortem(sys.exc_info()[2]);
        return (False, False, False)

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

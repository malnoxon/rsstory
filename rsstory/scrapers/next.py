import urllib3
from bs4 import BeautifulSoup
import rsstory.scrapers.tools as tools
import certifi
import logging

log = logging.getLogger(__name__)

http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where(),
        )

def scrape(url):
    '''Used if scraping a webcomic with a "next" type button
        eg. xkcd, smbc, not a villan'''
        # TODO: auto find the first page, give way to select type of parsing,
        # do this not all right now, 
    log.debug("Adding first url {} to pages".format(url))
    page_links = [url] # The <a> links with the exception of the first url
    page_urls = set(url) # Just the http://foo.com/blah strings
    while True:
        try:
            r = http.request('GET', url)
        except urllib3.exceptions.SSLError as e:
            print(e)
        soup = BeautifulSoup(r.data)
        links = soup.find_all('a', href=True)
        if not links:
            return []
        # looking for 'next', '>', 'nav', as rel or text or class
        links.sort(key=likelyhood_being_next_button)
        links.reverse()
        next_button = links[0]
        # import pdb; pdb.set_trace();
        if likelyhood_being_next_button(next_button) == 0:
            break
        else:
            if next_button['href'] in page_urls:
                break
            url = next_button['href']
            log.debug("Adding url {} to pages".format(url))
            page_links.append(next_button)
            page_urls.add(next_button['href'])


    return page_links


def likelyhood_being_next_button(link):
    # import pdb; pdb.set_trace();
    keywords = ['next', '>', 'nav']
    negative_keywords = ['http']
    likelyhood = 0
    # import pdb; pdb.set_trace();
    for k in keywords:
        if k in link.text:
            likelyhood += 1
        if 'rel' in link.attrs and k in link['rel']:
            likelyhood += 1
        if 'class' in link.attrs and k in link['class']:
            likelyhood += 1
    for k in negative_keywords:
        if k in link.text:
            likelyhood -= 1
    return likelyhood

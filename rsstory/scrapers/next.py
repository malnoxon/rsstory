import urllib3
import urllib.parse
from functools import partial
from bs4 import BeautifulSoup
import py_stringmatching as sm
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
    prev_next_button = None
    tokenizer = sm.QgramTokenizer(qval=3, return_set=True) #return_set=False gives a bag of tokens instead of a set
    measure = sm.Jaccard()
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
        # if url == "http://dresdencodak.com/2014/10/06/dark-science-35/":
        #     import pdb; pdb.set_trace();
        links.sort(key=partial(likelyhood_being_next_button, prev_next_button, tokenizer, measure))
        links.reverse()
        next_button = links[0]
        # import pdb; pdb.set_trace();
        if likelyhood_being_next_button(prev_next_button, tokenizer, measure, next_button) == 0:
            break
        else:
            joined_url = urllib.parse.urljoin(url, next_button['href'])
            if joined_url in page_urls:
                break
            url = joined_url
            log.debug("Adding url {} to pages".format(url))
            page_links.append(next_button)
            page_urls.add(joined_url)
            prev_next_button = next_button

    return page_links


def likelyhood_being_next_button(prev_next_button, tokenizer, measure, link):
    keywords = ['next', '>', 'nav', '&gt;', 'NEXT', 'Next']
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
        try:
            if k in link.img['src']:
                likelyhood += 1
        except TypeError:
            pass
        except KeyError:
            pass
        if prev_next_button == link:
            likelyhood += 1
    if prev_next_button:
        prev_tokens = tokenizer.tokenize(str(prev_next_button))
        new_tokens = tokenizer.tokenize(str(link))
        similarity = measure.get_raw_score(prev_tokens, new_tokens)
        if similarity > 0.6:
            likelyhood += similarity

    for k in negative_keywords:
        if k in link.text:
            likelyhood -= 1
    return likelyhood

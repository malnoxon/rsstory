import urllib3
from bs4 import BeautifulSoup
import certifi
from tld import get_tld
import re
import logging
import rsstory.scrapers.tools as tools

log = logging.getLogger(__name__)

http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where(),
        )

def is_wordpress(url):
    if get_tld(url) == "wordpress.com":
        log.debug("Returning true since tld is wordpress.com")
        return True

    try:
        r = http.request('GET', url)
    except urllib3.exceptions.SSLError as e:
        print(e)
        return False

    match = re.search("powered by wordpress", str(r.data), re.IGNORECASE)
    if match:
        log.debug("Returning true since 'powered by wordpress found'")
        return True

    return False

def get_monthly_archive_urls(links, page_url):
    '''Scans the provided links for wordpress style archives which are of
    the form website.com/yyyy/mm/'''
    log.info("Getting monthly archive urls")
    domain = get_tld(page_url)
    monthly_archive_urls = []
    for link in links:
        # Try for drop down lists using <option value="url.com/...">
        try:
            url = link.attrs['value']
            match = re.search(domain + "/\d{4}/\d{2}/$", url)
            if match:
                monthly_archive_urls.append(url)

        except KeyError:
            pass

        # Try for actual <a href="url.com/..." > links
        try:
            url = link.attrs['href']
            match = re.search(domain + "/\d{4}/\d{2}/$", url)
            if match:
                monthly_archive_urls.append(url)

        except KeyError:
            pass

    log.info("Returning monthly archive urls")
    return list(set(monthly_archive_urls))

def get_post_from_month(month_url):
    '''Returns the individual posts from the input monthly archive url'''
    log.debug("Getting posts from month url: {}".format(month_url))
    try:
        r = http.request('GET', month_url)
    except urllib3.exceptions.SSLError as e:
        print(e)
    soup = BeautifulSoup(r.data) #TODO different parser?
    links = soup.find_all('a', href=True)

    post_links = []
    for link in links:
        try:
            url = link.attrs['href']
            match = re.search(tools.clean_url(month_url) + "\d{2}", url)
            if match:
                post_links.append(link)

        except KeyError:
            pass

    log.debug("Posts from month url: {} are \n {}".format(month_url, post_links))
    return post_links

def remove_duplicates(links):
    out = []
    for link in links:
        if not any([link for x in out if x.attrs['href'] == link.attrs['href']]):
            out.append(link)

    return out

def remove_substrings(strings):
    out = []
    for s in strings:
        if not any([s.attrs['href'] in x.attrs['href'] for x in strings if x.attrs['href'] != s.attrs['href']]):
            out.append(s)

    return out

def scrape(url):
    try:
        r = http.request('GET', url)
    except urllib3.exceptions.SSLError as e:
        print(e)
    soup = BeautifulSoup(r.data)

    # Find the monthly archive urls
    links = soup.find_all('a', href=True)
    links.extend(soup.find_all('option', value=True))
    monthly_archive_urls = get_monthly_archive_urls(links, url)
    monthly_archive_urls.sort()
    log.debug("Montly archive urls: {}".format(monthly_archive_urls))

    posts = []
    for link in monthly_archive_urls:
        posts.extend(get_post_from_month(link))

    # Remove duplicates and links that don't go to the post itself
    posts = remove_duplicates(posts)
    posts.sort(key=lambda x: x.attrs['href'])
    posts = [p for p in posts if "#comment" not in p.attrs['href'] and "#more" not in p.attrs['href'] and "#respond" not in p.attrs['href']]
    posts = remove_substrings(posts)
    
    return posts

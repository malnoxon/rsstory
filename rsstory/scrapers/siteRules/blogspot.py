import urllib3
from bs4 import BeautifulSoup
import certifi
from tld import get_tld
import re

http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where(),
        )

def get_monthly_archive_urls(links, page_url):
    '''Scans the provided links for blogspot style archives which are of
    the form website.com/yyyy_dd_01_archive.html'''
    domain = get_tld(page_url)
    monthly_archive_urls = []
    for link in links:
        # Try for drop down lists using <option value="url.com/...">
        try:
            url = link.attrs['value']
            match = re.search(domain + "/\d{4}_\d{2}_01_archive.html", url)
            if match:
                monthly_archive_urls.append(url)

        except KeyError:
            pass

        # Try for actual <a href="url.com/..." > links
        try:
            url = link.attrs['href']
            match = re.search(domain + "/\d{4}_\d{2}_01_archive.html", url)
            if match:
                monthly_archive_urls.append(url)

        except KeyError:
            pass

    return list(set(monthly_archive_urls))

def get_post_from_month(month_url):
    '''Returns the individual posts from the input monthly archive url'''
    try:
        r = http.request('GET', month_url)
    except urllib3.exceptions.SSLError as e:
        print(e)
    soup = BeautifulSoup(r.data)
    links = soup.find_all('a', href=True)

    month_url_base = "/".join(month_url.split("/")[:3])
    year = month_url.split("/")[3][0:4]
    month = month_url.split("/")[3][5:7]

    post_links = []
    for link in links:
        try:
            url = link.attrs['href']
            match = url.startswith(month_url_base + "/" + year + "/" + month + "/")
            if match:
                post_links.append(link)

        except KeyError:
            pass

    post_links.reverse() # Reverse the order to get oldest posts first
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

    posts = []
    for link in monthly_archive_urls:
        posts.extend(get_post_from_month(link))

    # Remove duplicates and links that don't go to the post itself
    posts = remove_duplicates(posts)
    bad_indicators = ["#comment", "#more", "#respond", "#disqus_thread", "#links"]
    posts = [p for p in posts if not any(bi in p.attrs['href'] for bi in bad_indicators )]
    posts = remove_substrings(posts)
    
    return posts

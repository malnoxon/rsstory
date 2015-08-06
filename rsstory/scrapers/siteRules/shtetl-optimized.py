import rsstory.scrapers.monthly_sidebar as monthly_sidebar

def scrape(url):
    links = monthly_sidebar.scrape(url)
    links = [url] #temporary

    date_types = ["MMMM, Dnd, YYYY", "MMMM, Dst, YYYY"]
    #TODO: go into each url in month_links and grab all the urls from that page and 
    # build that into an rss feed

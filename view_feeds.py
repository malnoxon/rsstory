import pickle
import sys

def print_feed(fpath):
    rss_items, url, title = pickle.load(open(fpath, "rb"))
    print("Title {}".format(title))
    print("URL: {}".format(url))
    print("ITEMS:")
    for i, item in enumerate(rss_items):
        print(str(i) + ":\t" + item.title + " " + item.link)

if __name__ == "__main__":
    print_feed(sys.argv[1])

# encoding: utf-8

import yaml
from xml.etree.ElementTree import ElementTree
import urllib2
import simplejson
import hashlib
import time
from urlparse import urlparse

settings_file = open("settings.yml").read()
settings = list(yaml.load_all(settings_file))[0]

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
ONE_DAY = 86400

cache_opts = {
    'cache.type': 'file',
    'cache.data_dir': '/tmp/cache/data',
    'cache.lock_dir': '/tmp/cache/lock'
}

cache = CacheManager(**parse_cache_config_options(cache_opts))

def get_backtweets():
    base = "http://backtweets.com/search.json?q=http://stdout.be&key=" + settings["BACKTWEETS_API_KEY"]
    body = urllib2.urlopen(base).read()
    return simplejson.loads(body)

@cache.cache('delicious_info', expire=ONE_DAY)
def get_delicious_info(url):
    url = hashlib.md5(url).hexdigest()
    base = "http://feeds.delicious.com/v2/json/urlinfo/" + url
    body = urllib2.urlopen(base).read()
    json = simplejson.loads(body)
    # let's be civil to delicious
    time.sleep(0.1)
    if len(json):
        print json
        return json[0]
    else:
        return None

def get_old_url(new_url):
    parts = new_url.split("/")
    return parts[1] + "/" + "/".join(parts[4:])

def get_bookmark_count(urlinfo):
    if urlinfo:
        return urlinfo["total_posts"]
    else:
        return 0

def get_permalinks():
    tree = ElementTree()
    root = tree.parse("../public/sitemap.xml")
    posts = {}
    for entry in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
        title = entry.find("{http://www.sitemaps.org/schemas/sitemap/0.9}title").text
        genre = entry.find("{http://www.sitemaps.org/schemas/sitemap/0.9}genre").text
        loc = entry.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
        loc = urlparse(loc).path
        posts[loc] = {"title": title, "genre": genre}
    return posts

def add_delicious_info(info):
    for link in info.keys():
        # old url structure
        parts = link.split("/")
        if int(parts[1]) < 2011:
            old_url = "http://stdout.be/" + get_old_url(link)
            info[link]["old_delicious_count"] = get_bookmark_count(get_delicious_info(old_url))
        else:
            info[link]["old_delicious_count"] = 0
        
        url = "http://stdout.be" + link
        info[link]["delicious_count"] = get_bookmark_count(get_delicious_info(url))

    return info

def get_post_info():
    # permalinks
    info = get_permalinks()
    # GA
    # ?
    # tweets
    # ?
    # delicious
    info = add_delicious_info(info)
  
    # comments
    return info
import redis
import json
import zipfile
from io import BytesIO, StringIO
from urllib.request import urlopen
from datetime import datetime
from subprocess import check_output
import sys

ALEXA_DATA_URL = 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'

def alexa_etl():
    """
    Generator that:
        Extracts by downloading the csv.zip, unzipping.
        Transforms the data into python via CSV lib
        Loads it to the end user as a python list
    """

    f = urlopen(ALEXA_DATA_URL)
    buf = BytesIO(f.read())
    zfile = zipfile.ZipFile(buf)
    with zfile.open('top-1m.csv') as f:
        for line in f.readlines():
            (rank, domain) = line.decode('utf-8').split(',')
            yield (int(rank), domain.strip())


def twitter_etl():
    """
    Generate the output of the node based twitter article scraper.
    """
    urls = check_output(['node','getarticles.js'],cwd="../popular-articles-twitter/")
    for line in urls.decode('utf-8').strip().split('\n'):
        yield line

def todays_urls(browsers, treatments, num=1000):
    """
    Dump today's alexa up to num into various redis queues for consumption
    by the scrapers.
    """
    now = datetime.now() # current date and time
    today = now.strftime("%Y%m%d")
    conn = redis.Redis("redis.kaytwo.org")
    a = alexa_etl()
    urls = ['http://' + next(a)[1] for x in range(num)]
    for url in urls:
        for b in browsers:
            for t in treatments:
                obj = {'channel':'alexa','date': today, 'url': url}
                conn.rpush("queue:%s:%s" % (b, t),json.dumps(obj))
    # for testing, if num!=1000 don't do twitter stuff
    if num!=1000:
        return
    # FIXME: just consume all of the twitter URLs no matter what for now
    for url in twitter_etl():
        for b in browsers:
            for t in treatments:
                obj = {'channel':'twitter','date': today, 'url': url}
                conn.rpush("queue:%s:%s" % (b, t),json.dumps(obj))

if __name__ == '__main__':
    if len(sys.argv) == 2:
        length = int(sys.argv[1])
    else:
        length = 1000
    todays_urls(['chrome','safari','chrome-ubo','chrome-brave','firefox'],['3','4'],length)

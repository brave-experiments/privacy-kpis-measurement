import redis
import json
import zipfile
from io import BytesIO, StringIO
from urllib.request import urlopen
from datetime import datetime

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



def todays_alexa(browsers, treatments, num=1000):
    """
    Dump today's alexa up to num into various redis queues for consumption
    by the scrapers.
    """
    now = datetime.now() # current date and time
    today = now.strftime("%Y%m%d")
    a = alexa_etl()
    urls = ['http://' + next(a)[1] for x in range(num)]
    conn = redis.Redis("192.168.1.13")
    for url in urls:
        for b in browsers:
            for t in treatments:

                obj = {'channel':'alexa','date': today, 'url': url}
                conn.rpush("queue:%s:%s" % (b, t),json.dumps(obj))


if __name__ == '__main__':
    todays_alexa(['chrome','safari'],['1','2'])

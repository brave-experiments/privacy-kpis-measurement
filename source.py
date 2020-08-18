#!/usr/bin/env python3
import redis
import json
import zipfile
from io import BytesIO, StringIO
from urllib.request import urlopen
from datetime import datetime
from subprocess import check_output
import sys
from concurrent.futures import ThreadPoolExecutor
import asyncio

import requests

ALEXA_DATA_URL = 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'
HEADERS = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/84.0.4147.111 Safari/537.36"
}


def fetch(session, url):
    try:
        with session.get(url, timeout=(5, 1), headers=HEADERS) as response:
            return response.url
    except requests.exceptions.RequestException as e:
        return url


async def end_urls(urls):
    with ThreadPoolExecutor(max_workers=None) as executor:
        with requests.Session() as session:
            loop = asyncio.get_running_loop()
            tasks = []
            for url in urls:
                a_task = loop.run_in_executor(
                    executor,
                    fetch,
                    *(session, url)
                )
                tasks.append(a_task)
            return await asyncio.gather(*tasks)


async def alexa_etl(num=1000):
    """
    Generator that:
        Extracts by downloading the csv.zip, unzipping.
        Transforms the data into python via CSV lib
        Loads it to the end user as a python list
    """

    f = urlopen(ALEXA_DATA_URL)
    buf = BytesIO(f.read())
    zfile = zipfile.ZipFile(buf)
    line_count = 0
    urls = []
    with zfile.open('top-1m.csv') as f:
        for line in f.readlines():
            (rank, domain) = line.decode('utf-8').split(',')
            urls.append("http://" + domain.strip())
            line_count += 1
            if line_count == num:
                break
    return await end_urls(urls)


async def twitter_etl(num=1000):
    """
    Generate the output of the node based twitter article scraper.
    """
    twitter_urls = check_output(['node','getarticles.js'],
                                cwd="../popular-articles-twitter/")
    urls = twitter_urls.decode('utf-8').strip().split('\n')[:num]
    return await end_urls(urls)


async def todays_urls(browsers, treatments, num=1000):
    """
    Dump today's alexa up to num into various redis queues for consumption
    by the scrapers.
    """
    now = datetime.now() # current date and time
    today = now.strftime("%Y%m%d")
    conn = redis.Redis("redis.kaytwo.org")
    alexa_urls = await alexa_etl(num=num)
    for url in alexa_urls:
        for b in browsers:
            for t in treatments:
                obj = {'channel':'alexa','date': today, 'url': url}
                conn.rpush("queue:%s:%s" % (b, t), json.dumps(obj))
    # for testing, if num!=1000 don't do twitter stuff
    if num!=1000:
        return
    # FIXME: just consume all of the twitter URLs no matter what for now
    twitter_urls = await twitter_etl(num=num)
    for url in twitter_urls:
        for b in browsers:
            for t in treatments:
                obj = {'channel':'twitter','date': today, 'url': url}
                conn.rpush("queue:%s:%s" % (b, t), json.dumps(obj))


if __name__ == '__main__':
    if len(sys.argv) == 2:
        length = int(sys.argv[1])
    else:
        length = 1000
    asyncio.run(todays_urls(['chrome','safari','chrome-ubo','chrome-brave','firefox'],['3','4'],length))

import redis
from datetime import datetime
queue_host = 'redis.kaytwo.org'
now = datetime.now() # current date and time
today = now.strftime("%Y%m%d")
outfile = 'privacykpis.{}.json'.format(today)
while True:
    conn = redis.Redis(queue_host)
    packed = conn.blpop(['queue:output'],90)
    if not packed:
        # if no results received in last 90 seconds, exit
        break
    
    with open(outfile,'a') as f:
        f.write(packed[1].decode("utf-8") + "\n")

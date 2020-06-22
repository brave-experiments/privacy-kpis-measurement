import redis
queue_host = 'redis.kaytwo.org'
outfile = 'output.json'
while True:
    conn = redis.Redis(queue_host)
    packed = conn.blpop(['queue:output', 30])
    if not packed:
        continue
    
    with open(outfile,'a') as f:
        f.write(packed[1].decode("utf-8") + "\n")

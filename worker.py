import os

import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

REDIS_DEFAULT_CONNECTION_POOL = redis.ConnectionPool.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/'))

conn = redis.from_url(REDIS_DEFAULT_CONNECTION_POOL)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
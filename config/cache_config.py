"""
Created by tareq on 10/9/17
"""

__author__ = 'Tareq'

CACHES = {
    'default': {
        #############################################################################################################
        #
        # Used Redis as cache backend, and used socket connection instead of TSC connection for better performance.
        #
        #   Guide to setup:
        #
        #   1. Install redis: sudo apt install redis-server
        #   2. Configure socket connection: in /etc/redis/redis.conf file
        #       2.1. comment out these lines: 'port 6379' and 'bind 127.0.0.1'
        #       2.2. Uncomment these lines: 'unixsocket /var/run/redis/redis.sock' and 'unixsocketperm 700'
        #       2.3. Change the permission of Socket: change 'unixsocketperm 700' to 'unixsocketperm 777'
        #   3. Restart Redis server: service redis-server restart
        #   4. Test Redis server: "redis-cli ping". You should get the response: "PONG"
        #
        #############################################################################################################

        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': '/var/run/redis/redis.sock',
    }
}

LOG_CACHE_TIMING = True
MIN_DURATION_CACHE_LOG = 500  # in millisecond
CACHE_LOG_FILE_PATH = 'redis_log.csv'

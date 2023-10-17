from functools import lru_cache
from funboost.utils import RedisMixin


class ProxyGetterConfig:
    PROXY_KEY_IN_REDIS_DEFAULT = 'proxy_free'
    REQUESTS_TIMEOUT = 5

@lru_cache()
def get_redis():
    return RedisMixin().redis_db_frame




from functools import lru_cache
from funboost.utils import RedisMixin

global_dict = {'PROXY_KEY_IN_REDIS_DEFAULT': 'proxy_free',
               'REQUESTS_TIMEOUT': 5
               }


@lru_cache()
def get_redis():
    return RedisMixin().redis_db_frame


def get_redis_key():
    return global_dict['PROXY_KEY_IN_REDIS_DEFAULT']

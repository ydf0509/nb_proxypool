import typing
import time

import nb_log
import requests
import json

from boost_spider import RequestClient
from nb_proxypool.proxy_pool_config import get_redis, get_redis_key, global_dict
from funboost import boost, BrokerEnum, ConcurrentModeEnum

# CHECK_PROXY_VALIDITY_URL = 'https://www.sohu.com/sohuflash_1.js'
CHECK_PROXY_VALIDITY_URL = 'https://www.baidu.com/'

logger = nb_log.get_logger('proxy_check',log_filename='proxy_check.log')
logger_proxy_error = nb_log.get_logger('proxy_error',log_filename='proxy_error.log')

@boost('check_one_new_proxy', qps=100, broker_kind=BrokerEnum.REDIS, concurrent_num=300)
def check_one_new_proxy(proxy_dict, is_save_to_db=True, exist_proxy=False):
    is_valid = False
    try:
        # print(proxy_dict)
        RequestClient(using_platfrom=proxy_dict['platform'], request_retry_times=0).get(CHECK_PROXY_VALIDITY_URL,
                                                                                        timeout=global_dict[
                                                                                            'REQUESTS_TIMEOUT'],
                                                                                        proxies=proxy_dict,
                                                                                        verify=False)
        is_valid = True
    except Exception as e:
        logger_proxy_error.warning(e)
        pass
    new_proxy_str = '旧代理' if exist_proxy else '新代理'
    if is_valid:
        logger.info(f' {proxy_dict} {new_proxy_str} 有效')
    else:
        logger.warning(f' {proxy_dict} {new_proxy_str} 无效')
    if is_save_to_db and is_valid:
        get_redis().zadd(get_redis_key(), {json.dumps(proxy_dict, ensure_ascii=False): time.time()})
    if is_save_to_db and is_valid is False:
        get_redis().zrem(get_redis_key(), json.dumps(proxy_dict, ensure_ascii=False))
    return is_valid


@boost('check_one_exist_proxy', qps=100, broker_kind=BrokerEnum.REDIS, concurrent_num=400)
def check_one_exist_proxy(proxy_dict, is_save_to_db=True):
    return check_one_new_proxy(proxy_dict, is_save_to_db, exist_proxy=True)


@boost('scan_exists_proxy', broker_kind=BrokerEnum.REDIS,concurrent_mode=ConcurrentModeEnum.SINGLE_THREAD)
def scan_exists_proxy():
    proxy_dict_str_list = get_redis().zrangebyscore(get_redis_key(), 0, time.time() - 5)
    for proxy_dict_str in proxy_dict_str_list:
        check_one_exist_proxy.push(json.loads(proxy_dict_str))

@boost('show_proxy_count', broker_kind=BrokerEnum.REDIS,concurrent_mode=ConcurrentModeEnum.SINGLE_THREAD)
def show_proxy_count():
    count = get_redis().zcount(get_redis_key(),0,time.time())
    logger.info(f'当前共有 {count} 个 代理')
    return count




import json
import random

from boost_spider.http.request_client import RequestClient
from nb_proxypool.proxy_pool_config import redis_client,PROXY_KEY_IN_REDIS_DEFAULT

class MyRequestClient(RequestClient):
    def _request_with_free_proxy(self, method, url, verify=None, timeout=None, headers=None, cookies=None, **kwargs):
        """使用redis中的快代理池子,怎么从redis拿代理ip和requests怎么使用代理，用户自己写"""
        res = redis_client.zrange(PROXY_KEY_IN_REDIS_DEFAULT,0,-1)
        if len(res) == 0:
            err_msg = f'request_with_free_proxy redis {PROXY_KEY_IN_REDIS_DEFAULT} 键中没有代理ip'
            self.logger.error(err_msg)
            raise Exception(err_msg)
        proxies = json.loads(random.choice(res))
        resp = self.ss.request(method, url, verify=verify or self._verify, timeout=timeout or self._timeout,
                               headers=headers, cookies=cookies,
                               proxies=proxies, **kwargs)

        return resp

    PROXY_FREE = 'free'
    PROXYNAME__REQUEST_METHED_MAP = {'noproxy': RequestClient._request_with_no_proxy,
                                     'abuyun': RequestClient._request_with_abuyun_proxy,
                                     'kuai': RequestClient._request_with_kuai_proxy,
                                     'free':_request_with_free_proxy,
                                     }  # 用户新增了方法后，在这里添加代理名字和请求方法的映射映射





if __name__ == '__main__':
    MyRequestClient(proxy_name_list=[
                                     MyRequestClient.PROXY_FREE,MyRequestClient.PROXY_NOPROXY]).get('https://www.kuaidaili.com/free/intr/1')
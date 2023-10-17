import json
import random

from boost_spider.http.request_client import RequestClient
from proxy_pool_config import get_redis, ProxyGetterConfig


class ProxyClient(RequestClient):
    def _request_with_free_proxy(self, method, url, verify=None, timeout=None, headers=None, cookies=None, **kwargs):
        """使用redis中的快代理池子,怎么从redis拿代理ip和requests怎么使用代理，用户自己写"""
        res = get_redis().zrange(ProxyGetterConfig.PROXY_KEY_IN_REDIS_DEFAULT, 0, -1)
        if len(res) == 0:
            err_msg = f'request_with_free_proxy redis {ProxyGetterConfig.PROXY_KEY_IN_REDIS_DEFAULT} 键中没有代理ip'
            self.logger.warning(err_msg)
            raise Exception(err_msg) # 报错是为了换成noproxy重试
        proxies = json.loads(random.choice(res))
        resp = self.ss.request(method, url, verify=verify or self._verify, timeout=timeout or self._timeout,
                               headers=headers, cookies=cookies,
                               proxies=proxies, **kwargs)

        return resp

    PROXY_FREE = 'free'
    PROXYNAME__REQUEST_METHED_MAP = {'noproxy': RequestClient._request_with_no_proxy,
                                     'free': _request_with_free_proxy,
                                     }  # 用户新增了方法后，在这里添加代理名字和请求方法的映射映射


if __name__ == '__main__':
    ProxyClient(proxy_name_list=[
        ProxyClient.PROXY_FREE, ProxyClient.PROXY_NOPROXY],request_retry_times=4).get('https://www.kuaidaili.com/free/intr/1')

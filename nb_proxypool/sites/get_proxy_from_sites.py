from boost_spider import RequestClient


class BaseProxyFromSite:
    site_name = None
    url_formate: str = None

    def __init__(self, url_fmt_params: dict = None):
        self.resp = None
        self.url = self.url_formate.format(url_fmt_params)
        self.proxy_list = []

    def _request(self):
        self.resp = RequestClient().get(url=self.url)

    def parse(self):
        raise NotImplementedError

    def get_proxies(self):
        self._request()
        if self.resp is not None:
            self.proxy_list = self.parse()
        return self.proxy_list


class ZjProxy(BaseProxyFromSite):
    site_name = 'zj'
    url_formate = 'https://zj.v.api.aa1.cn/api/proxyip/'

    def parse(self):
        return self.resp.re_findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+')


if __name__ == '__main__':
    print(ZjProxy().get_proxies())

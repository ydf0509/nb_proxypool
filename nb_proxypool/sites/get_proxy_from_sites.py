import json
import typing
import nb_log

from boost_spider import RequestClient
from boost_spider.http.request_client import SpiderResponse

from pyquery import PyQuery as pq
import re

from nb_proxypool.my_request_client import MyRequestClient
from nb_proxypool.proxy_check import check_one_new_proxy


class BaseProxyFromSiteGetter(nb_log.LoggerMixin):
    site_name = None
    url_formatter: str = None
    support_page = False

    @classmethod
    def class_name(cls):
        return str(cls.__name__).split('.')[-1]

    def __init__(self, page=1,proxy_type=None, ):
        self.resp = None
        kwargs = {}
        kwargs['page'] = page
        kwargs['proxy_type'] = proxy_type
        self.page = page
        self.kwargs = kwargs
        self.logger.debug(kwargs)
        self._format_the_url()
        self.proxy_list = []  # type: typing.List[str]
        self.proxy_dict_list_valid = []  # type: typing.List[dict]

    def _format_the_url(self):
        self.url = self.url_formatter.format(**self.kwargs)

    def _request(self):
        self.resp = MyRequestClient(proxy_name_list=[MyRequestClient.PROXY_FREE,
                                                     MyRequestClient.PROXY_NOPROXY],
                                    using_platfrom=self.site_name,request_retry_times=6).get(url=self.url)  # type: SpiderResponse

    def _parse(self):
        """部分网站的通用提取，如果不通用需要重写"""
        """ 适用于这样的网页
          <td>139.196.214.238</td>
                    <td>2087</td>
        """
        res = re.findall('<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', self.resp.text)
        for r in res:
            self.proxy_list.append(f'{r[0]}:{r[1]}')

    def get_proxies(self):
        if self.support_page is False and self.page > 1:
            return
        self._request()
        if self.resp is not None:
            self._parse()
            # self.proxy_list= self._parse() or []
        self._check_all_proxies()
        return self.proxy_list

    def _check_all_proxies(self):
        for proxy in self.proxy_list:
            proxy_dict = {'https': f'{proxy}', 'http': f'{proxy}', 'platform': self.site_name}
            check_one_new_proxy.push(proxy_dict, )
            # if is_valid:
            #     self.proxy_dict_list_valid.append(proxy_dict)


def get_proxy_getter_cls(site_proxy_cls_name):
    site_proxy_cls = globals()[site_proxy_cls_name]  # type:type[BaseProxyFromSiteGetter]
    return site_proxy_cls


class ZjProxy(BaseProxyFromSiteGetter):
    '''
    代理非常非常垃圾，完全不可用。
    '''
    site_name = 'zj'
    url_formatter = 'https://zj.v.api.aa1.cn/api/proxyip/'
    support_page = False

    def _parse(self):
        self.proxy_list = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+', self.resp.text)


class Kuaidaili(BaseProxyFromSiteGetter):
    site_name = 'kuaidaili'
    url_formatter = 'https://www.kuaidaili.com/free/intr/{page}/'  # 页码从1开始  intr  inha
    support_page = True

    def _parse(self):
        '''
            <td data-title="IP">182.34.102.15</td>
                            <td data-title="PORT">9999</td>
        :return:
        '''
        # self.logger.debug(self.resp.text)
        p_list = re.findall('<td data-title="IP">(.*?)</td>[\s\S]*?<td data-title="PORT">(.*?)</td>', self.resp.text)
        for t in p_list:
            self.proxy_list.append(f'{t[0]}:{t[1]}')


class Ip66(BaseProxyFromSiteGetter):
    """
    一个代理没有，垃圾
    """
    site_name = '66ip'
    url_formatter = 'http://www.66ip.cn/{page}.html'
    support_page = True

    def _parse(self):
        doc = pq(self.resp.text)
        trs = doc('.containerbox table tr:gt(0)').items()
        for tr in trs:
            ip = tr.find('td:nth-child(1)').text()
            port = tr.find('td:nth-child(2)').text()
            self.proxy_list.append(':'.join([ip, port]))


class Ip3366(BaseProxyFromSiteGetter):
    '''
    很差劲
    '''
    site_name = 'ip3366'
    url_formatter = 'http://www.ip3366.net/?stype={proxy_type}&page={page}.html'  # 种类 1 2 加页面
    support_page = True

    find_tr = re.compile('<tr>(.*?)</tr>', re.S)

    def _format_the_url(self):
        self.url = self.url_formatter.format(**{'page': self.page, 'proxy_type': self.kwargs['proxy_type']})

    def _parse(self):
        trs = self.find_tr.findall(self.resp.text)
        for s in range(1, len(trs)):
            find_ip = re.compile('<td>(\d+\.\d+\.\d+\.\d+)</td>')
            re_ip_address = find_ip.findall(trs[s])
            find_port = re.compile('<td>(\d+)</td>')
            re_port = find_port.findall(trs[s])
            for address, port in zip(re_ip_address, re_port):
                address_port = address + ':' + port
                self.proxy_list.append(address_port.replace(' ', ''))



class Xici(BaseProxyFromSiteGetter):
    site_name = 'xici'
    url_formatter = 'https://www.xicidaili.com/wn/{page}'
    support_page = True

    find_tr = re.compile('<tr>(.*?)</tr>', re.S)

    def _parse(self):
        trs = self.find_tr.findall(self.resp.text)
        for s in range(1, len(trs)):
            find_ip = re.compile('<td>(\d+\.\d+\.\d+\.\d+)</td>')
            re_ip_address = find_ip.findall(trs[s])
            find_port = re.compile('<td>(\d+)</td>')
            re_port = find_port.findall(trs[s])
            for address, port in zip(re_ip_address, re_port):
                address_port = address + ':' + port
                self.proxy_list.append(address_port.replace(' ', ''))



class Ip89(BaseProxyFromSiteGetter):
    """ 89免费代理
    可以
    """
    site_name = '89ip'
    url_formatter = 'https://www.89ip.cn/index_{page}.html'
    support_page = True

    def _parse(self):
        # self.logger.info(self.resp.text)
        proxies = re.findall(
            r'<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>[\s\S]*?(\d+)[\s\S]*?</td>',
            self.resp.text)
        for proxy in proxies:
            self.proxy_list.append(':'.join(proxy))


class Ihuan(BaseProxyFromSiteGetter):
    """ 小幻代理
    不错
    """
    site_name = 'ihuan'
    url_formatter = 'https://ip.ihuan.me/address/5Lit5Zu9.html?page={page}'
    support_page = True

    def _parse(self):
        # self.logger.info(self.resp.text)
        proxies = re.findall(r'>\s*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*?</a></td><td>(\d+)</td>', self.resp.text)
        for proxy in proxies:
            self.proxy_list.append(':'.join(proxy))


class Fatezero(BaseProxyFromSiteGetter):
    '''
    垃圾
    '''
    site_name = 'fatezero'
    url_formatter = 'http://proxylist.fatezero.org/proxy.list'  # 不能分页
    support_page = False

    def _parse(self):
        for each in self.resp.text.split("\n"):
            if not each.startswith('{'):
                continue
            json_info = json.loads(each)
            if json_info.get("country") == "CN":
                self.proxy_list.append("%s:%s" % (json_info.get("host", ""), json_info.get("port", "")))


class Kaixin(BaseProxyFromSiteGetter):
    """
    不错
    """
    site_name = 'kaixin'
    url_formatter = 'http://www.kxdaili.com/dailiip/{proxy_type}/{page}.html'  # 可以同时分类和分页
    support_page = True


class Zdaye(BaseProxyFromSiteGetter):
    """
    不错
    """
    site_name = 'zdaye'
    url_formatter = 'https://www.zdaye.com/free/?ip=&adr=&checktime=&sleep=&cunhuo=&dengji=&nadr=&https=1&yys=&post=&px='  # 不分页
    support_page = False


class Uqidata(BaseProxyFromSiteGetter):
    '''不行'''
    site_name = 'uqidata'
    url_formatter = 'https://ip.uqidata.com/free/index.html'  # 不分页
    support_page = False


class Proxyhub(BaseProxyFromSiteGetter):
    """
    不可用
    """
    site_name = 'proxyhub'
    url_formatter = 'https://proxyhub.me/'  # 不分页
    support_page = False


# class Atomintersoft(BaseProxyFromSiteGetter):
#
#     site_name = 'atomintersoft'
#     url_formatter = 'https://atomintersoft.com/{proxy_type}_proxy_list'  # ['transparent', 'anonymous', 'high_anonymity_elite']
#
#     def _parse(self):
#         urls = ['https://atomintersoft.com/%s_proxy_list' % n for n in
#                 ['transparent', 'anonymous', 'high_anonymity_elite']]
#         request = WebRequest()
#         for url in urls:
#             tree = request.get(url, timeout=10).tree
#             for proxy in tree.xpath("//table/thead/tr//td[1]/text()[1]"):
#                 if proxy:
#                     yield proxy

class Cool(BaseProxyFromSiteGetter):
    """不行"""
    site_name = 'cool'
    url_formatter = 'https://cool-proxy.net/proxies.json'  # 不能分页
    support_page = False

    def _parse(self):
        for proxy in json.loads(self.resp.text):
            ip = proxy['ip']
            port = proxy['port']
            if ip:
                self.proxy_list.append("%s:%s" % (ip, port))


class Beesproxy(BaseProxyFromSiteGetter):
    """
    不错
    """
    site_name = 'beesproxy'
    url_formatter = 'https://www.beesproxy.com/free/page/{page}'
    support_page = True

    def _format_the_url(self):
        if self.page == 1:
            self.url = 'https://www.beesproxy.com/free'
        else:
            self.url = self.url_formatter.format(**self.kwargs)


if __name__ == '__main__':
    for p in range(1, 5):
        for proxy_type in (1, 2):
            get_proxy_getter_cls(Ip89.class_name())(page=p, proxy_type=proxy_type).get_proxies()

    # print(Beesproxy.class_name())

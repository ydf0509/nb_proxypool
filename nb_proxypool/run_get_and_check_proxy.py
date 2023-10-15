import time

from funboost import boost, BrokerEnum, funboost_aps_scheduler

from nb_proxypool.sites.get_proxy_from_sites import *
from proxy_check import check_one_new_proxy, check_one_exist_proxy, scan_exists_proxy


@boost('get_proxies_from_sites', broker_kind=BrokerEnum.REDIS, qps=0.5)
def get_proxies_from_sites(site_proxy_kls_name: str, page, proxy_type=1, ):
    get_proxy_getter_kls(site_proxy_kls_name)(page=page, proxy_type=proxy_type).get_proxies()


if __name__ == '__main__':
    funboost_aps_scheduler.start()
    for p in range(1, 5):
        for site_kls in [Kuaidaili, Xici, Ip89, Ihuan, Zdaye, Beesproxy]:
            if site_kls.support_page or (site_kls.support_page is False and p == 1):
                # 页数越靠后的，定时运行间隔越大，因为页数靠后的很少更新
                funboost_aps_scheduler.add_push_job(get_proxies_from_sites, 'interval', seconds=p * 60,
                                                    kwargs={"site_proxy_kls_name": site_kls.class_name(),
                                                            "page": p})
    for p in range(1, 5):
        for proxy_type in [1, 2]:
            funboost_aps_scheduler.add_push_job(get_proxies_from_sites, 'interval', seconds=60 * p,
                                                kwargs={"site_proxy_kls_name": Kaixin.class_name(),
                                                        "page": p, "proxy_type": proxy_type})

    funboost_aps_scheduler.add_push_job(scan_exists_proxy, 'interval', seconds=30, )

    get_proxies_from_sites.consume()
    check_one_new_proxy.consume()
    scan_exists_proxy.consume()
    check_one_exist_proxy.consume()

    while 1:
        time.sleep(10)

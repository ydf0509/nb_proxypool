import time

from funboost import boost, BrokerEnum, funboost_aps_scheduler

from proxy_from_sites_parse import *

from proxy_check import check_one_new_proxy, check_one_exist_proxy, scan_exists_proxy, show_proxy_count


@boost('get_proxies_from_sites', broker_kind=BrokerEnum.REDIS, qps=0.5, is_print_detail_exception=False)
def get_proxies_from_sites(site_proxy_cls_name: str, page, proxy_type=1, ):
    get_proxy_getter_cls(site_proxy_cls_name)(page=page, proxy_type=proxy_type).get_proxies()


def run_funboost():
    funboost_aps_scheduler.start()

    ''' 定时任务推送代理抓取'''
    for p in range(1, 5):
        for site_cls in [Kuaidaili, Xici, Ip89, Ihuan, Zdaye, Beesproxy]:
            if site_cls.support_page or (site_cls.support_page is False and p == 1):
                # 页数越靠后的，定时运行间隔越大，因为页数靠后的很少更新
                funboost_aps_scheduler.add_push_job(get_proxies_from_sites, 'interval', seconds=p * 60,
                                                    kwargs={"site_proxy_cls_name": site_cls.class_name(),
                                                            "page": p})
    for p in range(1, 5):
        for proxy_type in [1, 2]:
            funboost_aps_scheduler.add_push_job(get_proxies_from_sites, 'interval', seconds=60 * p,
                                                kwargs={"site_proxy_cls_name": Kaixin.class_name(),
                                                        "page": p, "proxy_type": proxy_type})
    '''定时任务扫描存量代理'''
    funboost_aps_scheduler.add_push_job(scan_exists_proxy, 'interval', seconds=30, )
    funboost_aps_scheduler.add_push_job(show_proxy_count, 'interval', seconds=10, )

    get_proxies_from_sites.consume()  # 启动消费代理抓取
    check_one_new_proxy.consume()  # 启动消费检测1个新ip代理
    scan_exists_proxy.consume()  # 启动消费扫描存量代理
    check_one_exist_proxy.consume()  # 消启动费 检测一个旧ip代理
    show_proxy_count.consume()  # # 消启动费显示代理ip数量

    while 1:  # 阻止 funboost_aps_scheduler 守护线程退出
        time.sleep(10)


if __name__ == '__main__':
    run_funboost()

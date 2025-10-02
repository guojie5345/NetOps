# -*- coding: utf-8 -*-
class SangforApiClient:
    """
    深信服AD设备API客户端类，用于与深信服应用交付(AD)设备交互，获取DNAT配置和自定义地址组信息。

    该类封装了深信服AD设备的API调用基础操作，提供DNAT规则查询、自定义地址组查询等功能。
    """

    def __init__(self):
        """
        初始化SengforApiClient实例，配置AD设备API基础URL和认证请求头。

        设置深信服AD设备的API访问地址，并初始化包含Content-Type和Basic认证信息的请求头。
        """
        self.ad_url = "https://172.16.190.21"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic bmV0b3BzOkRhaWx5Y2hlY2sxMjMh"
        }

    def get_dnat(self):
        """
        获取深信服AD设备上的所有DNAT（目的地址转换）配置条目。

        通过调用AD设备API的DNAT列表接口，获取当前设备上配置的所有DNAT规则信息。

        :return: API响应对象，包含DNAT配置数据；请求失败时返回None
        """
        return api_call(f"{self.ad_url}/api/ad/v3/net/dnat/", method="get", headers=self.headers)

    def get_dnat_by_search(self, search=None):
        """
        根据搜索关键词查询深信服AD设备上的DNAT配置条目。

        通过在DNAT列表接口中附加搜索参数，筛选符合关键词的DNAT规则。

        :param search: 搜索关键词（如IP地址、端口等），为None时日志记录错误
        :return: API响应对象，包含匹配的DNAT配置数据；未指定搜索词或请求失败时返回None
        """
        if not search:
            return api_call(f"{self.ad_url}/api/ad/v3/net/dnat/?search={search}", method="get", headers=self.headers)
        else:
            return logging.error("未指定搜索内容")

    def get_custom_addresses(self):
        """
        获取深信服AD设备上配置的自定义地址组信息。

        通过调用AD设备API的自定义地址组接口，获取设备上已配置的地址组列表及成员信息。

        :return: API响应对象，包含自定义地址组数据；请求失败时返回None
        """
        return api_call(f"{self.ad_url}/api/ad/v3/rc/custom-address-group/", method="get", headers=self.headers)
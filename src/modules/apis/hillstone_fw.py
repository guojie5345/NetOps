# -*- coding: utf-8 -*-
class HillstoneApiClient:
    # VSYS映射关系 - 提取为类常量，避免重复定义

    """
    山石防火墙API客户端类，用于与山石防火墙设备交互，获取策略、地址簿等配置信息。
    """
    # 默认查询参数 - 提取为类常量，便于统一维护

    VSYS_MAPPING = {
        "ZCE-OA": "1",
        "ES-OA": "2",
        "ISP-zhuanxian-vFW": "6",
        "ZCEOA-vFW": "7",
        "ZLTest-vFW": "8"
    }

    DEFAULT_QUERY_PARAMS = {
        "fields": [],
        "conditions": [{"field": "enable", "value": 1}],
        "start": 0,
        "limit": 50,
        "page": 1
    }

    def __init__(self, url):
        self.url = url
        self.headers = {
            "Content-Type": "application/json",
        }
        self._login()

    def _login(self):
        """登录防火墙并获取认证Cookie"""
        login_url = f"{self.url}/rest/api/login"
        # 5.5R4和5.5R5版本密码需要BASE64编码,5.5R5_F及5.5R6以后版本用户名和密码都需要BASE64编码
        login_data = {
            "userName": "bmV0b3Bz",
            "password": "RGFpbHljaGVjazEyMyE=",
            "lang": "zh_CN"
        }

        try:
            response = api_call(login_url, method="post", json=login_data)
            if not response:
                raise Exception("登录请求失败，未获取到响应")

            result = response.json()['result'][0]
            # 请注意 cookie中 username为非加密形式
            self.headers["Cookie"] = (
                f"token={result['token']};username=netops;vsysId={result['vsysId']};"
                f"role={result['role']};fromrootvsys={result['fromrootvsys']}"
            )
            logging.debug("山石防火墙登录成功")
        except Exception as e:
            logging.error(f"山石防火墙登录失败: {str(e)}")
            raise  # 重新抛出异常，让调用方处理

    def get_policy(self):
        """获取策略配置"""
        return api_call(f"{self.url}/rest/api/policy", method="get", headers=self.headers)

    def set_policy(self, policy):
        """设置策略配置"""
        response = api_call(f"{self.url}/rest/api/policy/", method="post", json=policy, headers=self.headers)
        if response:
            print(response.json()['success'])
        else:
            logging.error("设置策略失败，未获取到响应")

    def get_addrbook(self):
        """获取地址簿配置"""
        return api_call(f"{self.url}/rest/api/addrbook", method="get", headers=self.headers)

    def get_servicebook(self):
        """获取服务簿配置"""
        return api_call(f"{self.url}/rest/api/servicebook", method="get", headers=self.headers)

    def get_servicegroup(self):
        """获取服务组配置"""
        return api_call(f"{self.url}/rest/api/servicegroup", method="get", headers=self.headers)

    def get_vsys(self):
        """获取虚拟系统配置"""
        return api_call(f"{self.url}/rest/api/vsys", method="get", headers=self.headers)

    def _get_vsys_resource(self, vsys_name, resource_type, params=None):
        """
        获取指定VSYS的资源

        :param vsys_name: VSYS名称
        :param resource_type: 资源类型，如"policy"、"addrbook"等
        :param params: 查询参数，默认为DEFAULT_QUERY_PARAMS
        :return: API响应对象
        """
        if vsys_name not in self.VSYS_MAPPING:
            logging.error(f"不支持的VSYS名称: {vsys_name}")
            return None

        vsys_id = self.VSYS_MAPPING[vsys_name]
        # 使用默认参数或传入的参数
        query_params = params or self.DEFAULT_QUERY_PARAMS

        try:
            # 修改Cookie中的vsysId
            original_cookie = self.headers['Cookie']
            self.headers['Cookie'] = original_cookie.replace(
                f"vsysId={self._get_current_vsys_id()}",
                f"vsysId={vsys_id}"
            )

            # 调用API获取资源
            response = api_call(
                f"{self.url}/rest/api/{resource_type}",
                method="get",
                headers=self.headers,
                params=query_params
            )

            # 恢复原始Cookie
            self.headers['Cookie'] = original_cookie
            return response
        except Exception as e:
            logging.error(f"获取VSYS资源失败: {str(e)}")
            # 确保异常情况下也恢复原始Cookie
            self.headers['Cookie'] = original_cookie
            return None

    def _get_current_vsys_id(self):
        """从Cookie中获取当前vsysId"""
        import re
        cookie = self.headers.get('Cookie', '')
        match = re.search(r'vsysId=(\d+)', cookie)
        return match.group(1) if match else '0'

    def get_vsys_policy(self, vsys):
        """获取指定VSYS的策略配置"""
        return self._get_vsys_resource(vsys, "policy")

    def get_vsys_addrbook(self, vsys):
        """获取指定VSYS的地址簿配置"""
        return self._get_vsys_resource(vsys, "addrbook")
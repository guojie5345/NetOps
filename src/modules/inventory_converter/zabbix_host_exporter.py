import requests
import pandas as pd
import argparse
import json
from typing import List, Dict, Optional


class ZabbixHostConfigExporter:
    def __init__(self, zabbix_url: str, username: str, password: str):
        """初始化Zabbix连接参数"""
        self.zabbix_url = f"{zabbix_url}/api_jsonrpc.php"
        self.username = username
        self.password = password
        self.auth_token = None
        self.headers = {"Content-Type": "application/json-rpc"}

    def _send_request(self, method: str, params: Dict) -> Optional[Dict]:
        """发送请求到Zabbix API"""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }

        if self.auth_token:
            payload["auth"] = self.auth_token

        try:
            response = requests.post(
                self.zabbix_url,
                headers=self.headers,
                data=json.dumps(payload),
                verify=False
            )
            response.raise_for_status()
            result = response.json()

            if "error" in result:
                print(f"API错误: {result['error']['message']}")
                print(f"错误详情: {result['error']['data']}")
                return None

            return result.get("result")

        except requests.exceptions.RequestException as e:
            print(f"请求错误: {str(e)}")
            return None

    def authenticate(self) -> bool:
        """进行Zabbix API认证"""
        print("正在进行Zabbix API认证...")
        params = {
            "username": self.username,
            "password": self.password
        }

        result = self._send_request("user.login", params)
        if result:
            self.auth_token = result
            print("认证成功")
            return True
        print("认证失败")
        return False

    def get_host_configurations(self, host_ids: Optional[List[str]] = None) -> List[Dict]:
        """
        获取主机配置信息，包括核心配置参数
        """
        print("正在获取主机配置信息...")

        # 配置查询参数，专注于主机的核心配置信息
        params = {
            "output": [
                "hostid", "host", "name", "status", "available",
                "description", "proxy_hostid", "auto_compress",
                "ipmi_authtype", "ipmi_privilege", "ipmi_username",
                "snmp_community", "snmp_version", "snmp_authpassphrase",
                "maintenance_status", "maintenance_type", "maintenance_from"
            ],
            # 网络接口配置
            "selectInterfaces": [
                "interfaceid", "ip", "dns", "port", "type",
                "main", "useip", "bulk"
            ],
            # 所属主机组
            "selectHostGroups": ["groupid", "name"],
            # 关联模板
            "selectParentTemplates": ["templateid", "name"],
            # 宏配置
            "selectMacros": ["macro", "value", "description"]
        }

        if host_ids:
            params["hostids"] = host_ids

        hosts = self._send_request("host.get", params)

        if hosts:
            print(f"成功获取 {len(hosts)} 台主机的配置信息")
            return hosts
        print("未获取到主机配置信息")
        return []

    def format_config_data(self, hosts: List[Dict]) -> List[Dict]:
        """格式化配置数据，使其更适合Excel展示"""
        formatted = []
        for host in hosts:
            # 基础信息
            base_info = {
                "主机ID": host.get("hostid"),
                "主机名": host.get("host"),
                "显示名称": host.get("name"),
                "状态": "启用" if host.get("status") == "0" else "禁用",
                "可用性": self._get_availability_text(host.get("available")),
                "描述": host.get("description", ""),
                "代理主机ID": host.get("proxy_hostid", ""),
                "自动压缩": "是" if host.get("auto_compress") == "1" else "否",
                "维护状态": "在维护中" if host.get("maintenance_status") == "1" else "正常"
            }

            # 网络接口信息
            interfaces = host.get("interfaces", [])
            for i, iface in enumerate(interfaces, 1):
                base_info.update({
                    f"接口{i}类型": self._get_interface_type(iface.get("type")),
                    f"接口{i}IP": iface.get("ip", ""),
                    f"接口{i}DNS": iface.get("dns", ""),
                    f"接口{i}端口": iface.get("port", ""),
                    f"接口{i}是否为主": "是" if iface.get("main") == "1" else "否",
                    f"接口{i}是否使用IP": "是" if iface.get("useip") == "1" else "否"
                })

            # 主机组信息
            groups = host.get("hostGroups", [])
            base_info["主机组"] = ", ".join([g.get("name", "") for g in groups])

            # 模板信息
            templates = host.get("parentTemplates", [])
            base_info["关联模板"] = ", ".join([t.get("name", "") for t in templates])

            # 宏配置
            macros = host.get("macros", [])
            for macro in macros:
                base_info[f"宏_{macro.get('macro')}"] = macro.get("value", "")

            formatted.append(base_info)

        return formatted

    def _get_availability_text(self, available: str) -> str:
        """转换可用性状态为文本"""
        status_map = {
            "0": "未知",
            "1": "可用",
            "2": "不可用"
        }
        return status_map.get(available, "未知")

    def _get_interface_type(self, type_id: str) -> str:
        """转换接口类型为文本"""
        type_map = {
            "1": "代理",
            "2": "SNMP",
            "3": "IPMI",
            "4": "JMX"
        }
        return type_map.get(type_id, f"未知({type_id})")

    def export_to_excel(self, config_data: List[Dict], filename: str) -> bool:
        """将配置信息导出到Excel"""
        if not config_data:
            print("没有主机配置信息可导出")
            return False

        try:
            df = pd.DataFrame(config_data)
            # 调整列顺序，将重要字段放在前面
            important_columns = ["主机ID", "主机名", "显示名称", "状态", "可用性", "主机组", "关联模板"]
            other_columns = [col for col in df.columns if col not in important_columns]
            df = df[important_columns + other_columns]

            df.to_excel(filename, index=False)
            print(f"成功导出 {len(config_data)} 台主机的配置信息到 {filename}")
            return True

        except Exception as e:
            print(f"导出Excel失败: {str(e)}")
            return False


def main():
    # 配置参数
    config = {
        'url': 'http://your-zabbix-server/zabbix',  # 替换为你的Zabbix地址
        'user': 'Admin',  # 替换为你的用户名
        'password': 'zabbix',  # 替换为你的密码
        'output': 'zabbix_host_configs.xlsx',  # 输出文件名
        'host_ids': None  # 可选：指定主机ID列表
    }

    # 命令行参数
    parser = argparse.ArgumentParser(description='Zabbix主机配置信息导出工具')
    parser.add_argument('--url', help='Zabbix服务器URL')
    parser.add_argument('--user', help='Zabbix登录用户名')
    parser.add_argument('--password', help='Zabbix登录密码')
    parser.add_argument('--output', help='导出的Excel文件名')
    parser.add_argument('--host-ids', nargs='*', help='指定主机ID列表，只导出这些主机的配置')

    args = parser.parse_args()

    # 合并参数：命令行参数优先
    for key in config:
        arg_key = key.replace('_', '-')
        if hasattr(args, arg_key) and getattr(args, arg_key) is not None:
            config[key] = getattr(args, arg_key)

    # 执行导出
    exporter = ZabbixHostConfigExporter(config['url'], config['user'], config['password'])
    if not exporter.authenticate():
        return

    # 获取主机配置信息
    host_configs = exporter.get_host_configurations(host_ids=config['host_ids'])
    if not host_configs:
        return

    # 格式化数据以便Excel展示
    formatted_data = exporter.format_config_data(host_configs)

    # 导出到Excel
    exporter.export_to_excel(formatted_data, config['output'])


if __name__ == "__main__":
    main()

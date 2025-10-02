#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import TimeoutException
import ddddocr  # 验证码识别库
from src.modules.processing.process_order import process_order

# 配置日志格式（全局生效）
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ITSMAutomation:
    """ITSM系统自动化操作核心类

    封装浏览器初始化、登录、变更请求创建等核心功能
    """

    def __init__(self, driver_path, base_url):
        """初始化方法

        Args:
            driver_path (str): Edge浏览器驱动路径（如E:\\Tools\\msedgedriver.exe）
            base_url (str): ITSM系统基础URL（如https://172.17.16.3:5199）
        """
        self.driver = None  # 浏览器驱动实例
        self.wait = None  # 显式等待实例（30秒超时）
        self.base_url = base_url  # ITSM系统基础URL

        # 初始化浏览器配置并启动驱动
        self._init_browser(driver_path)

    def _init_browser(self, driver_path):
        """私有方法：初始化浏览器驱动及配置"""
        # 配置Edge选项（忽略SSL错误、禁用日志）
        options = Options()
        options.add_argument("--ignore-certificate-errors")  # 忽略不受信任的SSL证书
        options.add_experimental_option('excludeSwitches', ['enable-logging'])  # 禁用浏览器日志

        # 初始化驱动服务并启动浏览器
        service = Service(driver_path)
        self.driver = webdriver.Edge(service=service, options=options)
        self.driver.maximize_window()  # 最大化窗口
        self.wait = WebDriverWait(self.driver, 30)  # 全局显式等待30秒
        logging.info("浏览器初始化完成")

    def login(self, username, password):
        """登录ITSM系统（带验证码重试机制）

        Args:
            username (str): 登录用户名
            password (str): 登录密码

        Returns:
            bool: 登录成功状态

        Raises:
            Exception: 登录失败时抛出异常
        """
        max_retries = 3  # 验证码最大重试次数
        retry_count = 0  # 当前重试次数
        login_url = f"{self.base_url}/itil/login.do"

        for retry in range(max_retries):
            try:
                self.driver.get(login_url)  # 访问登录页面

                # 输入用户名密码
                user_ele = self.wait.until(EC.presence_of_element_located((By.ID, "AS_usr")))
                user_ele.clear()
                user_ele.send_keys(username)
                passwd_ele = self.wait.until(EC.presence_of_element_located((By.ID, "AS_psw")))
                passwd_ele.clear()
                passwd_ele.send_keys(password)

                # 验证码识别与输入
                captcha_img = self.wait.until(EC.presence_of_element_located((By.ID, "codeimg")))
                captcha_img.screenshot("temp_captcha.png")  # 临时保存验证码截图

                # 使用OCR识别验证码
                ocr = ddddocr.DdddOcr(show_ad=False)
                with open("temp_captcha.png", "rb") as f:
                    captcha_code = ocr.classification(f.read())

                # 输入验证码并提交
                as_code = self.wait.until(EC.presence_of_element_located(('id', 'AS_code')))
                as_code.clear()
                as_code.send_keys(captcha_code)
                self.wait.until(EC.element_to_be_clickable((By.ID, "loginSubmit"))).click()

                # 处理登录结果（弹窗或直接成功）
                try:
                    # 等待5秒检测是否有弹窗（可能是验证码错误提示）
                    alert = WebDriverWait(self.driver, 3).until(EC.alert_is_present())
                    alert.accept()  # 关闭弹窗
                    break
                except TimeoutException:
                    # 无弹窗可能是登录成功，直接检查用户信息
                    break
            except Exception as e:
                raise Exception(f"超过最大重试次数（{max_retries}次）")

        # 验证是否登录成功
        user_ele = self.wait.until(EC.presence_of_element_located((By.XPATH, '//cite')))
        if user_ele.text == "郭杰":
            return self.driver
        else:
            raise Exception("登录后检测到非目标用户")

    def create_change_request(self, start_time, end_time, change_file):
        """创建网络运行情况周报变更请求

        Args:
            start_time (datetime): 计划开始时间（datetime对象）
            end_time (datetime): 计划结束时间（datetime对象）
        """
        with open(change_file, "r", encoding="utf-8") as f:
            change_content = json.load(f)
        change_type = change_content["变更类型"]
        title = change_content["变更标题"]
        reason = change_content["变更原因"]
        scheme = change_content["变更方案"]

        # 导航到工作台并进入综合变更页面
        self._navigate_to_change_page()
        logging.info("导航到综合变更页面")

        # 填写变更基本信息（标题、影响服务等）
        self._fill_basic_info(change_type)
        logging.info("填写变更基本信息")

        # 填写时间信息（开始/结束时间）
        self._fill_time_info(start_time, end_time)
        logging.info("填写变更时间信息")

        # 填写变更详情（内容、原因、方案）
        # title, reason, scheme = process_order.main()
        logging.info(f"获取变更详情（内容、原因、方案）")
        self._fill_change_details(title, reason, scheme)
        logging.info("填写变更详情")

        # 提交变更请求
        self._submit_request()
        logging.info("提交变更请求")
        logging.info("变更请求创建完成")

    def _navigate_to_change_page(self):
        """私有方法：导航到综合变更页面"""
        # 点击"我的工作台"
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//li[@lay-id="-1"]'))).click()

        # 切换到主iframe
        main_iframe = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//iframe[@id="ifr-1"]')))
        self.driver.switch_to.frame(main_iframe)

        # 切换到快捷方式iframe
        shortcut_iframe = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//iframe[@cardid="fed12e0744da4a148af0fad07496906a"]')))
        self.driver.switch_to.frame(shortcut_iframe)

        # 点击"综合变更"入口
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="container"]/ul/li[4]'))).click()

        # 切换回当前活动iframe
        self.driver.switch_to.default_content()
        current_iframe = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//div[@class="layui-tab-item layui-show"]/iframe')))
        self.driver.switch_to.frame(current_iframe)
        time.sleep(1)  # 等待页面加载完成

    def _fill_basic_info(self, change_type):
        """私有方法：填写变更基本信息"""
        service = {
            "NAT网关": "期货行业云服务-网络服务-NAT网关(网络工程中心)",
            "弹性IP": "期货行业云服务-网络服务-弹性IP(网络工程中心)",
            "负载均衡": "期货行业云服务-网络服务-负载均衡(网络工程中心)",
            "高速通道": "期货行业云服务-网络服务-高速通道(网络工程中心)",
            "互联网接入": "期货行业云服务-网络服务-互联网接入服务（网络工程中心）",
            "交易网络接入": "期货行业云服务-网络服务-交易网络接入服务（网络工程中心）",
            "虚拟专有网络": "期货行业云服务-网络服务-虚拟专有网络(网络工程中心)",
            "易盛办公网接入": "期货行业云服务-网络服务-易盛办公网接入服务(网络工程中心)",
            "证联网测试网接入": "期货行业云服务-网络服务-证联网测试网接入服务（网络工程中心）",
            "证联网生产网接入": "期货行业云服务-网络服务-证联网生产网接入服务（网络工程中心）",
            "郑商所办公网接入": "期货行业云服务-网络服务-郑商所办公网接入服务(网络工程中心)",
            "郑商所业务网接入": "期货行业云服务-网络服务-郑商所业务网接入服务(网络工程中心)",
            "专线接入": "期货行业云服务-网络服务-专线接入服务(网络工程中心)"
        }

        # 选择影响服务（期货行业云服务）
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//div[@id="ownedserviceSelectTreeDiv"]'))).click()
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@title="期货行业云服务"]'))).click()
        time.sleep(1)
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, f'//a[@title="{service[change_type]}"]'))).click()
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//i[@id="ownedserviceConfirmIcon"]'))).click()

        # 选择变更来源（用户）
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//div[@id="changesourceForm"]'))).click()
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//div[@id="changesourceForm"]/div/div/dl/dd[@lay-value="用户"]'))).click()

        # 选择变更分类（行业云-云网络-策略调整）
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//div[@id="changetypeSelectTreeDiv"]'))).click()
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@title="行业云-云网络"]'))).click()
        time.sleep(1)
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@title="网络策略调整（开通、停用、删除）"]'))).click()

        # 选择布尔选项（变更前测试/是否中断业务等）
        self._select_boolean_option('ischangetestForm')  # 变更前测试-否
        self._select_boolean_option('isbreakForm')  # 是否中断业务-否
        self._select_boolean_option('urgencychangeForm')  # 紧急变更-否

    def _select_boolean_option(self, filter_name):
        """私有方法：通用布尔选项选择（通过lay-filter定位）

        Args:
            filter_name (str): lay-filter属性值（如"ischangetestForm"）
        """
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, f'//div[@lay-filter="{filter_name}"]/div/table/tbody/tr/td[2]/div/i'))).click()

    def _fill_time_info(self, start_time, end_time):
        """私有方法：填写计划开始/结束时间

        Args:
            start_time (datetime): 开始时间
            end_time (datetime): 结束时间
        """
        # 处理开始时间
        self._handle_time_input('计划开始时间', start_time)
        # 处理结束时间
        self._handle_time_input('计划结束时间', end_time)

    def _handle_time_input(self, field_name, target_time):
        """私有方法：通用时间输入处理

        Args:
            field_name (str): 时间字段名称（如"计划开始时间"）
            target_time (datetime): 目标时间
        """
        # 触发时间选择器
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, f'//input[@ext_name="{field_name}"]'))).click()

        # 获取日历面板并选择时间
        calendar_panel = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//div[@id="ui-datepicker-div"]')))
        self._select_calendar_time(calendar_panel, target_time)

    def _select_calendar_time(self, calendar_panel, target_time):
        """私有方法：在日历面板中选择具体时间

        Args:
            calendar_panel (WebElement): 日历面板元素
            target_time (datetime): 目标时间
        """
        # 选择年份
        year_select = calendar_panel.find_element(By.XPATH, '//select[@data-handler="selectYear"]')
        Select(year_select).select_by_value(str(target_time.year))

        # 选择月份（索引从0开始）
        month_select = calendar_panel.find_element(By.XPATH, '//select[@data-handler="selectMonth"]')
        Select(month_select).select_by_index(target_time.month - 1)

        # 选择日期
        calendar_panel.find_element(By.XPATH, f'//a[text()="{target_time.day}"]').click()

        # 选择时间（时/分/秒）
        Select(calendar_panel.find_element(
            By.XPATH, '//dd[@class="ui_tpicker_hour"]/div/select')).select_by_value(str(target_time.hour))
        Select(calendar_panel.find_element(
            By.XPATH, '//dd[@class="ui_tpicker_minute"]/div/select')).select_by_value(str(target_time.minute))
        Select(calendar_panel.find_element(
            By.XPATH, '//dd[@class="ui_tpicker_second"]/div/select')).select_by_value(str(target_time.second))

        # 确认时间选择
        calendar_panel.find_element(By.XPATH, '//button[text()="确定"]').click()

    def _fill_change_details(self, title, reason, scheme):
        """填写变更内容详情（原因、方案等富文本内容）"""
        # 变更标题
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//input[@id="title"]'))).send_keys(title)
        time.sleep(1)
        # 评审纪要
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//input[@id="changejy"]'))).send_keys("组内通过评审。")
        time.sleep(1)

        # 变更内容（普通文本框）
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//textarea[@id="bd7644c3cba74f50bd1687be612bb59b_变更内容_1000"]'))).send_keys(scheme)
        time.sleep(1)

        # 替换原因中的 \n 为 <br>
        reason_with_br = reason.replace('\n', '<br>')
        # 变更原因（富文本框）
        self._fill_richtext_field(
            '//tr[@class="changereasonhandle"]/td[2]//iframe',
            reason_with_br
        )
        time.sleep(1)

        # 执行完成后，切换回"综合变更"iframe
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame(
            self.driver.find_element(By.XPATH, '//div[@class="layui-tab-item layui-show"]/iframe'))
        time.sleep(1)

        # 替换方案中的 \n 为 <br>
        scheme_with_br = scheme.replace('\n', '<br>')
        # 变更方案（富文本框）
        self._fill_richtext_field(
            '//div[@id="cke_2_contents"]/iframe',
            scheme_with_br
        )
        time.sleep(1)

        # 执行完成后，切换回"综合变更"iframe
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame(
            self.driver.find_element(By.XPATH, '//div[@class="layui-tab-item layui-show"]/iframe'))
        time.sleep(1)

    def _fill_richtext_field(self, iframe_xpath, content):
        """通用富文本框内容填充方法

        Args:
            iframe_xpath (str): 富文本框所在iframe的XPath
            content (str): 需要填充的HTML内容
        """
        iframe = self.wait.until(EC.presence_of_element_located((By.XPATH, iframe_xpath)))
        self.driver.switch_to.frame(iframe)
        editable_body = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print(f"content: {content}")
        self.driver.execute_script("arguments[0].innerHTML = arguments[1];", editable_body, content)
        self.driver.switch_to.default_content()  # 切回主文档
        time.sleep(1)  # 等待内容渲染

    def _submit_request(self):
        """提交变更请求"""
        # 选择提交人
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@id="dealuserid3"]'))).click()
        # 切换到选择提交人iframe
        submit_iframe = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//iframe[@id="layui-layer-iframe1"]')))
        self.driver.switch_to.frame(submit_iframe)
        time.sleep(1)
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@id="userid3663698"]'))).click()
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@value="　确定　"]'))).click()
        self.driver.switch_to.default_content()  # 切回主文档
        time.sleep(1)
        self.driver.switch_to.frame(
            self.driver.find_element(By.XPATH, '//div[@class="layui-tab-item layui-show"]/iframe'))
        time.sleep(1)
        # 最终提交
        # self.wait.until(EC.element_to_be_clickable(
        #     (By.XPATH, '//input[@id="_set_submit"]'))).click()
        # logging.info("变更请求已提交")

    def close(self):
        """关闭浏览器驱动"""
        if self.driver:
            self.driver.quit()
            logging.info("浏览器已关闭")


def main():
    # 配置参数
    EDGE_DRIVER_PATH = r"E:\Tools\msedgedriver.exe"
    ITSM_BASE_URL = "https://172.17.16.3:5199"
    LOGIN_USER = "guo_jie"
    LOGIN_PWD = "1qazXSW@#EDC"

    # 计算时间参数（当天17:00或次日17:00）
    current_time = datetime.datetime.now()
    target_time = current_time.replace(hour=17, minute=0, second=0, microsecond=0)
    if current_time > target_time:
        target_time += datetime.timedelta(days=1)

    # 执行自动化流程
    for root, dirs, files in os.walk("change_scripts/20250808"):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                try:
                    itsm = ITSMAutomation(EDGE_DRIVER_PATH, ITSM_BASE_URL)
                    if itsm.login(LOGIN_USER, LOGIN_PWD):
                        itsm.create_change_request(current_time, target_time, file_path)
                        time.sleep(100)
                except Exception as e:
                    logging.error(f"自动化流程失败：{str(e)}")
                finally:
                    itsm.close()  # 确保关闭浏览器


if __name__ == '__main__':
    main()

import requests  # 导入requests库，用于发送HTTP请求
import json  # 导入json库，用于处理JSON数据
from opencc import OpenCC  # 导入OpenCC库，用于繁体中文到简体中文的转换
from datetime import datetime  # 导入datetime模块，用于获取当前日期和时间
import pytz  # 导入pytz库，用于处理时区
import os  # 导入os模块，用于操作文件系统


class LotteryDataFetcher:
    """
    彩票数据获取器类，负责获取和处理香港和澳门的彩票数据，并管理数据的比较和更新
    """
    # 类变量：存储常量和配置
    HONG_KONG_URL = "https://www.cpzhan.com/api/new-scores.js"  # 香港数据的API URL
    MACAU_URL = "https://api.macaumarksix.com/api/live"  # 澳门数据的API URL
    PUSH_TOKEN = os.environ.get("PUSH_TOKEN")  # Push服务的API令牌
    DATA_FILE_NAME = "data.txt"  # 保存数据的文件名
    PUSH_URL = f"https://push.showdoc.com.cn/server/api/push/{PUSH_TOKEN}"  # Push通知服务的URL
    BEIJING_TZ = pytz.timezone("Asia/Shanghai")  # 北京时区，用于获取北京时间

    def __init__(self):
        """
        初始化LotteryDataFetcher类
        """
        self.converter = OpenCC("t2s")  # 创建一个OpenCC对象，用于繁体中文到简体中文的转换

    def trad_to_simp(self, text: str) -> str:
        """
        将繁体中文转换为简体中文
        :param text: 繁体中文字符串
        :return: 简体中文字符串
        """
        return self.converter.convert(text)  # 使用OpenCC对象进行转换，并返回转换后的简体中文字符串

    def fetch_data(self, url: str, headers: dict) -> requests.Response:
        """
        从指定的URL获取数据
        :param url: 请求的URL
        :param headers: 请求头
        :return: HTTP响应对象或None
        """
        try:
            response = requests.get(url, headers=headers)  # 发送GET请求到指定的URL，使用提供的请求头
            response.raise_for_status()  # 检查请求是否成功，如果不成功则抛出HTTP错误异常
            return response  # 返回HTTP响应对象
        except requests.RequestException as e:  # 捕获所有的HTTP请求异常
            print(f"Error fetching data from {url}: {e}")  # 打印错误信息
            return None  # 返回None表示获取数据失败

    def parse_hong_kong_data(self, response_text: str) -> str:
        """
        解析香港数据并返回格式化的字符串
        :param response_text: 原始响应文本
        :return: 格式化后的字符串
        """
        try:
            data = response_text.split("'")[1]  # 解析响应文本，提取包含实际数据的部分（去掉前后的单引号）
            segments = data.split("|")  # 使用竖线“|”分割数据，获取不同部分

            period = segments[0].split(",")[0]  # 从分段的第一段中提取期数
            number = segments[0].split(",")[-1]  # 从分段的第一段中提取最后一个号码
            zodiac = self.trad_to_simp(segments[2].split(",")[-1])  # 从分段的第三段中提取最后一个生肖并转换为简体中文

            return f"期数：{period}\n号码：{number}\n生肖：{zodiac}"  # 返回格式化后的字符串
        except IndexError as e:  # 捕获索引错误异常
            print(f"Error parsing Hong Kong data: {e}")  # 打印错误信息
            return "解析失败"  # 返回解析失败的字符串

    def parse_macau_data(self, response_json: dict) -> str:
        """
        解析澳门数据并返回格式化的字符串
        :param response_json: JSON格式的响应数据
        :return: 格式化后的字符串
        """
        try:
            entry = response_json[0]  # 获取JSON响应的第一个元素

            period = entry["expect"][4:]  # 提取“expect”字段的值，并从第五个字符开始截取以获取期数
            number = entry["openCode"].split(",")[-1]  # 从“openCode”字段中提取最后一个号码
            zodiac = self.trad_to_simp(
                entry["zodiac"].split(",")[-1]
            )  # 从“zodiac”字段中提取最后一个生肖并转换为简体中文

            return f"期数：{period}\n号码：{number}\n生肖：{zodiac}"  # 返回格式化后的字符串
        except (IndexError, KeyError) as e:  # 捕获索引错误或键错误异常
            print(f"Error parsing Macau data: {e}")  # 打印错误信息
            return "解析失败"  # 返回解析失败的字符串

    def fetch_hong_kong_data(self) -> str:
        """
        获取并解析香港数据
        :return: 格式化后的香港数据字符串
        """
        headers = {"Host": "www.cpzhan.com"}  # 定义请求头，指定Host字段
        response = self.fetch_data(self.HONG_KONG_URL, headers)  # 调用fetch_data函数获取香港数据
        if response:  # 检查响应是否成功
            return self.parse_hong_kong_data(response.text)  # 解析响应文本并返回格式化的数据
        return "获取失败"  # 如果响应失败，返回获取失败的字符串

    def fetch_macau_data(self) -> str:
        """
        获取并解析澳门数据
        :return: 格式化后的澳门数据字符串
        """
        headers = {"Host": "api.macaumarksix.com"}  # 定义请求头，指定Host字段
        response = self.fetch_data(self.MACAU_URL, headers)  # 调用fetch_data函数获取澳门数据
        if response:  # 检查响应是否成功
            try:
                response_json = response.json()  # 解析响应文本为JSON对象
                return self.parse_macau_data(response_json)  # 解析JSON数据并返回格式化的数据
            except json.JSONDecodeError as e:  # 捕获JSON解码错误异常
                print(f"Error decoding Macau data: {e}")  # 打印错误信息
        return "获取失败"  # 如果响应失败，返回获取失败的字符串

    def send_push_notification(self, title: str, content: str) -> str:
        """
        发送 Push 通知
        :param title: 通知标题
        :param content: 通知内容
        :return: Push响应文本
        """
        # 定义一个字典，用于存储需要替换的字符串及其对应的替换值
        replacements = {
            "------": "\n------\n",  # 替换多连字符为换行后的连字符
            "香港：": "<h1>香港</h1>\n",  # 替换“香港：”为HTML标题标签
            "澳门：": "<h1>澳门</h1>\n",  # 替换“澳门：”为HTML标题标签
        }
        # 遍历字典中的所有键值对，进行替换操作
        for old, new in replacements.items():
            content = content.replace(old, new)
        data = {
            "title": title,
            "content": content,
        }  # 创建数据字典，包含API令牌、标题和内容
        body = json.dumps(data).encode("utf-8")  # 将数据字典转换为JSON字符串并编码为UTF-8格式的字节流
        headers = {"Content-Type": "application/json"}  # 定义请求头，指定内容类型为JSON
        try:
            response = requests.post(self.PUSH_URL, data=body, headers=headers)  # 发送POST请求到Push API
            response.raise_for_status()  # 检查请求是否成功，如果不成功则抛出HTTP错误异常
            # 解析响应的JSON数据，转换为字典
            response_dict = json.loads(response.text)
            return response_dict  # 返回API响应的文本内容
        except requests.RequestException as e:  # 捕获所有的HTTP请求异常
            print(f"Error sending Push notification: {e}")  # 打印错误信息
            return "通知发送失败"  # 返回通知发送失败的字符串

    def get_current_beijing_time(self) -> str:
        """
        获取当前北京时间并格式化
        :return: 格式化的北京时间字符串
        """
        current_time = datetime.now(self.BEIJING_TZ)  # 获取当前时间，并转换为北京时间
        return current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # 格式化时间字符串，精确到毫秒，并去掉最后三位

    def compare_and_update_data(self) -> str:
        """
        比较现有数据和新获取的数据，如果不一致则更新文件并发送通知
        :return: 比较和更新结果信息
        """
        current_data = f"香港：\n{self.fetch_hong_kong_data()}\n------\n澳门：\n{self.fetch_macau_data()}"  # 获取当前的香港和澳门数据，并合并为一个字符串

        if not os.path.exists(self.DATA_FILE_NAME):  # 检查数据文件是否存在
            with open(self.DATA_FILE_NAME, "w", encoding="utf-8") as file:  # 如果文件不存在，创建文件并写入当前数据
                file.write(current_data)
            return f"{self.DATA_FILE_NAME} 文件不存在，已创建并写入数据。"  # 返回文件创建和写入的消息

        with open(self.DATA_FILE_NAME, "r", encoding="utf-8") as file:  # 如果文件存在，打开文件并读取内容
            previous_data = file.read()  # 读取文件内容

        if previous_data != current_data:  # 比较文件内容与当前数据
            with open(self.DATA_FILE_NAME, "w", encoding="utf-8") as file:  # 如果不一致，覆盖写入新的数据
                file.write(current_data)
            update_time = self.get_current_beijing_time()  # 获取当前北京时间
            return self.send_push_notification(
                "数据已更新", f"更新时间：{update_time}\n------\n{current_data}"
            )  # 发送通知并返回API响应
        return "数据未更新"  # 如果数据一致，返回数据未更新的消息


# 创建LotteryDataFetcher类的实例
fetcher = LotteryDataFetcher()

# 调用compare_and_update_data方法，获取比较和更新结果
result = fetcher.compare_and_update_data()

# 打印结果到控制台
print(result)

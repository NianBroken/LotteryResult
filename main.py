import hashlib
import json
import os
import shutil
import requests
from pushplus import send_message

aomen_url = os.environ.get("AOMENURL")


# MD5加密
def md5_encrypt(string):
    return hashlib.md5(string.encode()).hexdigest()


aomen_file_path = "aomen.txt"
old_aomen_file_path = "old_aomen.txt"
aomen_output = ""
run_log = ""
token = "123456"

aomen_response = requests.get(aomen_url)

# 读取颜色映射文件
with open("color_mapping.json", "r", encoding="utf-8") as aomen_file:
    aomen_color_mapping = json.load(aomen_file)


if aomen_response.status_code == 200:
    aomen_macaujc = aomen_response.json()
    for aomen_data in aomen_macaujc:
        aomen_data["期号"] = aomen_data.pop("expect")
        aomen_data["号码"] = aomen_data.pop("openCode").split(",")[-1]
        aomen_data["生肖"] = aomen_data.pop("zodiac").split(",")[-1]
        # 将 wave 的值转为简体中文
        wave_value = aomen_data.pop("wave").split(",")[-1]
        aomen_data["颜色"] = aomen_color_mapping.get(wave_value, wave_value)
        aomen_data["公布时间"] = aomen_data.pop("openTime")
        # 删除 info 字段
        aomen_data.pop("info", None)
        for aomen_key, aomen_value in aomen_data.items():
            aomen_output += f"{aomen_key}: {aomen_value}\n"

    # 移除末尾额外的空行
    aomen_output = aomen_output.rstrip()

    # 加密
    encrypted_aomen = md5_encrypt(aomen_output)

    # 如果aomen.txt文件不存在,则创建文件
    if not os.path.exists(aomen_file_path):
        open(aomen_file_path, "w").close()

    # 清空old_aomen.txt文件内容
    with open(old_aomen_file_path, "w") as old_aomen_file:
        old_aomen_file.truncate()

    # 将aomen.txt文件中的内容写入old_aomen.txt文件内
    with open(aomen_file_path, "r") as aomen_file, open(
        old_aomen_file_path, "w"
    ) as old_aomen_file:
        old_aomen_file.write(aomen_file.read())

    # 清空aomen.txt文件内容
    with open(aomen_file_path, "w") as aomen_file:
        aomen_file.truncate()

    # 将信息写入到aomen.txt
    with open(aomen_file_path, "w") as aomen_file:
        aomen_file.write(encrypted_aomen)
else:
    aomen_output = "获取数据失败"

# 读取aomen.txt和old_aomen.txt文件的内容
with open(aomen_file_path, "r") as aomen_file, open(
    old_aomen_file_path, "r"
) as old_aomen_file:
    aomen_content = aomen_file.read()
    old_aomen_content = old_aomen_file.read()

if aomen_content != old_aomen_content:
    run_log += "号码已更新\n"
    # 推送信息
    response_text = send_message(
        token,
        "号码已更新",
        aomen_output,
    )

    # 解析 JSON 数据
    response_dict = json.loads(response_text)

    # 删除 "data" 字段
    if "data" in response_dict:
        response_dict.pop("data")

    # 输出响应内容
    run_log += f"{response_dict}\n"

else:
    run_log += "号码未更新"
print(run_log)

# 删除 __pycache__ 缓存目录及其内容
current_directory = os.getcwd()
cache_folder = os.path.join(current_directory, "__pycache__")
# 检查目录是否存在
if os.path.exists(cache_folder):
    # 删除目录及其内容
    shutil.rmtree(cache_folder)

import xianggang
import aomen
import hashlib
import os
import shutil
from pushplus import send_message
import json

xianggang_url = os.environ.get("XIANGGANG_URL")
aomen_url = os.environ.get("AOMEN_URL")
token = os.environ.get("TOKEN")
beijing_time = os.environ.get("BEIJING_TIME")
result_file_path = "result.txt"
old_result_file_path = "old_result.txt"


def md5_encrypt(string):
    return hashlib.md5(string.encode()).hexdigest()


def file_operation():
    if not os.path.exists(result_file_path):
        open(result_file_path, "w").close()
    with open(old_result_file_path, "w") as old_result_file:
        old_result_file.truncate()
    with open(result_file_path, "r") as result_file, open(
        old_result_file_path, "w"
    ) as old_result_file:
        old_result_file.write(result_file.read())
    with open(result_file_path, "w") as result_file:
        result_file.truncate()
    with open(result_file_path, "w") as result_file:
        result_file.write(output_encrypted)


def file_comparison():
    with open(result_file_path, "r") as result_file, open(
        old_result_file_path, "r"
    ) as old_result_file:
        result_content = result_file.read()
        old_result_content = old_result_file.read()
    return result_content == old_result_content


def delete_the_data_field(response_text):
    response_dict = json.loads(response_text)
    if "data" in response_dict:
        response_dict.pop("data")
    return response_dict


try:
    xianggang_output = xianggang.get_xianggang_lottery_output(xianggang_url)
    aomen_output = aomen.get_aomen_lottery_output(aomen_url)

except Exception as e:
    print(f"M_Error: {e}")

else:
    xianggang_output = f"香港：\n" f"{xianggang_output}"
    aomen_output = f"澳门：\n" f"{aomen_output}"
    output = f"{xianggang_output}\n------\n{aomen_output}"

    output_encrypted = md5_encrypt(output)

    file_operation()
    file_comparison()

    push_text = (
        f"新号码已更新\n"
        f"------\n"
        f"{output}\n"
        f"------\n"
        f"本次服务器时间：{beijing_time}"
    )

    if not file_comparison():
        response_text = send_message(
            token,
            "号码已更新",
            push_text,
        )
        print("号码已更新")
        print(delete_the_data_field(response_text))

    else:
        print("号码未更新")

current_directory = os.getcwd()
cache_folder = os.path.join(current_directory, "__pycache__")
if os.path.exists(cache_folder):
    shutil.rmtree(cache_folder)

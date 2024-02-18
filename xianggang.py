import requests


def get_xianggang_lottery_output(xianggang_url):
    try:
        xianggang_response = requests.get(xianggang_url)
        xianggang_output = ""
        if xianggang_response.status_code == 200:
            xianggang_data = xianggang_response.json()
            xianggang_record_list = xianggang_data.get("data", {}).get("recordList", [])
            xianggang_first_record = xianggang_record_list[0]
            xianggang_lottery_time = xianggang_first_record.get("lotteryTime")
            xianggang_year = xianggang_lottery_time[:4]
            xianggang_period = xianggang_first_record.get("period")
            xianggang_number_dict = xianggang_first_record.get("numberList", [])
            xianggang_number = xianggang_number_dict[-1].get("number")
            xianggang_sheng_xiao = xianggang_number_dict[-1].get("shengXiao")
            xianggang_new_period = f"{xianggang_year}0{xianggang_period}"
            xianggang_output += f"期数: {xianggang_new_period}\n"
            xianggang_output += f"号码: {xianggang_number}\n"
            xianggang_output += f"生肖: {xianggang_sheng_xiao}\n"
            xianggang_output += f"公布时间: {xianggang_lottery_time}\n"
    except Exception as e:
        return f"XG_Error: {e}"
    else:
        xianggang_output = xianggang_output.rstrip()
        if not xianggang_output:
            return "获取失败"
        else:
            return xianggang_output

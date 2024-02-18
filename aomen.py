import json
import requests


def get_aomen_lottery_output(aomen_url):
    try:
        aomen_output = ""
        aomen_response = requests.get(aomen_url)
        with open("color_mapping.json", "r", encoding="utf-8") as aomen_file:
            aomen_color_mapping = json.load(aomen_file)
        if aomen_response.status_code == 200:
            aomen_macaujc = aomen_response.json()
            for aomen_data in aomen_macaujc:
                aomen_data["期号"] = aomen_data.pop("expect")
                aomen_data["号码"] = aomen_data.pop("openCode").split(",")[-1]
                aomen_data["生肖"] = aomen_data.pop("zodiac").split(",")[-1]
                wave_value = aomen_data.pop("wave").split(",")[-1]
                aomen_data["颜色"] = aomen_color_mapping.get(wave_value, wave_value)
                aomen_data["公布时间"] = aomen_data.pop("openTime")
                aomen_data.pop("info", None)
                for aomen_key, aomen_value in aomen_data.items():
                    aomen_output += f"{aomen_key}: {aomen_value}\n"
    except Exception as e:
        return f"AM_Error: {e}"
    else:
        aomen_output = aomen_output.rstrip()
        if not aomen_output:
            return "获取失败"
        else:
            return aomen_output

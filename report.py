from config import config

class Report:
    SERVICE_NAME = "daily-report"
    service = config["service"][SERVICE_NAME]
    def __init__(self, session):
        self.session = session
        if "jinji_lxr" not in self.service["user-params"] or self.service["user-params"]["jinji_lxr"] == "":
            print("紧急联系人为空！")
            return
        if "jinji_guanxi" not in self.service["user-params"] or self.service["user-params"]["jinji_guanxi"] == "":
            print("与本人关系为空！")
            return
        if "jiji_mobile" not in self.service["user-params"] or self.service["user-params"]["jiji_mobile"] == "":
            print("联系人电话为空！")
            return
        self.params = {
            "_token": "",
            "now_address": "1",
            "gps_now_address": "",
            "now_province": "340000",
            "gps_province": "",
            "now_city": "340100",
            "gps_city": "",
            "now_country": "340104",
            "gps_country": "",
            "now_detail": "",
            "is_inschool": "4",
            "body_condition": "1",
            "body_condition_detail": "",
            "now_status": "1",
            "now_status_detail": "",
            "has_fever": "0",
            "last_touch_sars": "0",
            "last_touch_sars_date": "",
            "last_touch_sars_detail": "",
            "is_danger": "0",
            "is_goto_danger": "0",
            "jinji_lxr": self.service["user-params"]["jinji_lxr"],
            "jinji_guanxi": self.service["user-params"]["jinji_guanxi"],
            "jiji_mobile": self.service["user-params"]["jiji_mobile"],
            "other_detail": ""
        }
        self.report()

    def report(self):
        res = self.session.get(url=self.service["url"])
        try:
            _token = res.text[res.text.find("_token"):].split("\"")[2]
            self.params["_token"] = _token
        except:
            print("Token not found!")
            return

        res = self.session.post("https://weixine.ustc.edu.cn/2020/daliy_report", params=self.params, allow_redirects=False)
        res = self.session.get(res.headers["location"])
        if res.text.find("上报成功"):
            print("上报成功.", res.text[res.text.find("上报时间"):].split("<")[0])
        else:
            print("上报失败")

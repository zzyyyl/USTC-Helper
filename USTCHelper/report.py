from .config import config
from .config import LoadConfig, DumpConfig

class ReportError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return f"ReportError: {self.text}"

REPORT_SERVICE_NAME = "daily-report"
config["service"][REPORT_SERVICE_NAME] = {
    "doc": "每日健康上报",
    "login": "https://weixine.ustc.edu.cn/2020/caslogin",
    "url": "https://weixine.ustc.edu.cn/2020/home",
    "exec": "https://weixine.ustc.edu.cn/2020/daliy_report",
}

class Report:
    SERVICE_NAME = REPORT_SERVICE_NAME
    service = config["service"][SERVICE_NAME]
    def __init__(self, session, stuid, silence=None):
        self.session = session
        self.stuid = stuid
        self.user_config = LoadConfig(self.stuid)
        if "user_params" not in self.user_config or not self.user_config["user_params"]:
            self.user_config["user_params"] = {}
        if self.SERVICE_NAME not in self.user_config["user_params"]:
            self.user_config["user_params"][self.SERVICE_NAME] = {}
        self.user_params = self.user_config["user_params"][self.SERVICE_NAME]
        if "dorm_building" not in self.user_params or not self.user_params["dorm_building"]:
            self.user_params["dorm_building"] = input("宿舍楼号：")
        if "dorm" not in self.user_params or not self.user_params["dorm"]:
            self.user_params["dorm"] = input("宿舍房号：")
        if "jinji_lxr" not in self.user_params or not self.user_params["jinji_lxr"]:
            self.user_params["jinji_lxr"] = input("紧急联系人：")
        if "jinji_guanxi" not in self.user_params or not self.user_params["jinji_guanxi"]:
            self.user_params["jinji_guanxi"] = input("与本人关系：")
        if "jiji_mobile" not in self.user_params or not self.user_params["jiji_mobile"]:
            self.user_params["jiji_mobile"] = input("联系人电话：")

        self.params = {
            "_token": "",
            "juzhudi": "中校区",
            "dorm_building": self.user_params["dorm_building"],
            "dorm": self.user_params["dorm"],
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
            "jinji_lxr": self.user_params["jinji_lxr"],
            "jinji_guanxi": self.user_params["jinji_guanxi"],
            "jiji_mobile": self.user_params["jiji_mobile"],
            "other_detail": ""
        }
        self.report(silence=silence)
        DumpConfig(self.stuid, self.user_config)

    def report(self, silence=None):
        res = self.session.get(url=self.service["url"])
        try:
            _token = res.text[res.text.find("_token"):].split("\"")[2]
            self.params["_token"] = _token
        except:
            if not silence:
                print("Token not found!")
            return

        res = self.session.post(url=self.service["exec"], params=self.params, allow_redirects=False)
        res = self.session.get(res.headers["location"])
        if res.text.find("上报成功") != -1:
            if not silence:
                print(res.text[res.text.find("上报成功"):].split("<")[0])
        else:
            if not silence:
                print("上报失败")
            raise ReportError("上报失败")

config["service"][REPORT_SERVICE_NAME]["entry"] = Report

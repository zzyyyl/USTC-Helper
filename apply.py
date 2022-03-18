from config import config, LoadConfig, DumpConfig
from datetime import datetime, timedelta

class ApplyError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return f"ApplyError: {self.text}"

class Apply:
    SERVICE_NAME = "daily-apply"
    service = config["service"][SERVICE_NAME]
    def __init__(self, session, stuid, silence=None):
        self.session = session
        self.stuid = stuid
        self.user_config = LoadConfig(self.stuid)
        if "user_params" not in self.user_config:
            self.user_config["user_params"] = {}
        if self.SERVICE_NAME not in self.user_config["user_params"]:
            self.user_config["user_params"][self.SERVICE_NAME] = {}
        self.user_params = self.user_config["user_params"][self.SERVICE_NAME]
        self.apply(silence=silence)
        DumpConfig(self.stuid, self.user_config)

    def apply(self, silence=None):
        res = self.session.get(url=self.service["url"])
        if not silence:
            s = res.text
            c = s.find("你的当前状态")
            state = s[c:].split('>')[1].split('<')[0]
            print(f"你的当前状态：{state}")

        if "t" not in self.user_params or self.user_params["t"] == "":
            print(
                """【现居地】
                1，高新园区、先研院、国金院
                2，合肥其他校区
                3，合肥市内校外""")
            t1 = input("请输入现居地 (1/2/3)：")
            while t1 not in ["1", "2", "3"]: t1 = input("请重新输入 (1/2/3)：")
            print(
                """【出校原因】
                1，特殊原因前往合肥市外
                2，合肥市内就医等紧急情况
                3，跨校区上课、实验等""")
            t2 = input("请输入出校原因 (1/2/3)：")
            while t2 not in ["1", "2", "3"]: t2 = input("请重新输入 (1/2/3)：")
            # 11,21,31->离校申请
            # 12,13,22,32,33->进出校申请
            # 23->跨校区报备
            self.user_params["t"] = t1 + t2

        self.params = {
            "t": self.user_params["t"]
        }
        res = self.session.get(self.service["pre-exec"], params=self.params)
        try:
            _token = res.text[res.text.find("_token"):].split("\"")[2]
            self.params["_token"] = _token
        except:
            if not silence:
                raise ApplyError("Token not found!")
            return

        nowtime = datetime.now()
        start_date = nowtime.strftime("%Y-%m-%d %H:%M:%S")
        end_date = (nowtime + timedelta(days=1)).strftime("%Y-%m-%d 23:59:59")
        self.params = {
            "_token": _token,
            "start_date": start_date,
            "end_date": end_date,
            "t": self.user_params["t"]
        }

        if not silence:
            print(f"计划申请时间：{start_date} --- {end_date}")
            # choice = input("确认报备请按回车")
            # if choice != "":
            #     return

        res = self.session.post(self.service["exec"], params=self.params, allow_redirects=False)
        res = self.session.get(res.headers["location"])

        if not silence:
            if res.text.find("报备成功") != -1:
                print("报备成功, ", end="")
            else:
                print("报备失败, ", end="")
            print("最近三次报备：")
            apply_list = res.text.split("<tbody>")[1].split("<tr>")[1:4]
            for items in apply_list:
                if not silence:
                    print(", ".join([item.split("</td>")[0] for item in items.split("<td>")[1:]]))

from config import config
from datetime import datetime, timedelta
class Apply:
    SERVICE_NAME = "daily-apply"
    service = config["service"][SERVICE_NAME]
    def __init__(self, session):
        self.session = session
        self.apply()

    def apply(self):
        res = self.session.get(url=self.service["url"])
        s = res.text
        c = s.find("你的当前状态")
        state = s[c:].split('>')[1].split('<')[0]
        print(f"你的当前状态：{state}")

        self.params = {
            "t": self.service["user-params"]["t"]
        }
        res = self.session.get(self.service["pre-exec"], params=self.params)
        try:
            _token = res.text[res.text.find("_token"):].split("\"")[2]
            self.params["_token"] = _token
        except:
            print("Token not found!")
            return

        nowtime = datetime.now()
        start_date = nowtime.strftime("%Y-%m-%d %H:%M:%S")
        end_date = (nowtime + timedelta(days=1)).strftime("%Y-%m-%d 23:59:59")
        self.params = {
            "_token": _token,
            "start_date": start_date,
            "end_date": end_date,
            "t": self.service["user-params"]["t"]
        }

        print(f"计划申请时间：{start_date} --- {end_date}")

        choice = input("确认报备请按回车")
        if choice != "":
            return

        res = self.session.post(self.service["exec"], params=self.params, allow_redirects=False)

        res = self.session.get(res.headers["location"])
        if res.text.find("报备成功"):
            print("报备成功, ", end="")
        else:
            print("报备失败, ", end="")
        print("最近三次报备：")
        apply_list = res.text.split("<tbody>")[1].split("<tr>")[1:4]
        for items in apply_list:
            print(", ".join([item.split("</td>")[0] for item in items.split("<td>")[1:]]))

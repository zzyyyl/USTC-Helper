from config import config

from config import LoadConfig, DumpConfig

import requests

fake_useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"

class ServiceError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return f"ServiceError: {self.text}"

class Login:
    def __init__(self, service, stuid=None, store_password=None, silence=None):
        try:
            self.service = config["service"][service]["login"]
        except:
            self.service = ''
        if stuid:
            self.stuid = stuid
        else:
            self.stuid = input("Student ID: ")
            if not self.stuid:
                raise UserError("Student ID cannot be empty.")
        self.user_config = LoadConfig(self.stuid)

        if "password" in self.user_config and self.user_config["password"]:
            self.password = self.user_config["password"]
        else:
            from getpass import getpass
            self.password = getpass("Password: ")

        if store_password:
            self.store_password = True
            self.user_config['store-password'] = True
        elif "store-password" in self.user_config:
            self.store_password = self.user_config['store-password']
        else:
            self.store_password = False
            self.user_config['store-password'] = False

        if self.store_password:
            self.user_config["password"] = self.password

        self.session = requests.session()

        self.load_cookies()
        self.login()
        self.dump_cookies()
        DumpConfig(self.stuid, self.user_config)

    def load_cookies(self):
        if "cookies" in self.user_config and self.user_config["cookies"]:
            for item in self.user_config["cookies"]:
                self.session.cookies.set(name=item["name"], value=item["value"], path=item["path"], domain=item["domain"])

    def dump_cookies(self):
        cookie_list = []
        for domain, sub1 in self.session.cookies._cookies.items():
            for path, sub2 in sub1.items():
                for name, cookie in sub2.items():
                    cookie_list.append({"domain": domain, "path": path, "name": name, "value": cookie.value})
        self.user_config['cookies'] = cookie_list

    def login(self):
        if not self.service: return
        res = self.session.get(url=self.service, allow_redirects=False)
        res = self.session.get(url=res.headers["location"], allow_redirects=False)
        if res.status_code != 200:
            res = self.session.get(url=res.headers["location"])
            return
        s = res.text
        c = s.find("name=\"CAS_LT\"")
        CAS_LT = s[c:].split('\"')[3]


        res = self.session.get("https://passport.ustc.edu.cn/validatecode.jsp?type=login", allow_redirects=False)

        params = {
            "model": "uplogin.jsp",
            "CAS_LT": CAS_LT,
            "service": self.service,
            "warn": "",
            "showCode": "1",
            "username": self.stuid,
            "password": self.password,
            "button": ""
        }

        res = self.session.post("https://passport.ustc.edu.cn/login", params=params, allow_redirects=False)
        res = self.session.get(res.headers["Location"])

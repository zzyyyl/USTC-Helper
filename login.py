import requests
# import cv2 as cv
# import numpy as np
# from PIL import Image
# import hashlib
import json

fake_useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"

class Login:
    def __init__(self, service):
        try:
            with open("config.json", "r", encoding = "utf-8") as f:
                self.login_config = json.load(f)
        except Exception as e:
            print(f"Open config file failed. {e}")
            self.login_config = {}
        if "student-id" in self.login_config and self.login_config["student-id"]:
            self.stuid = self.login_config["student-id"]
        else:
            self.stuid = input("Student ID: ")
            self.login_config["student-id"] = self.stuid
        if "password" in self.login_config and self.login_config["password"]:
            self.password = self.login_config["password"]
        else:
            from getpass import getpass
            self.password = getpass("Password: ")
        if "store-password" in self.login_config:
            self.store_password = self.login_config['store-password']
        else:
            choice = input("Always store password? (y/N)")
            if choice == 'y' or choice == 'Y':
                self.store_password = True
            else:
                self.store_password = False
            self.login_config['store-password'] = self.store_password
        if self.store_password:
            self.login_config["password"] = self.password
        else:
            self.login_config["password"] = ""

        self.service = service
        self.session = requests.session()
        if "cookies" in self.login_config and self.login_config["cookies"] != "":
            for x in self.login_config["cookies"]:
                self.session.cookies.set(name=x["name"], value=x["value"], path=x["path"], domain=x["domain"])
        self.login()
        self.store_config()

    def store_config(self):
        dic=[]
        for domain, sub1 in self.session.cookies._cookies.items():
            for path, sub2 in sub1.items():
                for name, cookie in sub2.items():
                    dic.append({"domain": domain, "path": path, "name": name, "value":cookie.value})
        self.login_config['cookies'] = dic
        with open("config.json", "w", encoding = "utf-8") as f:
            json.dump(self.login_config, f, indent=4)

    def login(self):
        res = self.session.get(url=self.service, allow_redirects=False)
        res = self.session.get(url=res.headers["location"], allow_redirects=False)
        if res.status_code != 200:
            res = self.session.get(url=res.headers["location"])
            return
        s = res.text
        c = s.find("name=\"CAS_LT\"")
        CAS_LT = s[c:].split('\"')[3]


        res = self.session.get("https://passport.ustc.edu.cn/validatecode.jsp?type=login", allow_redirects=False)
        #非常奇怪，只要get过上述网址，没有LT也能登录

        # this_validatecode = hashlib.md5(res.content).hexdigest()

        # if "validatecode" in self.login_config and this_validatecode in self.login_config["validatecode"]:
        #     LT = self.login_config["validatecode"][this_validatecode]
        # else:
        #     img = cv.imdecode(np.frombuffer(res.content, np.uint8), cv.IMREAD_COLOR)
        #     a = Image.fromarray(img)
        #     a.show()
        #     LT = input("input validatecode:")

        params = {
            "model": "uplogin.jsp",
            "CAS_LT": CAS_LT,
            "service": self.service,
            "warn": "",
            "showCode": "1",
            "username": self.stuid,
            "password": self.password,
            # "LT": LT,
            "button": ""
        }

        res = self.session.post("https://passport.ustc.edu.cn/login", params=params, allow_redirects=False)
        res = self.session.get(res.headers["Location"])

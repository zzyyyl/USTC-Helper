from sqlalchemy import false
from sympy import re
from .config import config
from .config import LoadConfig, DumpConfig
from bs4 import BeautifulSoup

class ApplyError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return f"ApplyError: {self.text}"

LESSONTABLE_SERVICE_NAME = "lesson-table"
config["service"][LESSONTABLE_SERVICE_NAME] = {
    "doc": "教务系统查询课程表",
    "login": "https://jw.ustc.edu.cn/ucas-sso/login",
    "url": "https://jw.ustc.edu.cn/for-std/course-table",
    "exec": "https://jw.ustc.edu.cn/for-std/course-table/get-data"
}

class LessonTable:
    SERVICE_NAME = LESSONTABLE_SERVICE_NAME
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
        self.lesson_table(silence=silence)
        DumpConfig(self.stuid, self.user_config)

    def lesson_table(self, silence=None):
        res = self.session.get(url=self.service["url"])
        document = BeautifulSoup(res.text, "html.parser")
        allSemesters = document.find(id="allSemesters")
        semesterList = []
        for option in allSemesters.find_all("option"):
            semesterList.append(
                {
                    'keywords': [option.string[0:4], option.string[5]],
                    'id': int(option.attrs['value'])
                }
            )
        def getSemesterId() -> int:
            semesterId = -1
            for item in semesterList:
                ok = True
                for keyword in item['keywords']:
                    if keyword not in self.user_params['semester']:
                        ok = False
                        break
                if ok: semesterId = item['id']
            return semesterId

        if "semester" not in self.user_params or not self.user_params["semester"]:
            self.user_params["semester"] = input("查询学期：")
        semesterId = getSemesterId()
        while semesterId == -1:
            self.user_params["semester"] = input("查询学期：")
            semesterId = getSemesterId()

        print(semesterId)
        dataId = int(res.text.split("var dataId = ", 1)[1].split(";", 1)[0])
        bizTypeId = int(res.text.split("bizTypeId: ", 1)[1].split(",", 1)[0])
        res = self.session.get(url=self.service['exec'], params = {
            "semesterId": semesterId,
            "bizTypeId": bizTypeId,
            "dataId": dataId,
        })
        print({
            "semesterId": semesterId,
            "bizTypeId": bizTypeId,
            "dataId": dataId,
        })
        print(res.text)
config["service"][LESSONTABLE_SERVICE_NAME]["entry"] = LessonTable

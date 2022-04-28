from .config import config
from .config import LoadConfig, DumpConfig
from bs4 import BeautifulSoup
import json
import numpy as np
from datetime import datetime, timedelta, timezone

timeline_t = [('beginTime', datetime), ("endTime", datetime), ("event", dict)]

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
CLASSTIME = [
    "7:50-8:35",
    "8:40-9:25",
    "9:45-10:30",
    "10:35-11:20",
    "11:25-12:10",
    "14:00-14:45",
    "14:50-15:35",
    "15:55-16:40",
    "16:45-17:30",
    "17:35-18:20",
    "19:00-19:45",
    "19:50-20:35",
    "20:40-21:25"
]
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

        dataId = int(res.text.split("var dataId = ", 1)[1].split(";", 1)[0])
        bizTypeId = int(res.text.split("bizTypeId: ", 1)[1].split(",", 1)[0])
        res = self.session.get(url=self.service['exec'], params={
            "semesterId": semesterId,
            "bizTypeId": bizTypeId,
            "dataId": dataId,
        })
        context = json.loads(res.text)
        courses = []
        for lesson in context["lessons"]:
            start_date = datetime.strptime(lesson["semester"]["startDate"], "%Y-%m-%d")
            end_date = datetime.strptime(lesson["semester"]["endDate"], "%Y-%m-%d")

            classes_in_week = []
            for x in lesson["scheduleGroupStr"].split('\n'):
                items = x.split(' ')
                classes_in_week.append({
                    "weekday": int(items[2].split(':', 1)[1].split('(', 1)[0]),
                    "classes": [int(xi) for xi in items[2].split('(', 1)[1].split(')', 1)[0].split(',')],
                    "room": items[1],
                    "teacher": items[3]
                })

            if start_date.weekday():
                start_date = start_date + timedelta(days=7-start_date.weekday())
            weeks_exact = [start_date + timedelta(days=7*(x-1))
                for x in lesson["suggestScheduleWeeks"]]
            classes_exact = []
            for week_exact in weeks_exact:
                for item in classes_in_week:
                    start_time = CLASSTIME[item["classes"][0]-1].split('-')[0]
                    end_time = CLASSTIME[item["classes"][-1]-1].split('-')[1]
                    day_exact = week_exact + timedelta(days=item["weekday"] - 1)
                    classes_exact.append({
                        "startTime": day_exact.replace(
                            hour=int(start_time.split(':')[0]),
                            minute=int(start_time.split(':')[1])),
                        "endTime": day_exact.replace(
                            hour=int(end_time.split(':')[0]),
                            minute=int(end_time.split(':')[1])),
                        "room": item["room"],
                        "teacher": item["teacher"]
                    })
            courses.extend([
                {
                    "name": lesson["course"]["nameZh"],
                    "room": x["room"],
                    "teacher": x["teacher"],
                    "startTime": x["startTime"].strftime("%Y-%m-%d %H:%M:%S"),
                    "endTime": x["endTime"].strftime("%Y-%m-%d %H:%M:%S")
                } for x in classes_exact
            ])
        coursesList = []
        for course in courses:
            coursesList.append((course["startTime"], course["endTime"], json.dumps({
                "name": course["name"],
                "room": course["room"],
                "teacher": course["teacher"]
            }, ensure_ascii=False)))
        coursesArray = np.array(coursesList, dtype=timeline_t)
        coursesArray.sort(axis=0, order=('beginTime', 'endTime'))
        coursesDict = {}
        for item in coursesArray:
            day = item["beginTime"].split(' ')[0]
            if day not in coursesDict:
                coursesDict[day] = []
            event = json.loads(item["event"])
            coursesDict[day].append({
                "beginTime": item["beginTime"].split(' ')[1],
                "endTime": item["endTime"].split(' ')[1],
                "event": f"{event['name']}, {event['room']}, {event['teacher']}"
            })
        # coursesList = coursesArray.tolist()
        print(json.dumps(coursesDict, indent=4, ensure_ascii=False))
        # print(json.dumps(context["lessons"][0], indent=4, ensure_ascii=False))
config["service"][LESSONTABLE_SERVICE_NAME]["entry"] = LessonTable

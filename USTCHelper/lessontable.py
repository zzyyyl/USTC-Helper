from typing import Optional, Tuple
from bs4 import BeautifulSoup
import json
import numpy as np
from datetime import datetime, timedelta, timezone
from submodules import AmiyaTimePlanner
from .config import config
from .config import LoadConfig, DumpConfig

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
    def __init__(self, session, stuid, silence=None, params=None):
        self.result = r"{}"
        self.session = session
        self.stuid = stuid
        self.user_config = LoadConfig(self.stuid)
        if params:
            self.now, params = AmiyaTimePlanner.utils.getDateFromParams(params=params)
            if params:
                self.now, params = self._getTimeFromParams(params=params, now=self.now)
        else:
            self.now = datetime.now() 
        if "user_params" not in self.user_config:
            self.user_config["user_params"] = {}
        if self.SERVICE_NAME not in self.user_config["user_params"]:
            self.user_config["user_params"][self.SERVICE_NAME] = {}
        self.user_params = self.user_config["user_params"][self.SERVICE_NAME]
        self.lesson_table(silence=silence)
        DumpConfig(self.stuid, self.user_config)

    @staticmethod
    def _getTimeFromParams(params: str, now=datetime.now()) -> Tuple[datetime, Optional[str]]:
        params = params.split(' ', 1)
        _time = AmiyaTimePlanner.utils.getTimeFromStr(params[0])
        if _time:
            _time = now.replace(hour=_time.hour, minute=_time.minute, second=_time.second)
        else:
            _time = now.replace(hour=0, minute=0, second=0)
        if len(params) == 1: return (_time, None)
        else: return (_time, params[1])

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
                tmp = items[2].split('(', 1)[1].split(')', 1)[0]
                if len(tmp.split(',')) == 1:
                    classes = tmp.split('~')
                    if len(classes) != 2:
                        raise ValueError("Unrecognized class: ", x)
                    start_time = classes[0]
                    end_time = classes[1]
                else:
                    classes = [int(xi) for xi in tmp.split(',')]
                    start_time = CLASSTIME[classes[0]-1].split('-')[0]
                    end_time = CLASSTIME[classes[-1]-1].split('-')[1]
                added = False
                for item in classes_in_week:
                    if item["weekday"] == int(items[2].split(':', 1)[1].split('(', 1)[0]) \
                    and item["startTime"] == start_time \
                    and item["endTime"] == end_time:
                        item["teacher"] = item["teacher"] + "," + items[3]
                        added = True
                        break
                if not added:
                    classes_in_week.append({
                        "weekday": int(items[2].split(':', 1)[1].split('(', 1)[0]),
                        "startTime": start_time,
                        "endTime": end_time,
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
                    start_time = item["startTime"]
                    end_time = item["endTime"]
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
        self.result = json.dumps(coursesDict, ensure_ascii=False)
        if not silence:
            AmiyaTimePlanner.utils.timeline(now=self.now, config={"day": coursesDict})

config["service"][LESSONTABLE_SERVICE_NAME]["entry"] = LessonTable

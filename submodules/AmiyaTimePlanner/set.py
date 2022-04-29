from datetime import datetime, timedelta
import json
import numpy as np

timeline_t = [('beginTime', datetime), ("endTime", datetime), ("event", dict)]

WEEK = ["Mon", "Tue", "Wed", "Thr", "Fri", "Sat", "Sun"]
lower_week = [x.lower() for x in WEEK]

DAY = ["Today", "Tomorrow"]
lower_day = [x.lower() for x in DAY]

# TODO. 把 assert 改为自定义错误类型

def accept() -> bool:
	choice = 'n'
	while True:
		choice = input("(y/n)").lower()
		if choice in ['y', 'n']: break
	return choice == 'y'

def isTime(param: str) -> bool:
	time_params = param.split(':')
	if len(time_params) != 2:
		return False
	hours = time_params[0]
	minutes = time_params[1]
	if not (hours.isdecimal() and minutes.isdecimal()):
		return False
	hours = int(hours)
	minutes = int(minutes)
	if hours < 0 or hours > 23:
		return False
	if minutes < 0 or minutes > 59:
		return False
	return True

def loadConfig(config_path="timeline.json", config=None):
	if config:
		if type(config) == str:
			time_schedule = json.loads(config)
			if type(time_schedule) != dict:
				raise RuntimeError(f"type(time_schedule) is `{type(time_schedule)}`, but should be `dict`.")
		elif type(config) == dict:
			time_schedule = config
		else:
			raise RuntimeError(f"type(config) is `{type(config)}`, but should be `str` or `dict`.")
	else:
		try:
			with open(config_path, "r", encoding="utf8") as f:
				time_schedule = json.load(f)
			assert type(time_schedule) == dict
		except:
			time_schedule = {}
	if "week" in time_schedule:
		assert type(time_schedule["week"]) == list
	else:
		time_schedule["week"] = [[] for x in range(7)]
	if "day" in time_schedule:
		assert type(time_schedule["day"]) == dict
	else:
		time_schedule["day"] = {}
	return time_schedule

def dumpConfig(time_schedule, config_path="timeline.json"):
	if config_path:
		with open(config_path, "w", encoding="utf8") as f:
			json.dump(time_schedule, f, indent=2)

# Week 0 13:30-15:30 doSomething
# Week Mon 13:30-15:30 doSomething
def addWeekEvent(params: str, now, time_schedule):
	assert "week" in time_schedule
	week_schedule = time_schedule["week"]
	assert type(week_schedule) == list
	assert type(params) == str
	params = params.split(' ', 1)
	if params[0].lower() in lower_week:
		week_index = lower_week.index(params[0].lower())
	else:
		week_index = int(params[0])
	params = params[1].split(' ', 1)
	if '-' in params[0]:
		assert len(params[0].split('-')) == 2
		beginTime, endTime = params[0].split('-')
	else:
		beginTime = params[0]
		params = params[1].split(' ', 1)
		endTime = params[0]
	event = params[1] #allows space
	assert (isTime(beginTime) and isTime(endTime))
	print(WEEK[week_index], f"{beginTime}-{endTime}, {event}")
	if accept():
		week_schedule[week_index].append({
			"beginTime": beginTime,
			"endTime": endTime,
			"event": event
		})
		dumpConfig(time_schedule=time_schedule)
		print("Adding success.")

def getDayFromParams(params: str, now=datetime.now()):
	assert type(params) == str
	params = params.split(' ', 1)
	param = params[0].lower()
	if param in lower_day:
		day_index = lower_day.index(param)
		day_formatted = now + timedelta(days=day_index)
	elif param.isdecimal():
		day_index = int(param)
		day_formatted = now + timedelta(days=day_index)
	elif param[:4] == "next" and param[-4:] == "week":
		if param[4:-4] == '':
			week_count = 1
		else:
			week_count = int(param[4:-4])
		params = params[1].split(' ', 1)
		param = params[0].lower()
		if param in lower_week:
			weekday_index = lower_week.index(param)
		else:
			weekday_index = int(param)
		day_index = week_count * 7 - now.weekday() + weekday_index
		day_formatted = now + timedelta(days=day_index)
	elif param == "thisweek":
		params = params[1].split(' ', 1)
		param = params[0].lower()
		if param in lower_week:
			weekday_index = lower_week.index(param)
		else:
			weekday_index = int(param)
		day_index = weekday_index - now.weekday()
		day_formatted = now + timedelta(days=day_index)
	else:
		while True:
			try: day_formatted = datetime.strptime(param, "%Y-%m-%d")
			except: pass
			else: break
			try: day_formatted = datetime.strptime(param, "%y-%m-%d")
			except: pass
			else: break
			try: day_formatted = datetime.strptime(param, "%m-%d").replace(year=now.year)
			except: pass
			else: break
			raise ValueError("Unrecognized time data " + param)
	if len(params) == 1:
		return (day_formatted, None)
	else:
		return (day_formatted, params[1])

# Day today 13:30-15:30 doSomething
# Day 0 13:30-15:30 doSomething
# Day 2022-4-13 13:30-15:30 doSomething
# Day thisweek Mon 13:30-15:30 doSomething
# Day nextweek Mon 13:30-15:30 doSomething
# Day next1week Mon 13:30-15:30 doSomething
def addDayEvent(params: str, now, time_schedule):
	assert "day" in time_schedule
	day_schedule = time_schedule["day"]
	assert type(day_schedule) == dict

	day_formatted, params = getDayFromParams(params=params, now=now)

	params = params.split(' ', 1)
	if '-' in params[0]:
		assert len(params[0].split('-')) == 2
		beginTime, endTime = params[0].split('-')
	else:
		beginTime = params[0]
		params = params[1].split(' ', 1)
		endTime = params[0]
	event = params[1] #allows space
	assert (isTime(beginTime) and isTime(endTime))
	dateYmd = day_formatted.strftime("%Y-%m-%d")
	print(dateYmd, f"{beginTime}-{endTime}, {event}")
	if accept():
		if dateYmd not in day_schedule:
			day_schedule[dateYmd] = []
		day_schedule[dateYmd].append({
			"beginTime": beginTime,
			"endTime": endTime,
			"event": event
		})
		dumpConfig(time_schedule=time_schedule)
		print("Adding success.")

def addEvent(input_string, now, time_schedule):
	assert ' ' in input_string
	scheduleType, params = input_string.split(' ', 1)
	scheduleType = scheduleType.lower()
	if scheduleType == "week":
		addWeekEvent(params=params, now=now, time_schedule=time_schedule)
	elif scheduleType == "day":
		addDayEvent(params=params, now=now, time_schedule=time_schedule)
	else:
		assert False

def main():
	time_schedule = loadConfig()
	while True:
		try:
			addEvent(input_string=input("Add event:"),
						time_schedule=time_schedule,
						now=datetime.now())
		except (KeyboardInterrupt, EOFError):
			break
		except AssertionError as e:
			print(e.__repr__())
		except Exception as e:
			raise

if __name__ == '__main__':
	main()
	print("Exit.")

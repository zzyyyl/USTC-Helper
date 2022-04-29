from datetime import datetime
import json
import numpy as np
import random

timeline_t = [('beginTime', datetime), ("endTime", datetime), ("event", dict)]

message = {
	"ongoing": [
		"博士，您还有许多事情需要处理。现在还不能休息哦。",
		"ドクター、終わってない仕事がたくさんありますから、まだ休んじゃだめですよ。"
	],
	"waiting": [
		"咻，应该可以小小休息一下了吧。",
		"ふう、これで少しは休めますね。"
	],
	"finish": [
		"博士，您工作辛苦了。",
		"ドクター、お仕事お疲れ様です。"
	]
}

def loadConfig():
	try:
		with open("timeline.json", "r", encoding="utf8") as f:
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

def getDayPlan(now, time_schedule):
	today_schedule = []

	weekday = now.weekday()
	week_schedule = time_schedule["week"]
	if weekday < len(week_schedule):
		assert type(week_schedule[weekday]) == list 
		today_schedule.extend(week_schedule[weekday])

	todayYmd = now.strftime("%Y-%m-%d")
	day_schedule = time_schedule["day"]
	if todayYmd in day_schedule:
		assert type(day_schedule[todayYmd]) == list 
		today_schedule.extend(day_schedule[todayYmd])

	return today_schedule

def classify(now, today_schedule):
	ongoing_events = []
	waiting_events = []

	for item in today_schedule:
		beginTime = datetime.strptime(item["beginTime"], "%H:%M")
		beginTime = now.replace(hour=beginTime.hour, minute=beginTime.minute, second=0)

		endTime = datetime.strptime(item["endTime"], "%H:%M")
		endTime = now.replace(hour=endTime.hour, minute=endTime.minute, second=0)

		if item["event"]:
			if beginTime <= now and now <= endTime:
				ongoing_events.append((beginTime, endTime, item["event"]))
			elif now < beginTime:
				waiting_events.append((beginTime, endTime, item["event"]))

	ongoing_events_array = np.array(ongoing_events, dtype=timeline_t)
	ongoing_events_array.sort(axis=0, order=('beginTime', 'endTime', 'event'))

	waiting_events_array = np.array(waiting_events, dtype=timeline_t)
	waiting_events_array.sort(axis=0, order=('beginTime', 'endTime', 'event'))

	return ongoing_events_array, waiting_events_array

def main():
	now = datetime.now()
	random.seed(now.timestamp())
	time_schedule = loadConfig()
	today_schedule = getDayPlan(now, time_schedule)
	ongoing_events_array, waiting_events_array = classify(now, today_schedule)
	ongoing_events_count = len(ongoing_events_array)
	waiting_events_count = len(waiting_events_array)

	print(now.strftime("%Y-%m-%d %H:%M:%S"), end='\n\n')

	if ongoing_events_count:
		print(message["ongoing"][random.randint(0, len(message["ongoing"])-1)], end='\n\n')
		print("---Ongoing---")
		for item in ongoing_events_array:
			print(f"{item['event']}, {item['beginTime'].strftime('%H:%M')}-{item['endTime'].strftime('%H:%M')}")
			print("Countdown:", item["endTime"] - now)
			print()
		if waiting_events_count:
			print("---Waiting---")
			for item in waiting_events_array:
				print(f"{item['event']}, {item['beginTime'].strftime('%H:%M')}-{item['endTime'].strftime('%H:%M')}")
				print("Countdown:", item["beginTime"] - now)
				print()
	elif waiting_events_count:
		print(message["waiting"][random.randint(0, len(message["waiting"])-1)], end='\n\n')
		print("---Waiting---")
		for item in waiting_events_array:
			print(f"{item['event']}, {item['beginTime'].strftime('%H:%M')}-{item['endTime'].strftime('%H:%M')}")
			print("Countdown:", item["beginTime"] - now)
			print()
	else:
		print(message["finish"][random.randint(0, len(message["finish"])-1)], end='\n\n')

if __name__ == '__main__':
	main()

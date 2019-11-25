from urllib.request import urlopen
import bs4 as BeautifulSoup

import re
from datetime import datetime
import time

from flask import Flask, request

import json
from operator import itemgetter
from apscheduler.scheduler import Scheduler

STANDARD_DELAY = 60
STANDARD_DELETION = 1200
JV_PAGE_SIZE = 26

topics = {}

def heure():
	return str(datetime.now())

def delete_topics(topics):
	now = datetime.timestamp(datetime.now())
	remove = [topic for topic in topics.items() if (now - topic[1][-1][0]) > STANDARD_DELETION]

	for to_remove in remove:
		del topics[to_remove[0]]
		print("Topic supprimé : " + to_remove[0])

	print(str(len(topics)) + " topics trackés.")

def my_counter(topics):
	html = urlopen('http://www.jeuxvideo.com/forums/0-51-0-1-0-1-0-blabla-18-25-ans.htm', timeout = 120).read()

	soup = BeautifulSoup.BeautifulSoup(html, features="html.parser")

	page_topic_content = soup.find_all('ul', class_='topic-list topic-list-admin')

	nowa = datetime.now()
	now = datetime.timestamp(nowa)

	for i in range(1, JV_PAGE_SIZE):
		raw_title = page_topic_content[0].find_all('span', class_="topic-subject")[i].text
		raw_count = page_topic_content[0].find_all('span', class_="topic-count")[i].text

		title = re.sub(r"^\s+|\s+$", "", raw_title)
		count = float(re.sub(r"^\s+|\s+$", "", raw_count)) + 1

		if (title in topics.keys()):
			topics[title].append((now,count))
		else:
			topics[title] = [(now,count)]

def main():
	while(1):
		my_counter(topics)
		delete_topics(topics)
		time.sleep(STANDARD_DELAY)

app = Flask(__name__)

@app.route("/trends", methods = ['GET'])
def trends():
	top = request.args.get('top', default = 1, type = int)
	interval = request.args.get('interval', default = 1, type = int)

	result = []
	for topic in topics.items():
		size = len(topic[1])
		last = size - 1

		limit = min(interval, last)
		old_count = topic[1][last - limit][1]
		new_count = topic[1][last][1]
		delta = new_count - old_count
		title = topic[0]

		result.append((title, delta, old_count, new_count))

	result.sort(key=itemgetter(1))
	result = result[-top:]

	json_res = json.dumps(result)
	return json_res, 200

@app.before_first_request
def before():
	scheduler = Scheduler()
	scheduler.start()
	scheduler.add_interval_job(main, seconds=5)
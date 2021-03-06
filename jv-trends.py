import urllib
import bs4 as BeautifulSoup
import re
from datetime import datetime
import time

import json
from operator import itemgetter
import threading

from flask import Flask
from flask import request

STANDARD_DELAY = 5
STANDARD_DELETION = 120
JV_PAGE_SIZE = 26

topics = {}

def log(string):
	print(string)

def timestamp_minute():
	"""
	This method returns the cur timestamp as minute, in a entire value.
	"""
	return int(datetime.timestamp(datetime.now()) // 60)

def delete_topics(topics):
	"""
	This method creates a list of topics to delete and then delete each one of it.
	"""
	now = timestamp_minute()
	remove = [topic for topic in topics.items() if (now - most_recent_before(topic, 0)) > STANDARD_DELETION]

	for to_remove in remove:
		del topics[to_remove[0]]
		log("Deleted topic: " + to_remove[0])

	log(str(len(topics)) + " tracked topics")

def most_recent_before(topic, duration):
	"""
	Returns the most recent count before a certain moment (duration)
	"""
	count = topic[1]["count"]
	now = max(i for i in count.keys())
	limit =  now - duration
	most_recent = max((i for i in count.keys() if i <= limit))

	return most_recent

def oldest_after(topic, duration):
	"""
	Returns the oldest count after a certain moment (duration)
	"""
	count = topic[1]["count"]
	now = max(i for i in count.keys())
	limit =  now - duration
	oldest = min((i for i in count.keys() if i >= limit))

	return oldest

def get_data(topics):
	"""
	Fetch forum main page and add it in dict "topics" in the following format:
	{"topic_1_title": {"link" : topic_link, "count": {time_t: count_at_t, time_t1: count_at_t1}}
	}
	"""

	try:
		html = urllib.request.urlopen('http://www.jeuxvideo.com/forums/0-51-0-1-0-1-0-blabla-18-25-ans.htm', timeout = 120).read()
	except urllib.error.URLError:
		log("Bad URL or timeout")
		return

	soup = BeautifulSoup.BeautifulSoup(html, features="html.parser")

	page_topic_content = soup.find('ul', class_='topic-list topic-list-admin')

	if page_topic_content is None:
		return

	topic_list = page_topic_content.find_all('li', class_='')

	if topic_list is None:
		return

	now = timestamp_minute()
	for topic in topic_list:
		raw_count = topic.find('span', class_="topic-count").text

		if raw_count is None:
			raw_count = "0"

		link = topic.find('a', class_="lien-jv topic-title")["href"]
		if link is None:
			link = "http://www.google.fr"

		title = topic.find('a', class_="lien-jv topic-title")["title"]
		if title is None:
			title = "DEFAULT TITLE"

		new_count = float(re.sub(r"^\s+|\s+$", "", raw_count)) + 1
		if new_count is None:
			new_count = 0

		if (title in topics.keys()):
			topics[title]["count"][now] = new_count
		else:
			topics[title] = {"link" : link, "count" : {now: new_count}}

def monitoring_loop():
	"""
	Program loop. It will loop infinitely, on a background thread.
	Periodically it will fetch forum data and add it to dictionnary "topics".
	"""
	while(1):
		get_data(topics)
		delete_topics(topics)
		time.sleep(STANDARD_DELAY)

class MyFlaskApp(Flask):
	def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
		print("started")
		if not self.debug:
			with self.app_context():
				threading.Thread(target=monitoring_loop).start()
				super(MyFlaskApp, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)

app = MyFlaskApp(__name__)

@app.route("/trends", methods = ['GET'])
def trends():
	"""
		Root to access results: /trends. It takes two parameters in GET method: top and interval.
		Return the "top" topics the most active during "interval".

		Example of usage: http://your-ip-address:your-port/trends?interval=60&top=3
		The request just above will return a JSON formatted response
		containing the 3 most active topics during the 60 last minutes.
	"""
	top = request.args.get('top', default = 20, type = int)
	begin = request.args.get('begin', default = 120, type = int)
	end = request.args.get('end', default = 0, type = int)

	result_json = {}

	result_json["top"] = top
	result_json["begin"] = begin
	result_json["end"] = end

	# Create topic array
	topics_array = []
	for topic in topics.copy().items():
		size = len(topic[1]["count"])
		last = size - 1

		link = topic[1]["link"]
		old_count = topic[1]["count"][oldest_after(topic, begin)]
		new_count = topic[1]["count"][most_recent_before(topic, end)]
		delta = new_count - old_count
		title = topic[0]

		topics_array.append({"title" : title, "link" : link, "oldval" : old_count, "newval" : new_count, "delta" : delta})

	topics_array = sorted(topics_array, key = lambda i: (i['delta']), reverse = True)
	topics_array = topics_array[:top]

	result_json["topics"] = topics_array

	json_res = json.dumps(result_json)
	return json_res, 200

app.run(host="0.0.0.0", port=5000)
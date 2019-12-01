from urllib.request import urlopen
import bs4 as BeautifulSoup

import re
from datetime import datetime
import time

from flask import Flask, request

import json
from operator import itemgetter
from apscheduler.scheduler import Scheduler

STANDARD_DELAY = 5
STANDARD_DELETION = 14400
JV_PAGE_SIZE = 26

topics = {}

# Retourne la date + l'heure sous forme de string
def heure():
	return str(datetime.now())

def timestamp_minutes():
	return int(datetime.timestamp(datetime.now()) // 60)

# Cette fonction supprime les topics plus vieux que STANDARD_DELETION secondes.
def delete_topics(topics):
	now = datetime.timestamp(datetime.now())
	remove = [topic for topic in topics.items() if (now - topic[1][-1][0]) > STANDARD_DELETION]

	for to_remove in remove:
		del topics[to_remove[0]]
		print("Topic supprimé : " + to_remove[0])

	print(str(len(topics)) + " topics trackés.")

# Récupère la liste des 25 topics en première page du forum 18-25 de JVC et les stocke dans le dictionnaire "topics" 
# sous la forme suivante: 
# {"nom_topic1":[(t, count_at_t), (t+1, count_at_t+1)],
# "nom_topic2":[(t, count_at_t), (t+1, count_at_t+1)]
# }
def my_counter(topics):
	html = urlopen('http://www.jeuxvideo.com/forums/0-51-0-1-0-1-0-blabla-18-25-ans.htm', timeout = 120).read()

	soup = BeautifulSoup.BeautifulSoup(html, features="html.parser")

	page_topic_content = soup.find_all('ul', class_='topic-list topic-list-admin')

	now = timestamp_minutes()

	for i in range(1, JV_PAGE_SIZE):
		raw_title = page_topic_content[0].find_all('span', class_="topic-subject")[i].text
		raw_count = page_topic_content[0].find_all('span', class_="topic-count")[i].text

		title = re.sub(r"^\s+|\s+$", "", raw_title)
		new_count = float(re.sub(r"^\s+|\s+$", "", raw_count)) + 1

		if (title in topics.keys()):
			topics[title][now] = new_count
		else:
			topics[title] = {now:new_count}

# Boucle du programme executée sur un thread secondaire
def main():
	while(1):
		my_counter(topics)
		# delete_topics(topics)
		time.sleep(STANDARD_DELAY)

app = Flask(__name__)

# Route pour accéder aux résultats, deux paramêtres entiers:
# La valeur de "top" sert à retourner les topics les plus chauds au cours de l'intervalle "interval" 
@app.route("/trends", methods = ['GET'])
def trends():
	top = request.args.get('top', default = 1, type = int)
	interval = request.args.get('interval', default = 1, type = int)
	interval_seconds = interval * 60
	result_json = {}

	result_json["top"] = top
	result_json["interval"] = interval

	# Create topic array
	topics_array = []
	
	now = timestamp_minutes()
	
	for topic in topics.items():
		size = len(topic[1])
		last = size - 1

		limit = min(interval, last)
		
		i = 0
		while (now not in topic[1].keys()):
			now = now - 1

		old = now
		while (old in topic[1].keys() and now - old < interval):
			old = old - 1

		old_count = topic[1][now][1]
		new_count = topic[1][now][1]
		delta = new_count - old_count
		title = topic[0]

		topics_array.append({"title" : title, "oldval" : old_count, "newval" : new_count, "delta" : delta})

	topics_array = sorted(topics_array, key = lambda i: (i['delta']), reverse = True) 
	topics_array = topics_array[:top]

	result_json["topics"] = topics_array

	json_res = json.dumps(result_json)
	return json_res, 200

@app.before_first_request
def before():
	scheduler = Scheduler()
	scheduler.start()
	scheduler.add_interval_job(main, seconds=5)
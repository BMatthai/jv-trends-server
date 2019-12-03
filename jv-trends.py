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
def timestamp_minute():
	return int(datetime.timestamp(datetime.now()) // 60)

# Cette fonction supprime les topics plus vieux que STANDARD_DELETION secondes.
def delete_topics(topics):
	now = datetime.timestamp(datetime.now())
	remove = [topic for topic in topics.items() if (now - topic[1]["count"][-1][0]) > STANDARD_DELETION]

	for to_remove in remove:
		del topics[to_remove[0]]
		print("Topic supprimé : " + to_remove[0])

	print(str(len(topics)) + " topics trackés.")

def delta_from_topic(topic, begin, end = 0):
	now = timestamp_minute()

	if (topic[1]["count"][0][0] > (now - begin)):
		return topic[1]["count"][-1 - end][1] - topic[1]["count"][0][1]
	else: 
		return topic[1]["count"][-1 - end][1] - topic[1]["count"][-1 - begin][1]
	return 0

	# cur_time = datetime.timestamp(datetime.now())
	# first_time = topic[1]["count"][0][0]

	# if (cur_time - begin > first_time)

		# i = 0

		# interval = end - begin
		
		# topic[1]["count"][i][0]
		# while (topic[1]["count"][last][1] - topic[1]["count"][i][1] > interval_seconds):
		# 	i = i + 1

# Récupère la liste des 25 topics en première page du forum 18-25 de JVC et les stocke dans le dictionnaire "topics" 
# sous la forme suivante: 
# {"nom_topic1":[(t, count_at_t), (t+1, count_at_t+1)],
# "nom_topic2":[(t, count_at_t), (t+1, count_at_t+1)]
# }
def my_counter(topics):
	html = urlopen('http://www.jeuxvideo.com/forums/0-51-0-1-0-1-0-blabla-18-25-ans.htm', timeout = 120).read()

	soup = BeautifulSoup.BeautifulSoup(html, features="html.parser")

	page_topic_content = soup.find('ul', class_='topic-list topic-list-admin')

	now = timestamp_minute()

	topicsl = page_topic_content.find_all('li', class_='')
	
	for topic in topicsl:
		raw_count = topic.find('span', class_="topic-count").text

		link = topic.find('a', class_="lien-jv topic-title")["href"]
		title = topic.find('a', class_="lien-jv topic-title")["title"]
		new_count = float(re.sub(r"^\s+|\s+$", "", raw_count)) + 1

		if (title in topics.keys()):
			# Si le moment courant est la même minute que le dernier élement du tableau
			last_element = topics[title]["count"][-1]
			if (now == last_element[0]):
				if (new_count > last_element[1]):
					last_element = (now, new_count)
			else:
				topics[title]["count"].append((now, new_count))
		else:
			topics[title] = {"link" : link, "count" : [(now, new_count)]}

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
	for topic in topics.items():
		size = len(topic[1]["count"])
		last = size - 1

		limit = min(interval, last)
		
		i = 0
		# Voir si la condition est OK...
		while (topic[1]["count"][last][1] - topic[1]["count"][i][1] > interval_seconds):
			i = i + 1

		link = topic[1]["link"]
		old_count = topic[1]["count"][i][1]
		new_count = topic[1]["count"][last][1]
		delta = delta_from_topic(topic, interval, 0)

		# new_count - old_count
		title = topic[0]

		topics_array.append({"title" : title, "link" : link, "oldval" : old_count, "newval" : new_count, "delta" : delta})

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
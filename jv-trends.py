from urllib.request import urlopen
import bs4 as BeautifulSoup
import re
from datetime import datetime
import time
from flask import Flask, request
import json
from operator import itemgetter
import threading

STANDARD_DELAY = 5
STANDARD_DELETION = 120
JV_PAGE_SIZE = 26

topics = {}

def log(string):
	print(string)

# Retourne la date + l'heure sous forme de string
def timestamp_minute():
	return int(datetime.timestamp(datetime.now()) // 60)

# Cette fonction supprime les topics plus vieux que STANDARD_DELETION secondes.
# def delete_topics(topics):
# 	now = timestamp_minute()
# 	remove = [topic for topic in topics.items() if (now - topic[1]["count"][-1][0]) > STANDARD_DELETION]

# 	for to_remove in remove:
# 		del topics[to_remove[0]]
# 		log("Topic supprimé : " + to_remove[0])

# 	log(str(len(topics)) + " topics trackés.")


def count_before(topic, duration):
	now = timestamp_minute()
	count = topic[1]["count"]
	limit =  now - duration
	max_val = max(i for i in count.keys() if i <= limit, default = 0)
    
	return count[max_val]


def count_after(topic, duration):
	now = timestamp_minute()
	count = topic[1]["count"]
	limit =  now - duration
	min_val = min(i for i in count.keys() if i >= limit, default = 0)
    
	return count[min_val]

def delta_from_topic(topic, begin, end = 0):
	now = timestamp_minute()
	counts = topic[1]["count"]

	if (end > begin):
		return 0

	# Si begin fait référence à un moment avant le début du tracking, renvoyer début du tracking
	if (counts[0][0] > now - begin):
		log("Topic tracké depuis pas longtemps on renvoie le delta maximal")
		return counts[-1][1] - counts[0][1]

	for index, element in enumerate(counts):
		if (now - begin >= element[0]):
			log("Différence compteur " + str(now - begin) + " à " + str(now) + " (" + str(counts[index][1]) + " -> " + str(counts[-1][1]) + ")")
			return counts[-1][1] - counts[index][1]
	return 0

# Récupère la liste des 25 topics en première page du forum 18-25 de JVC et les stocke dans le dictionnaire "topics" 
# sous la forme suivante: 
# {"nom_topic1":[(t, count_at_t), (t+1, count_at_t+1)],
# "nom_topic2":[(t, count_at_t), (t+1, count_at_t+1)]
# }
def get_data(topics):
	html = urlopen('http://www.jeuxvideo.com/forums/0-51-0-1-0-1-0-blabla-18-25-ans.htm', timeout = 120).read()

	soup = BeautifulSoup.BeautifulSoup(html, features="html.parser")

	page_topic_content = soup.find('ul', class_='topic-list topic-list-admin')

	now = timestamp_minute()

	topic_list = page_topic_content.find_all('li', class_='')
	
	for topic in topic_list:
		raw_count = topic.find('span', class_="topic-count").text

		link = topic.find('a', class_="lien-jv topic-title")["href"]
		title = topic.find('a', class_="lien-jv topic-title")["title"]
		new_count = float(re.sub(r"^\s+|\s+$", "", raw_count)) + 1

		if (title in topics.keys()):
			topics[title]["count"][now] = new_count
		else:
			topics[title] = {"link" : link, "count" : {now: new_count}}

# Boucle du programme executée sur un thread secondaire
def main():
	while(1):
		get_data(topics)
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
	for topic in topics.copy().items():
		size = len(topic[1]["count"])
		last = size - 1

		limit = min(interval, last)
		
		link = topic[1]["link"]
		old_count = count_after(topic, interval)
		new_count = count_before(topic, 0)
		delta = new_count - old_count
		title = topic[0]

		topics_array.append({"title" : title, "link" : link, "oldval" : old_count, "newval" : new_count, "delta" : delta})

	topics_array = sorted(topics_array, key = lambda i: (i['delta']), reverse = True) 
	topics_array = topics_array[:top]

	result_json["topics"] = topics_array

	json_res = json.dumps(result_json)
	return json_res, 200

@app.before_first_request
def before():
	threading.Thread(target=main).start()
from urllib.request import urlopen
import bs4 as BeautifulSoup

import re
from datetime import datetime
import time

STANDARD_DELAY = 60
STANDARD_DELETION = 1200
JV_PAGE_SIZE = 26

def heure():
	return str(datetime.now())

def my_write(file, string):
	file.write(string)
	print(string)

def display_sorted(file, interval, evolution_time):
	if (evolution_time == {}):
		return
	my_write(file, "----------------------\n")
	my_write(file, heure() + ". Topic les plus actifs sur les " + interval + " dernières minutes:\n")
	sorted_list = sorted(evolution_time.items(), key = lambda kv:(kv[1]))
	sorted_list = sorted_list[-5:]
	for i in sorted_list:
		my_write(file, i[0] + "\n")

def delete_topics(topics):
	now = datetime.timestamp(datetime.now())
	remove = [topic for topic in topics.items() if (now - topic[1][-1][0]) > STANDARD_DELETION]

	for to_remove in remove:
		del topics[to_remove[0]]
		print("Topic supprimé : " + to_remove[0])

	print(str(len(topics)) + " topics trackés.")

def display_counter(topics):
	file = open("./topic_file.txt", "w")
	
	evolution = [{}, {}, {}, {}]

	tab = [10, 60, 120, 240]

	for topic in topics.items():
		size = len(topic[1])
		last = size - 1

		new_count = topic[1][last][1]

		title = topic[0]

		for index, value in enumerate(tab):
			limit = min(value, last)
			time_counter = new_count - topic[1][last - limit][1]
			evolution[index][title] = time_counter

	for index, value in enumerate(tab):
		display_sorted(file, str(tab[index]), evolution[index])

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
	topics = {}

	while(1):
		my_counter(topics)
		display_counter(topics)
		delete_topics(topics)
		time.sleep(STANDARD_DELAY)

main()
f.close()
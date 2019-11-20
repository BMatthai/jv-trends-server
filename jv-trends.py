from urllib.request import urlopen
import bs4 as BeautifulSoup

import re
from datetime import datetime
import time

STANDARD_DELAY = 10
STANDARD_DELETATION = 3600


def heure():
	return datetime.now()

def my_write(str):
	f.write(str)
	print(str)

def display_sorted(interval, evolution_time):
	if (evolution_time == {}):
		return
	my_write("----------------------")
	my_write(heure() + "Topic les plus actifs sur les " + interval + " dernières minutes:")
	sorted_list = sorted(evolution_time.items(), key = lambda kv:(kv[1]))
	sorted_list = sorted_list[:5]
	for i in sorted_list:
		my_write(i)

def delete_topic(topic):
	last = len(topic[1]) - 1
	now = datetime.timestamp(datetime.now())
	tile = topic[0]
	if (now - topic[1][last][0] > STANDARD_DELETATION):
		del topics[title]
		print("Topic supprimé : " + title)

def display_counter(topics):
	evolution_thirty_minutes = {}

	for topic in topics.items():
		delete_topic(topic)
		size = len(topic[1])
		last = size - 1

		new_count = topic[1][last][1]

		title = topic[0]

		if (size > 6):
			thirty_count = new_count - topic[1][last - (6)][1]
			evolution_thirty_minutes[title] = thirty_count	

	display_sorted("30", evolution_thirty_minutes)

def my_counter(topics):
	html = urlopen('http://www.jeuxvideo.com/forums/0-51-0-1-0-1-0-blabla-18-25-ans.htm').read()

	soup = BeautifulSoup.BeautifulSoup(html, features="html.parser")

	page_topic_content = soup.find_all('ul', class_='topic-list topic-list-admin')

	nowa = datetime.now()
	now = datetime.timestamp(nowa)

	for i in range(1,26):
		raw_title = page_topic_content[0].find_all('span', class_="topic-subject")[i].text
		raw_count = page_topic_content[0].find_all('span', class_="topic-count")[i].text

		title = re.sub(r"^\s+|\s+$", "", raw_title)
		count = float(re.sub(r"^\s+|\s+$", "", raw_count)) + 1

		if (title in topics):
			topics[title].append((now,count))		
		else:
			topics[title] = [(now,count)]


f = open("topic_file.txt", "a")

def main():
	topics = {}
	
	while(1):
		my_counter(topics)
		display_counter(topics)
		time.sleep(STANDARD_DELAY)

main()
f.close()	


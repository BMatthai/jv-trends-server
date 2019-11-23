from urllib.request import urlopen
import bs4 as BeautifulSoup

import re
from datetime import datetime
import time

STANDARD_DELAY = 60
STANDARD_DELETION = 1200

def heure():
	return str(datetime.now())

def my_write(file, string):
	file.write(string)
	print(string)

def display_sorted(file, interval, evolution_time):
	my_write(file, str(evolution_time))
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
	remove = [topic for topic in topics.items() if now - topic[1][-1][0] > STANDARD_DELETION ]

	for to_remove in remove:
		del topics[to_remove[0]]
		print("Topic supprimé : " + to_remove[0])

def display_counter(topics):
	file = open("./topic_file.txt", "w")
	evolution_two_hours = {}
	evolution_hours = {}
	evolution_thirty_minutes = {}
	evolution_last = {}

	for topic in topics.items():
		size = len(topic[1])
		last = size - 1

		new_count = topic[1][last][1]

		title = topic[0]

		if (size > 240):
			two_hour_count = new_count - topic[1][last - (240)][1]
			evolution_two_hours[title] = two_hour_count

		if (size > 120):
			hour_count = new_count - topic[1][last - (120)][1]
			evolution_hours[title] = hour_count

		if (size > 60):
			thirty_count = new_count - topic[1][last - (60)][1]
			evolution_thirty_minutes[title] = thirty_count

		if (size > 10):
			last_count = new_count - topic[1][last - 10][1]
			evolution_last[title] = last_count

	display_sorted(file, "240", evolution_two_hours)
	display_sorted(file, "120", evolution_hours)
	display_sorted(file, "60", evolution_thirty_minutes)
	display_sorted(file, "10", evolution_last)

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

def main():
	topics = {}

	while(1):
		my_counter(topics)
		display_counter(topics)
		delete_topics(topics)
		time.sleep(STANDARD_DELAY)

main()
f.close()
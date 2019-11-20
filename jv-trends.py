from urllib.request import urlopen
import bs4 as BeautifulSoup

import re
from datetime import datetime
import time


def display_sorted(interval, evolution_time):
	if (evolution_time == {}):
		return
	print("----------------------")
	print("Topic les plus actifs sur les " + interval + " dernières minutes:")
	sorted_list = sorted(evolution_time.items(), key = lambda kv:(kv[1]))
	sorted_list = sorted_list[:5] 
	for i in sorted_list:
		print(i)

def display_counter(compteur):
	evolution_two_hours = {}
	evolution_hours = {}
	evolution_thirty_minutes = {}
	evolution_last = {}

	for key in compteur:
		size = len(compteur[key])
		last = size - 1

		new_count = compteur[key][last][1]

		if (size >= 24):
			two_hour_count = new_count - compteur[key][last - (24)][1]
			evolution_two_hours[key] = two_hour_count

		if (size > 12):
			hour_count = new_count - compteur[key][last - (12)][1]
			evolution_hours[key] = hour_count

		if (size > 6):
			thirty_count = new_count - compteur[key][last - (6)][1]
			evolution_thirty_minutes[key] = thirty_count	

		if (size > 3):
			last_count = new_count - compteur[key][last - 1][1]
			evolution_last[key] = last_count

	display_sorted("1", evolution_last)
	display_sorted("30", evolution_thirty_minutes)
	display_sorted("60", evolution_hours)
	display_sorted("120", evolution_two_hours)
		
def my_counter(compteur):
	html = urlopen('http://www.jeuxvideo.com/forums/0-51-0-1-0-1-0-blabla-18-25-ans.htm').read()

	soup = BeautifulSoup.BeautifulSoup(html, features="html.parser")

	topics = soup.find_all('ul', class_='topic-list topic-list-admin')

	nowa = datetime.now()
	now = datetime.timestamp(nowa)

	for i in range(1,26):
		raw_title = topics[0].find_all('span', class_="topic-subject")[i].text
		raw_count = topics[0].find_all('span', class_="topic-count")[i].text

		title = re.sub(r"^\s+|\s+$", "", raw_title)
		count = float(re.sub(r"^\s+|\s+$", "", raw_count)) + 1

		if (title in compteur):
			compteur[title].append((now,count))
					
		else:
			compteur[title] = [(now,count)]

def main():
	compteur = {}

	while(1):
		my_counter(compteur)
		display_counter(compteur)
		time.sleep(300)

main()
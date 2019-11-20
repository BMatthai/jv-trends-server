from urllib.request import urlopen
import bs4 as BeautifulSoup

import re
from datetime import datetime
import time


def my_counter(compteur):
	html = urlopen('http://www.jeuxvideo.com/forums/0-51-0-1-0-1-0-blabla-18-25-ans.htm').read()

	soup = BeautifulSoup.BeautifulSoup(html, features="html.parser")

	topics = soup.find_all('ul', class_='topic-list topic-list-admin')

	nowa = datetime.now()
	now = datetime.timestamp(nowa)

	evolution = []
	for i in range(1,26):
		raw_title = topics[0].find_all('span', class_="topic-subject")[i].text
		raw_count = topics[0].find_all('span', class_="topic-count")[i].text

		title = re.sub(r"^\s+|\s+$", "", raw_title)
		count = float(re.sub(r"^\s+|\s+$", "", raw_count)) + 1

		if (title in compteur):
			compteur[title].append((now,count))
			size = len(compteur[title])
			old_count = compteur[title][size - 2][1]
			new_count = count
			# new_count = compteur[title][size][1]
			evolution_value = (((new_count - old_count) / old_count) * 100)
			print("%d -> %d (+%f)" % (old_count, new_count, evolution_value))
			evolution.append((evolution_value, title))
		else:
			compteur[title] = [(now,count)]
			print(now)

	evolution.sort()
	print(evolution)


compteur = {}
# now = datetime.now().time()
while(1):
	my_counter(compteur)
	time.sleep(60)
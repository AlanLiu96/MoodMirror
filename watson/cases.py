'''
Given a CSV file of links, runs tone analysis and ports the results to a new CSV

NB: some cases do not match the regex, only one main person + possibly one contributor is allowed
	Ex: this dissent: https://www.law.cornell.edu/supremecourt/text/9-11121/#writing-9-11121.ZD

Check against demo: https://tone-analyzer-demo.mybluemix.net/?cm_mc_uid=75326432702014806613455&cm_mc_sid_50200000=1481858201
'''

import bs4, csv, json, re, requests, urllib
from watson_developer_cloud import ToneAnalyzerV3
from bs4 import BeautifulSoup


# Setup IBM Watson APIs
creds = {
  "url": "https://gateway.watsonplatform.net/tone-analyzer/api",
  "password": "hbbozehNfKLM",
  "username": "1424013d-badb-4bea-9e71-da73a2ffa5ed"
}

tone_analyzer = ToneAnalyzerV3(
   username=creds["username"],
   password=creds["password"],
   version='2016-05-19')

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title', 'meta']:
        return False
    elif isinstance(element, bs4.element.Comment):
        return False
    return True

# Loop through cases.csv and run analysis on every link, print result to data.csv
with open('cases3.csv', 'r') as oldcsv, open('data.csv', 'a') as newcsv:
	links = csv.reader(oldcsv)
	data = csv.writer(newcsv)
	
	counter = 0
	for row in links:
		# copy header row
		counter += 1
		if counter < 3225:
			#data.writerow(row)
			continue

		# extract get info from csv
		justice = row[0]
		url = row[1]
		caseType = row[2]

		# turn page into beautiful soup for parsing
		html = urllib.urlopen(url).read()
		soup = BeautifulSoup(html)
		texts = soup.find_all(text=True)
		visible_texts = filter(visible, texts)		

		# set regex pattern for isolating caseType segment we're looking for
		pattern = ""	
		if caseType == "opinion":
			pattern = "justice " + justice + "(?:\s)?delivered the opinion of the court"
		elif caseType == "concurrence":
			pattern = "justice " + justice + "(?:\s)?, (with whom justice [a-z]+ joins, )?concurring"
		elif caseType == "dissent":
			pattern = "justice " + justice + "(?:\s)?, (with whom (the chief )?justice ([a-z]+)? joins, )?dissenting"
		else:
			#caseType == "dissent in part, concur in part":
			pattern = "this justice dissents in part and concurs in part no matches"

		# break into lines and remove leading and trailing space on each
		lines = (line.strip() for line in visible_texts)
		# break multi-headlines into a line each
		chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
		# get segment we want
		start = False
		stop = False
		segment = []
		prevchunk = ""
		for chunk in chunks:
			if chunk:
				if start:
					if chunk == "TOP":
						stop = True
					else:
						segment.append(chunk)
				if re.search(pattern, prevchunk + chunk, re.IGNORECASE):
					start = True
				if stop:
					break
				prevchunk = chunk
		text = ' '.join(segment)

		case = text.encode('utf-8') 

		# If case contains text, do text analysis
		if case:
			print str(counter) + ": analysis"
			# run through analysis
			try:
				result = tone_analyzer.tone(text=case)
			except:
				data.writerow(row)
				continue

			emotion_tone = result["document_tone"]["tone_categories"][0]["tones"]
			language_tone = result["document_tone"]["tone_categories"][1]["tones"]
			social_tone = result["document_tone"]["tone_categories"][2]["tones"]

			anger = emotion_tone[0]["score"]
			disgust = emotion_tone[1]["score"]
			fear = emotion_tone[2]["score"]
			joy = emotion_tone[3]["score"]
			sadness = emotion_tone[4]["score"]

			analytical = language_tone[0]["score"]
			confident = language_tone[1]["score"]
			tentative = language_tone[2]["score"]

			openness = social_tone[0]["score"]
			conscientiousness = social_tone[1]["score"]
			extraversion = social_tone[2]["score"]
			agreeableness = social_tone[3]["score"]
			emotional_range = social_tone[4]["score"]

			# write results to file
			newlist = ' '.join(row).strip().split(' ') + [anger, disgust, fear, joy, sadness, analytical, confident, tentative, openness, conscientiousness, extraversion, agreeableness, emotional_range]
			data.writerow(newlist)

		else:
			print str(counter) + ": empty"
			# it's empty, keep it that way
			data.writerow(row)

		# debug break after first few
		# if counter == 5:
		# 	break


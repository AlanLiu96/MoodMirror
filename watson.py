from watson_developer_cloud import ToneAnalyzerV3

# Setup IBM Watson APIs
creds = {
  "url": "https://gateway.watsonplatform.net/tone-analyzer/api",
  "username": "58471750-236c-4103-85ea-15ef328025e6",
  "password": "nzBOc8Zk02LR"
}

tone_analyzer = ToneAnalyzerV3(
   username=creds["username"],
   password=creds["password"],
   version='2016-05-19')

def send_watson(sentence):
	try:
		result = tone_analyzer.tone(text=sentence)
	except:
		raise Exception(" Wasn't able to analyze! :( ")

	ret = {}

	emotion_tone = result["document_tone"]["tone_categories"][0]["tones"]
	# language_tone = result["document_tone"]["tone_categories"][1]["tones"]
	# social_tone = result["document_tone"]["tone_categories"][2]["tones"]

	for emo in emotion_tone:
		print "here! :)"
		ret[emo["tone_id"]]=emo["score"]

	# anger = emotion_tone[0]["score"]
	# disgust = emotion_tone[1]["score"]
	# fear = emotion_tone[2]["score"]
	# joy = emotion_tone[3]["score"]
	# sadness = emotion_tone[4]["score"]

	# analytical = language_tone[0]["score"]
	# confident = language_tone[1]["score"]
	# tentative = language_tone[2]["score"]

	# openness = social_tone[0]["score"]
	# conscientiousness = social_tone[1]["score"]
	# extraversion = social_tone[2]["score"]
	# agreeableness = social_tone[3]["score"]
	# emotional_range = social_tone[4]["score"]

	return ret
	# # write results to file
	# newlist = ' '.join(row).strip().split(' ') + [anger, disgust, fear, joy, sadness, analytical, confident, tentative, openness, conscientiousness, extraversion, agreeableness, emotional_range]
	# data.writerow(newlist)
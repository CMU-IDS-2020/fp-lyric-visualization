# Name of File: dictionary_preprocess.py
# Date: November 14th, 2020
# Purpose of File: to create a Panda dataframe called dict_dataframe that uses the lyrics dataframe from
#                  lyrics_preprocess.py, makes a dictionary of the words with their word counts, and
#                  looks up different dimensions of the words using the tools below
# Tools used:
# TextBlob (see https://textblob.readthedocs.io/en/dev/)
# HuggingFace Library (https://huggingface.co/transformers/quicktour.html)
# Merriam-Webster (https://dictionaryapi.com/)
import numpy as np
import pandas as pd
from enum import Enum
from textblob import TextBlob
from transformers import pipeline
import urllib.request as ur
import json

# Used for the HuggingFace Library (see https://huggingface.co/transformers/quicktour.html)
# This sentiment-analysis classifier "uses the DistilBERT architecture and has been 
# fine-tuned on a dataset called SST-2 for the sentiment analysis task."
# model_name = "distilbert-base-uncased-finetuned-sst-2-english"
hugface_classifier = pipeline('sentiment-analysis')

# Used for the Merriam-Webster Dictionary API
# keys are obfuscated here because they are associated with an account
# CAUTION: insert own keys for dict_key and thes_key
dict_url = "https://dictionaryapi.com/api/v3/references/collegiate/json/"
dict_key = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
thes_url = "https://dictionaryapi.com/api/v3/references/thesaurus/json/"
thes_key = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

class Lyrics_Columns(Enum):
 	WORD_ORIGINAL = 1
 	WORD_NO_PUNCTUATION = 2
 	WORD_CAN_SEARCH = 3
 	WORD_INDEX_IN_SONG = 4
 	LINE_INDEX_IN_SONG = 5
 	STANZA_INDEX_IN_SONG = 6
 	STANZA_DESCRIPTION = 7
 	LINE_INDEX_IN_STANZA = 8
 	WORD_INDEX_IN_LINE = 9

# The artist and song that will be preprocessed
artist_name = "Will Smith"
song_name = "Just the Two of Us"

# Read in the lyrics dataframe
lyrics_df = pd.read_csv(artist_name + " " + song_name + " lyrics.csv")

# Make four dictionaries of the words that are in the song, all indexed by word (equivalent of word_can_search)
# 1. Count of all appearances of the word (including all choruses)
all_chorus_count = {}
# 2. Count of all appearances of the word (including only the first chorus)
first_chorus_count = {}
# 3. Count of all appearances of the word (not including any of the choruses)
no_chorus_count = {}
# 4. List of word_index_in_song values for all the appearances of the word
word_indexes = {}
past_first_chorus = False
for index, row in lyrics_df.iterrows():
	# for readability, get row values ahead
	word = row[Lyrics_Columns.WORD_CAN_SEARCH.value]
	word_index_in_song = row[Lyrics_Columns.WORD_INDEX_IN_SONG.value]
	stanza_description = row[Lyrics_Columns.STANZA_DESCRIPTION.value]
	# increment counts
	if (stanza_description == "Chorus") and not past_first_chorus:
		# the word is in the first chorus
		# increment the count_with_all_chorus and the count_with_first_chorus for this word
		all_chorus_count[word] = all_chorus_count.get(word, 0) + 1
		first_chorus_count[word] = first_chorus_count.get(word, 0) + 1
		# this is the first chorus, so change the value of past_first_chorus
		past_first_chorus = True
	elif (stanza_description == "Chorus"):
		# the word is in a chorus that is not the first chorus
		# increment the count_with_all_chorus for this word
		all_chorus_count[word] = all_chorus_count.get(word, 0) + 1
	else:
		# the word is not in chorus
		# increment the count_with_all_chorus, count_with_first_chorus, and count_with_no_chorus for this word
		all_chorus_count[word] = all_chorus_count.get(word, 0) + 1
		first_chorus_count[word] = first_chorus_count.get(word, 0) + 1
		no_chorus_count[word] = no_chorus_count.get(word, 0) + 1
	# add this word's index to the word_indexes dictionary
	word_indexes.setdefault(word, []).append(word_index_in_song)

# Open the broad_part_of_speech panda dataframe
part_of_speech_df = pd.read_csv("broad_parts_of_speech_key.csv")
# Make a dictionary where the key is the specific part of speech and the value is the broad part of speech
part_of_speech_dict = {}
for index, row in part_of_speech_df.iterrows():
	# example: broad_pos = ["N"], specific_pos = ["NN", "NNS", "NNP", "NNPS"]
	broad_pos = row["abbreviation"]
	specific_pos = row["specific_pos"].strip('][').split(', ')
	for element in specific_pos:
		part_of_speech_dict[element[1:-1]] = broad_pos

# Make a dictionary Panda dataframe from the above dictionaries
dict_columns = ["word_can_search", "count_with_all_chorus", "count_with_first_chorus", "count_with_no_chorus", "list_of_indexes", 
					"textblob_pos_tags", "broad_pos_tag", "hugface_label", "hugface_score"]
dict_df = pd.DataFrame(columns = dict_columns)
for word in word_indexes.keys():
	# Use the TextBlob Library for each word
	# Descriptions from https://textblob.readthedocs.io/en/dev/_modules/textblob/blob.html#BaseBlob.classify
	# polarity(self): return the polarity score as a float within the range [-1.0, 1.0]
	# subjectivity(self): return the subjectivity score as a float within the range [0.0, 1.0] where 0.0 is very objective and 1.0 is very subjective
	# CAUTION: a lot of the words do not have values for these above because the dictionary that sentiment is being taken from is not that large
	# 			(see issue here: https://stackoverflow.com/questions/62117003/textblob-0-values-for-polarity-and-subjectivity)
	# pos_tags(self): returns an list of tuples of the form (word, POS tag) - example: [('At', 'IN'), ('eight', 'CD'), ("o'clock", 'JJ'), ('on', 'IN')]
	#                 default uses NLTK’s standard TreeBank tagger (https://textblob.readthedocs.io/en/dev/api_reference.html#textblob.en.taggers.NLTKTagger)
	# 				  this is NLTK's description: https://www.nltk.org/_modules/nltk/test/unit/test_pos_tag.html#TestPosTag.test_pos_tag_eng
	# 				  CAUTION: in their example here, something like "John's" is split into [('John', 'NNP'), ("'s", 'POS')]
	# 				  what the abbreviations mean: https://pythonprogramming.net/natural-language-toolkit-nltk-part-speech-tagging/
	textblob = TextBlob(word)
	# remove these (see CAUTION above)
	# textblob_polarity = textblob.polarity
	# textblob_subjectivity = textblob.subjectivity
	textblob_pos_tags = textblob.pos_tags

	broad_pos_tag = ""
	if (len(textblob_pos_tags) == 0):
		print("error: no classification for word = ", word)
		broad_pos_tag = "ERR"
	elif(len(textblob_pos_tags) == 1):
		broad_pos_tag = part_of_speech_dict[textblob_pos_tags[0][1]]
	else:
		print("error: more than two classifications for word = ", word, ", pos = ", textblob_pos_tags)
		broad_pos_tag = "MULT"
	
	# Use the Huggingface Library for each word
	hugface_sentiment = hugface_classifier(word)
	hugface_label = hugface_sentiment[0]["label"]
	hugface_score = round(hugface_sentiment[0]["score"], 4)

	# Add the new column to the dictionary dataframe
	word_df = pd.DataFrame([[word, all_chorus_count.get(word, 0), first_chorus_count.get(word, 0), no_chorus_count.get(word, 0), word_indexes.get(word), 
								textblob_pos_tags, broad_pos_tag, hugface_label, hugface_score]], columns = dict_columns)
	dict_df = dict_df.append(word_df, ignore_index = True)

# Save this dataframe as a .csv file
dict_df.to_csv(artist_name + " " + song_name + " dictionary.csv")

# For each word in the word_indexes list, save the word's thesaurus and dictionary merriam-webster responses to a json file
# COMMENTED OUT FOR NOW SO THAT IT IS NOT RUN ACCIDENTALLY
'''
for word in word_indexes.keys():
	# Use the Merriam-Webster Dictionary API for each word
	# CAUTION (for when design app) from website: "All applications using Merriam-Webster APIs must feature the Merriam-Webster logo. 
	# 				Please refer to our Brand Guidelines for directions on the use of our logo, brand name, and product names."
	# Write the word's data out to a dictionary and thesaurus file for easy access later if desired
	dict_file = open(word + "_m_w_dict.json", "w")
	json_dict_url = ur.urlopen(dict_url + word + "?key=" + dict_key)
	dict_data = json.loads(json_dict_url.read())
	dict_file.write(json.dumps(dict_data))
	dict_file.close()

	thes_file = open(word + "_m_w_thes.json", "w")
	json_thes_url = ur.urlopen(thes_url + word + "?key=" + thes_key)
	thes_data = json.loads(json_thes_url.read())
	thes_file.write(json.dumps(thes_data))
	thes_file.close()

	# TODO: need to look at the fields offered by dictionary and thesaurus and make another program to parse the ones we want from the json files
	# Offhand (from browsing https://dictionaryapi.com/products/json) I think the most interesting ones are:
	# STEM METADATA: "lists all of the entry's headwords, variants, inflections, undefined entry words, and defined run-on phrases. 
	#					Each stem string is a valid search term that should match this entry."
	# SUBJECT/STATUS LABELS: SLS "A subject/status label describes the subject area (eg, "computing") or regional/usage status (eg, "British", "formal", "slang")"
	# ETYMOLOGY: ET "An etymology is an explanation of the historical origin of a word."
	# FIRST KNOWN USE: DATE "The date of the earliest recorded use of a headword in English is captured in date."
	# SYNONYMS SECTION: SYNS "Extensive discussions of synonyms for the headword"
	# SYNONYM AND NEAR SYNONYM LISTS: SIM_LIST "A thesaurus entry may contain a list of synonyms and near synonyms for the headword. 
	#											A list of all similar words (synonyms and near synonyms) is contained in a sim_list."
	# ANTONYM LISTS: ANT_LIST "A thesaurus entry may contain a list of antonyms of the headword."
	# NEAR ANTONYM LISTS: NEAR_LIST "A thesaurus entry may contain a list of near antonyms of the headword."
	# ANTONYM AND NEAR ANTONYM LISTS: OPP_LIST "A thesaurus entry may contain a list of antonyms and near antonyms of the headword. 
	# 											A list of all opposite words (antonyms and near antonyms) is contained in an opp_list."
'''

# IDEA FOR LATER:
# If we expand this to a general-purpose interactive visualization (can enter many songs)
# We could use this library for parsing, including removing punctuation and correcting the spelling of words so that they are searchable

# IDEA FOR LATER:
# Pass lines into textblob (getting the polarity and subjectivity) to see if there are clear differences between lines
# Also do with the huggingface library [it's interesting that there are so many super postive and super negative labeled words]

# IDEA FOR LATER:
# Use TextBlob to get the similarity of every pair of words:
# Example from here: https://textblob.readthedocs.io/en/dev/quickstart.html#quickstart
# Guidance: 
# "You can also create synsets directly.
# from textblob.wordnet import Synset
# octopus = Synset('octopus.n.02')
# shrimp = Synset('shrimp.n.03')
# octopus.path_similarity(shrimp)
# 0.1111111111111111
# Name of File: synonyms_preprocess.py
# Date: November 29th, 2020
# Purpose of File: to create Panda dataframes called syn_dataframe that reads the 
#                  definition, as well as synonyms and and antonyms from each word's
#                  json file
# Tools used:
# Merriam-Webster (https://dictionaryapi.com/) - previously used to make the json files
import numpy as np
import pandas as pd
import json

# The artist and song that will be preprocessed
artist_name = "Will Smith"
song_name = "Just the Two of Us"

# Read in the dictionary of words associated with this song (each should have a json file)
dict_df = pd.read_csv(artist_name + " " + song_name + " dictionary.csv")

# This will be the new dataframe made specifically to keep the synonym/antonym information
syns_plus_columns = ["word_can_search", "m_w_definition", "m_w_synonyms", "m_w_synonyms_in_data", "m_w_antonyms", "m_w_antonyms_in_data"]
syns_plus_df = pd.DataFrame(columns = syns_plus_columns)

# Go through the dictionary dataframe and make a dictionary of all of the 
WORD_CAN_SEARCH_INDEX = 1;
word_list = []
for index, row in dict_df.iterrows():
	word = row[WORD_CAN_SEARCH_INDEX]
	word_list.append(word)
word_set = set(word_list)

# Go through the dictionary dataframe and get the definition, synonyms, and antonyms for each word
WORD_CAN_SEARCH_INDEX = 1;
for index, row in dict_df.iterrows():
	word = row[WORD_CAN_SEARCH_INDEX]

	# Checking the dictionary
	definition = []
	dict_file = open("Merriam-Webster Data " + artist_name + " " + song_name + "/" + word + "_m_w_dict.json", "r")
	word_dict_json = json.load(dict_file)
	if len(word_dict_json) != 0:
		word_dict = word_dict_json[0]
		if "shortdef" in word_dict:
			definition = word_dict["shortdef"]
		else:
			if "def" not in word_dict:
				print("word = ", word, "has no definition or short definition")
			else:
				print("word = ", word, "has a definition, but no short definition")
	else:
		print("word = ", word, "has no dictionary entry")
	dict_file.close()

	# Checking the thesaurus
	synonyms = []
	antonyms = []
	thes_file = open("Merriam-Webster Data " + artist_name + " " + song_name + "/" + word + "_m_w_thes.json", "r")
	word_thes_json = json.load(thes_file)
	if len(word_thes_json) != 0:
		word_thes = word_thes_json[0]
		if "meta" in word_thes:
			# Check for synonyms
			if "syns" in word_thes["meta"]:
				synonyms = word_thes["meta"]["syns"]
			else:
				print("word = ", word, "has no synonyms")
			# Check for antonyms
			if "ants" in word_thes["meta"]:
				antonyms = word_thes["meta"]["ants"]
			else:
				print("word = ", word, "has no antonyms")

		else:
			print("word = ", word, "has no thesaurus entry (no 'meta' section)")
	else:
		print("word = ", word, "has no thesaurus entry")
	thes_file.close()

	# For each of the synonyms and antonyms, check if they are in the song
	synonyms_in_data_dict = {}
	antonyms_in_data_dict = {}
	if len(synonyms) != 0:
		for sublist in synonyms:
			for syn in sublist:
				if syn in word_set:
					if syn not in synonyms_in_data_dict:
						synonyms_in_data_dict[syn] = 1
	if len(antonyms) != 0:
		for sublist in antonyms:
			for ant in sublist:
				if ant in word_set:
					if ant not in antonyms_in_data_dict:
						antonyms_in_data_dict[ant] = 1
	synonyms_in_data = list(synonyms_in_data_dict.keys())
	antonyms_in_data = list(antonyms_in_data_dict.keys())

	row_df = pd.DataFrame([[word, definition, synonyms, synonyms_in_data, antonyms, antonyms_in_data]], columns = syns_plus_columns)
	syns_plus_df = syns_plus_df.append(row_df, ignore_index = True)

# Save this dataframe as a .csv file
syns_plus_df.to_csv(artist_name + " " + song_name + " synonyms_and_more.csv")
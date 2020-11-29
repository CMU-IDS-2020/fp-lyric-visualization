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
syn_columns = ["word_can_search", "definition", "synonyms", "antonyms"]
syn_df = pd.DataFrame(columns = syn_columns)

# Go through the dictionary dataframe and get the definition, synonyms, and antonyms for each word
# WORD_CAN_SEARCH_INDEX = 1;
# for index, row in dict_df.iterrows():
#	word = row[WORD_CAN_SEARCH_INDEX]
	# print("word = ", word)
	
word = "now"
dict_file = open("Merriam-Webster Data " + artist_name + " " + song_name + "/" + word + "_m_w_dict.json", "r")
word_dict_df = pd.read_json(dict_file.read(), lines = True)
dict_file.close()
word_dict_df.to_csv("now_synonyms_test_dict.csv")
thes_file = open("Merriam-Webster Data " + artist_name + " " + song_name + "/" + word + "_m_w_thes.json", "r")
thes_dict_df = pd.read_json(thes_file.read(), lines = True)
thes_dict_df.to_csv("now_synonyms_test_thes.csv")
thes_file.close()
print(thes_dict_df)
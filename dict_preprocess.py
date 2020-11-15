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

# Make a dictionary Panda dataframe from the above dictionaries
dict_columns = ["word_can_search", "count_with_all_chorus", "count_with_first_chorus", "count_with_no_chorus", "list_of_indexes"]
dict_df = pd.DataFrame(columns = dict_columns)
for word in word_indexes.keys():
	word_df = pd.DataFrame([[word, all_chorus_count.get(word, 0), first_chorus_count.get(word, 0), 
								no_chorus_count.get(word, 0), word_indexes.get(word)]], columns = dict_columns)
	dict_df = dict_df.append(word_df, ignore_index = True)

# Use the TextBlob Library for each word
# Add the results to the dictionary Panda Dataframe

# Use the Huggingface Library for each word
# Add the results to the dictionary Panda Dataframe

# Use the Merriam-Webster Dictionary API for each word
# Add the results to the dictionary Panda Dataframe
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

# Make a dictionary Panda dataframe of the words that are in the song
# With the count of how many times the word appears in the song
# And the word indexes from the beginning
# (including all the chorus duplicates and also not including the chorus duplicates)
dict_df = pd.DataFrame(columns = ["word_can_search", "count_all", "count_with_first_chorus", "count_with_no_chorus"])
for index, row in lyrics_df.iterrows():
	if (row[Lyrics_Columns.STANZA_DESCRIPTION.value] == "Chorus"):
		print(row)
		print("=======")

# Use the TextBlob Library for each word
# Add the results to the dictionary Panda Dataframe

# Use the Huggingface Library for each word
# Add the results to the dictionary Panda Dataframe

# Use the Merriam-Webster Dictionary API for each word
# Add the results to the dictionary Panda Dataframe
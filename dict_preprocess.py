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

# Used for the HuggingFace Library (see https://huggingface.co/transformers/quicktour.html)
# This sentiment-analysis classifier "uses the DistilBERT architecture and has been 
# fine-tuned on a dataset called SST-2 for the sentiment analysis task."
# model_name = "distilbert-base-uncased-finetuned-sst-2-english"
hugface_classifier = pipeline('sentiment-analysis')

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
dict_columns = ["word_can_search", "count_with_all_chorus", "count_with_first_chorus", "count_with_no_chorus", "list_of_indexes", 
					"textblob_polarity", "textblob_subjectivity", "textblob_pos_tags",
					"hugface_label", "hugface_score"]
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
	textblob_polarity = textblob.polarity
	textblob_subjectivity = textblob.subjectivity
	textblob_pos_tags = textblob.pos_tags
	
	# Use the Huggingface Library for each word
	hugface_sentiment = hugface_classifier(word)
	hugface_label = hugface_sentiment[0]["label"]
	hugface_score = round(hugface_sentiment[0]["score"], 4)

	# Use the Merriam-Webster Dictionary API for each word

	# add the new column to the dictionary dataframe
	word_df = pd.DataFrame([[word, all_chorus_count.get(word, 0), first_chorus_count.get(word, 0), no_chorus_count.get(word, 0), word_indexes.get(word), 
								textblob_polarity, textblob_subjectivity, textblob_pos_tags, hugface_label, hugface_score]], columns = dict_columns)
	dict_df = dict_df.append(word_df, ignore_index = True)

# Save this dataframe as a .csv file
dict_df.to_csv(artist_name + " " + song_name + " dictionary.csv")

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

# Name of File: lyrics_preprocess.py
# Date: November 14th, 2020
# Purpose of File: to create a Panda dataframe called lyrics_dataframe of words by their location in a song
# Tools used:
# LyricsGenius (see https://pypi.org/project/lyricsgenius/)
# HuggingFace Library (https://huggingface.co/transformers/quicktour.html)
import numpy as np
import pandas as pd
import os
from transformers import pipeline

def preprocess_lyrics(artist_name, song_name):
	# Used to get the lyrics for all songs from an artist
	# (automatically saved to a JSON file)
	# this gets a lot of information that is not needed
	# the lyrics for each song are with the field "lyrics"
	# artist = genius.search_artist(artist_name)
	# artist.save_lyrics()

	lyrics = ''
	# Use the Genius API to get the lyrics
	import lyricsgenius
	genius = lyricsgenius.Genius("tub_dvzlNtK1D1lLS7o4YUqX2fGBnJdAVbW_OgjEjRKtfhyUopjvonY50UzhPlKe")
	song = genius.search_song(song_name, artist_name)
	lyrics = song.lyrics


	# For testing/debugging purposes, use the plaintext copy of the lyrics
	# FOR TEST/DEBUG
	# file = open(artist_name + " " + song_name + " lyrics.txt", "r")

	# Split the lyrics up into individual words (ignore punctuation)
	# Keep track of the Stanza and Speaker
	# (directly copying what is inside [] brackets)
	# Assign an index for each Stanza/Speaker pair
	# For now, duplicates of the chorus are kept (no deduplication)
	# Assign line and word indexes, in two ways
	# 1. Line index within a stanza and word index within a line (start at 1)
	# 2. Line index from the beginning and word index from the beginning (start at 1)
	# The stanza in song starts at 0 because it will be immediately incremented and therefore
	# actually start at 1 in the numbering
	stanza_in_song = 0
	stanza_description = ""
	line_in_song = 1
	line_in_stanza = 1
	word_in_song = 1
	word_in_line = 1

	lyrics_columns = ["word_original", "word_no_punctuation", "word_can_search", "word_index_in_song",
		"line_index_in_song", "stanza_index_in_song", "stanza_description", "line_index_in_stanza", "word_index_in_line"]
	lyrics_df = pd.DataFrame(columns = lyrics_columns)

	lines_columns = ["line_original", "line_index_in_song", "line_classified", "line_label", "line_score"]
	lines_df = pd.DataFrame(columns = lines_columns)

	# Used for the HuggingFace Library (see https://huggingface.co/transformers/quicktour.html)
	# This sentiment-analysis classifier "uses the DistilBERT architecture and has been
	# fine-tuned on a dataset called SST-2 for the sentiment analysis task."
	# model_name = "distilbert-base-uncased-finetuned-sst-2-english"
	hugface_classifier = pipeline('sentiment-analysis')

	# Add the words to a lyrics Panda dataframe with their indexes
	# only needed for when reading from the genius lyrics
	# lines = lyrics.split("\n")
	# for line in lines:
	# FOR TEST/DEBUG
	for line in lyrics.split("\n"):
		# FOR TEST/DEBUG
		# take off the "\n" at the end of the line
		line = line.rstrip()
		# if the line is not empty
		if line.strip():
			# if the line is a stanza header because it is inside brackets []
			# then start a new stanza index-numbering-wise
			if (line[0] == "[") and (line[-1] == "]"):
				stanza_in_song = stanza_in_song + 1
				stanza_description = line[1:-1]
				line_in_stanza = 1
				word_in_line = 1
			# otherwise, process all of the words in the line
			else:
				words = line.split(" ")
				new_line = ""
				for word in words:
					word = word.encode().decode() # UTF-8 encoding
					if len(word) == 0:
						continue
					# remove any punctuation that might have come with the word
					# and save the word and its location data as a row in the dataframe
					# NOTE: the lowercase version of the word is saved as "word_can_search"
					#       so that if words used as labels in a tooltip/hover on a chart
					#         all the words will all be lowercase (with the exception of 'I',
					#         I'd, I'm, ...)
					# There is one place where a hyphen is used (-) between two words
					# in the phrase "See me-I'm tyin to pretend I know" it should be split
					# into two words
					if (word == "me-I'm"):
						# Save the first word as a new row to the dataframe
						# (changed original punctuation so that the "original words" can be printed easily from this dataframe)
						first_word_df = pd.DataFrame([["me-", "me", "me", word_in_song,
							line_in_song, stanza_in_song, stanza_description, line_in_stanza, word_in_line]], columns = lyrics_columns)
						lyrics_df = lyrics_df.append(first_word_df, ignore_index = True)

						# add the word to the line that will be classified
						new_line = new_line + " " + "me"

						# increment the word indexes
						word_in_song = word_in_song + 1
						word_in_line = word_in_line + 1
						# save the second word as a new row to the dataframe
						second_word_df = pd.DataFrame([["I'm", "I'm", "I'm", word_in_song,
							line_in_song, stanza_in_song, stanza_description, line_in_stanza, word_in_line]], columns = lyrics_columns)
						lyrics_df = lyrics_df.append(second_word_df, ignore_index = True)

						# add the word to the line that will be classified
						new_line = new_line + " " + "I'm"
					else:
						# For "Just the two of us" the punctuations to remove are
						# (this is complicated by things like an' for and)
						# After the word: comma (,) question mark (?) and parenthesis ())
						# Before the word: parenthesis (()
						# More conditions are added to meet the needs of other songs
						# including special quote types: https://stackoverflow.com/questions/18735921/are-there-different-types-of-double-quotes-in-utf-8-php-str-replace#:~:text=Some%20rarer%20ones%20are%20FULLWIDTH,QUOTATION%20MARK%2C%20and%20so%20on.
						word_no_punctuation = word
						if len(word_no_punctuation) > 0:
							# punctuation after the word
							keep_going = True
							while (((word_no_punctuation[-1] == '''"''') or
								  (word_no_punctuation[-1] == ")") or
								  (word_no_punctuation[-1] == ",") or
								  (word_no_punctuation[-1] == "?") or
								  (word_no_punctuation[-1] == "!") or
								  (word_no_punctuation[-1] == "-") or
								  (word_no_punctuation[-1] == ".") or
								  (word_no_punctuation[-1] == """'""") or
							      (word_no_punctuation[-1] == '\u201D')) and keep_going):
								  # exclude the n' -> ng case
								  if (word_no_punctuation[-2:] != "n'"):
								  		word_no_punctuation = word_no_punctuation[0:-1]
								  else:
								  		keep_going = False
							# punctuation before the word
							keep_going = True
							while (((word_no_punctuation[0] == "(") or
								  (word_no_punctuation[0] == '''"''') or
								  (word_no_punctuation[0] == """'""") or
								  (word_no_punctuation[0] == '\u201C')) and keep_going):
								  # exclude the 'cause -> because case
								  if (word_no_punctuation != "'cause"):
								  		word_no_punctuation = word_no_punctuation[1:]
								  else:
								  		keep_going = False
						# Make most of the words lower-case except for words like "I" which are upper-case in English
						word_can_search = word_no_punctuation
						if (word_can_search != "I") and (word_can_search != "I'm") and (word_can_search != "I'd") and (word_can_search != "I'll"):
							word_can_search = word_can_search.lower()
						# Words that are changed so that they can be looked up:
						# gettin -> getting, ta -> to, cause -> because, bringin -> bringing
						# an' -> and, makin -> making, changin -> changing, tyin -> trying, nothin -> nothing
						if (word_can_search == "gettin"):
							word_can_search = "getting"
						elif (word_no_punctuation == "ta"):
							word_can_search = "to"
						elif (word_can_search == "cause"):
							word_can_search = "because"
						elif (word_can_search == "makin"):
							word_can_search = "making"
						elif (word_can_search == "changin"):
							word_can_search = "changing"
						elif (word_can_search == "tyin"):
							word_can_search = "trying"
						elif (word_can_search == "nothin"):
							word_can_search = "nothing"
						
						if (word_can_search[-2:] == "n'"):
							word_can_search = word_can_search[0:-1] + "g"
						
						if (word_can_search == "'cause"):
							word_can_search = "because"

						# save the word as a new row to the dataframe
						word_df = pd.DataFrame([[word, word_no_punctuation, word_can_search, word_in_song,
							line_in_song, stanza_in_song, stanza_description, line_in_stanza, word_in_line]], columns = lyrics_columns)
						lyrics_df = lyrics_df.append(word_df, ignore_index = True)

						# add the word to the line that will be classified
						new_line = new_line + " " + word_can_search
					#increment the word indexes
					word_in_song = word_in_song + 1
					word_in_line = word_in_line + 1

				# Use the Huggingface Library for each line
				hugface_sentiment = hugface_classifier(new_line)
				hugface_label = hugface_sentiment[0]["label"]
				hugface_score = round(hugface_sentiment[0]["score"], 4)
				# Save the result to the lines dataframe
				new_line_df = pd.DataFrame([[line, line_in_song, new_line, hugface_label, hugface_score]], columns = lines_columns)
				lines_df = lines_df.append(new_line_df, ignore_index = True)

				# increment the line indexes
				line_in_song = line_in_song + 1
				line_in_stanza = line_in_stanza + 1

	return lyrics_df, lines_df
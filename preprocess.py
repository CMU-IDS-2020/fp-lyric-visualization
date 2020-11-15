
# Name of File: preprocess.py
# Date: November 14th, 2020
# Purpose of File: to collect data about the words in a particular song from various sources
#                  and create two Panda dataframes: one that is by-location in the song (lyrics)
#                  and one that is by-word (dictionary)
# Tools used:
# LyricsGenius (see https://pypi.org/project/lyricsgenius/)
# TextBlob (see https://textblob.readthedocs.io/en/dev/)
# HuggingFace Library (https://huggingface.co/transformers/quicktour.html)
# Merriam-Webster (https://dictionaryapi.com/)
import lyricsgenius

# The artist and song that will be preprocessed
artist_name = "Will Smith"
song_name = "Just the Two of Us"

# Use the Genius API to get the lyrics
genius = lyricsgenius.Genius("tub_dvzlNtK1D1lLS7o4YUqX2fGBnJdAVbW_OgjEjRKtfhyUopjvonY50UzhPlKe")
song = genius.search_song(song_name, artist_name)
lyrics = song.lyrics

# Used to save the plaintext copy of the lyrics to a file (for easy perusal)
# file = open(artist_name + " " + song_name + " lyrics.txt", "w")
# file.write(lyrics)
# file.close()

# Used to get the lyrics for all songs from an artist
# (automatically saved to a JSON file)
# this gets a lot of information that is not needed
# the lyrics for each song are with the field "lyrics"
# artist = genius.search_artist(artist_name)
# artist.save_lyrics()

# Split the lyrics up into individual words (ignore punctuation)
# Keep track of the Stanza and Speaker
# (directly copying what is inside [] brackets)
# Assign an index for each Stanza/Speaker pair
# For now, duplicates of the chorus are kept (no deduplication)
# Assign line and word indexes, in two ways
# 1. Line index within a stanza and word index within a line
# 2. Line index from the beginning and word index from the beginning

# Add the words to a lyrics Panda dataframe with their indexes

# Also make a dictionary Panda dataframe of the words that are in the song
# With the count of how many times the word appears in the song
# And the word indexes from the beginning
# (including all the chorus duplicates and also not including the chorus duplicates)

# Use the TextBlob Library for each word
# Add the results to the dictionary Panda Dataframe

# Use the Huggingface Library for each word
# Add the results to the dictionary Panda Dataframe

# Use the Merriam-Webster Dictionary API for each word
# Add the results to the dictionary Panda Dataframe
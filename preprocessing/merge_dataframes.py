# Name of File: combine_dataframes.py
# Date: November 14th, 2020
# Purpose of File: to merge two Panda dataframes (here lyrics and dictionary)
import numpy as np
import pandas as pd

# The artist and song whose lyrics dataframe and dictionary dataframe will be merged
artist_name = "Will Smith"
song_name = "Just the Two of Us"

# Read in the lyrics dataframe
lyrics_df = pd.read_csv(artist_name + " " + song_name + " lyrics.csv")

# Read in the dictionary dataframe
dict_df = pd.read_csv(artist_name + " " + song_name + " dictionary.csv")

merged_df = lyrics_df.merge(dict_df, how="left", on = "word_can_search")

# Save this dataframe as a .csv file
merged_df.to_csv(artist_name + " " + song_name + " merged.csv")

# TODO: the above keeps the indices of the lyrics and dictionary dataframes
# calling them unnamed x and unnamed y ... not changing right now but could
# consider cleaning up later if we want
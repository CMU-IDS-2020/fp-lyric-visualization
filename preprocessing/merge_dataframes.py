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

# Read in the lines dataframe
lines_df = pd.read_csv(artist_name + " " + song_name + " lines.csv")

merged_df = lyrics_df.merge(dict_df, how="left", on = "word_can_search")

merged_df = merged_df.merge(lines_df, how="left", on = "line_index_in_song")

# drop the 'unnamed' columns
# help from https://stackoverflow.com/questions/43983622/remove-unnamed-columns-in-pandas-dataframe
merged_df.rename({"Unnamed: 0_x":"x"}, axis="columns", inplace=True)
merged_df.drop(["x"], axis=1, inplace=True)
merged_df.rename({"Unnamed: 0_y":"y"}, axis="columns", inplace=True)
merged_df.drop(["y"], axis=1, inplace=True)
merged_df.rename({"Unnamed: 0":"z"}, axis="columns", inplace=True)
merged_df.drop(["z"], axis=1, inplace=True)

# Save this dataframe as a .csv file
merged_df.to_csv(artist_name + " " + song_name + " merged.csv")

# TODO: the above keeps the indices of the lyrics and dictionary dataframes
# calling them unnamed x and unnamed y ... not changing right now but could
# consider cleaning up later if we want
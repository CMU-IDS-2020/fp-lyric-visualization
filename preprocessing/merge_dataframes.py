# Name of File: combine_dataframes.py
# Date: November 14th, 2020
# Purpose of File: to merge two Panda dataframes (here lyrics and dictionary)
import numpy as np
import pandas as pd

def merge_dataframes(lyrics_df, lines_df, dict_df):
    merged_df = lyrics_df.merge(dict_df, how="left", on = "word_can_search")

    # # Read in the synonyms dataframe
    # syns_df = pd.read_csv(artist_name + " " + song_name + " synonyms_and_more.csv")

    # merged_df = merged_df.merge(syns_df, how="left", on = "word_can_search")

    lyrics_df = merged_df.merge(lines_df, how="left", on = "line_index_in_song")

    from preprocessing.tsne import tsne_column, normalize_positivity

    # Normalize the positivity value from hugging face
    lyrics_df = normalize_positivity(lyrics_df)

    # Compute T-SNE dimensions
    lyrics_df['tsne_x'], lyrics_df['tsne_y'] = tsne_column(lyrics_df['word_can_search'])

    lines_df['tsne_x'], lines_df['tsne_y'] = tsne_column(lines_df['line_classified'])

    return lyrics_df, lines_df

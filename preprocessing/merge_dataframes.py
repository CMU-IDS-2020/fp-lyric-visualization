# Name of File: combine_dataframes.py
# Date: November 14th, 2020
# Purpose of File: to merge two Panda dataframes (here lyrics and dictionary)
import numpy as np
import pandas as pd

from preprocessing.tsne import normalize_positivity

def merge_dataframes(lyrics_df, lines_df, dict_df):
    merged_df = lyrics_df.merge(dict_df, how="left", on = "word_can_search")

    # # Read in the synonyms dataframe
    # syns_df = pd.read_csv(artist_name + " " + song_name + " synonyms_and_more.csv")

    # merged_df = merged_df.merge(syns_df, how="left", on = "word_can_search")

    lyrics_df = merged_df.merge(lines_df, how="left", on = "line_index_in_song")

    # Normalize the positivity value from hugging face
    lyrics_df = normalize_positivity(lyrics_df)

    # The following code computes t-sne on the words of each song indivitually, but we want tsne with the words
    # from both songs so we now compute it somewhere else
    # # Compute T-SNE dimensions
    # lyrics_df['tsne_x'], lyrics_df['tsne_y'] = tsne_column(lyrics_df['word_can_search'])
    # lines_df['tsne_x'], lines_df['tsne_y'] = tsne_column(lines_df['line_classified'])

    # Get the positive word in positive line .. etc. data
    lyrics_df['positivity_bar_chart'] = ''
    lyrics_df.loc[(lyrics_df['line_label'] == 'POSITIVE') & (lyrics_df['hugface_label'] == 'POSITIVE'), 'positivity_bar_chart'] = 'pos_word_pos_line'
    lyrics_df.loc[(lyrics_df['line_label'] == 'NEGATIVE') & (lyrics_df['hugface_label'] == 'NEGATIVE'), 'positivity_bar_chart'] = 'neg_word_neg_line'
    lyrics_df.loc[(lyrics_df['line_label'] == 'NEGATIVE') & (lyrics_df['hugface_label'] == 'POSITIVE'), 'positivity_bar_chart'] = 'pos_word_neg_line'
    lyrics_df.loc[(lyrics_df['line_label'] == 'POSITIVE') & (lyrics_df['hugface_label'] == 'NEGATIVE'), 'positivity_bar_chart'] = 'neg_word_pos_line'

    return lyrics_df, lines_df


def positivity_barplot_data(lyrics0_df_in, lyrics1_df_in):
    # Check whether the two songs have the same song name. 
    # If they do, make sure their song names are different
    lyrics0_df = lyrics0_df_in.copy(deep=True)
    lyrics1_df = lyrics1_df_in.copy(deep=True)
    if (lyrics0_df_in.at[0, 'song_name'] == lyrics1_df_in.at[0, 'song_name']):
        lyrics0_df.loc[:, 'song_name'] = lyrics0_df_in.at[0, 'song_name'] + " v0"
        lyrics1_df.loc[:, 'song_name'] = lyrics1_df_in.at[0, 'song_name'] + " v1"

    """ Get counts of how many times a positive word was in a positive line
        and the other combinations per song. Convert into a dictionary for d3"""
    both_songs_df = pd.concat([lyrics0_df, lyrics1_df], ignore_index=True)

    # Add a column that will be used to count
    both_songs_df['count'] = 1

    # Group by song and positivity alignment, then count
    both_songs_df = both_songs_df.groupby(['song_name', 'positivity_bar_chart'], as_index=False).count()

    data = {'columns':['pos_word_pos_line', 'neg_word_neg_line', 'pos_word_neg_line', 'neg_word_pos_line']}
    i = 0
    for positivity_val in ['pos_word_pos_line', 'neg_word_neg_line', 'pos_word_neg_line', 'neg_word_pos_line']:
        t = {'group': positivity_val}
        for song_name in both_songs_df['song_name'].unique():
            t[song_name] = float(both_songs_df.loc[(both_songs_df['song_name'] == song_name) \
                    & (both_songs_df['positivity_bar_chart'] == positivity_val) , 'count'].values[0])

            # Normalize by how many lines are in the song. Put into a percentage
            t[song_name] = 100. * t[song_name] / float(both_songs_df.loc[both_songs_df['song_name'] == song_name, 'count'].sum())
        data[i] = t
        i += 1

    return data
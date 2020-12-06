from lyrics_preprocess import preprocess_lyrics

artist_name = "Vanilla Ice"
song_name = "Ice Ice Baby"

lyrics_df, lines_df = preprocess_lyrics(artist_name, song_name)

lyrics_df.to_csv("TEMP_test_lyrics.csv")
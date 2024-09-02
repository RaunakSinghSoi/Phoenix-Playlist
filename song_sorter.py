import pandas as pd
from sentiment_analysis import sentiment_scores

def sort_songs_by_sentiment_and_genre(filename, positive_threshold=0.05, negative_threshold=-0.05):
    data = pd.read_csv(filename)

    positive_songs = data[
        (data['top genre'].isin(['dance pop', 'pop', 'hip pop'])) &
        (data['lyrics'].apply(sentiment_scores) >= positive_threshold)
    ]
    negative_songs = data[
        (data['top genre'].isin(['neo mellow', 'detroit hip hop'])) &
        (data['lyrics'].apply(sentiment_scores) <= negative_threshold)
    ]
    neutral_songs = data[
        (data['top genre'] == 'rock') &
        (data['lyrics'].apply(lambda x: abs(sentiment_scores(x)) < positive_threshold))
    ]

    return positive_songs, negative_songs, neutral_songs

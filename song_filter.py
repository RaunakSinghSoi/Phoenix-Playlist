import pandas as pd
from sentiment_analysis import SentimentAnalyzer

class SongFilter:
    def __init__(self, filename, sentiment_analyzer):
        self.filename = filename
        self.sentiment_analyzer = sentiment_analyzer
        self.data = pd.read_csv(filename)
        self.data['sentiment'] = self.data['lyrics'].apply(self.sentiment_analyzer.analyze)

    def filter_songs(self, positive_threshold=0.05, negative_threshold=-0.05):
        positive_songs = self.data[
            (self.data['top genre'].isin(['dance pop', 'pop', 'hip pop'])) &
            (self.data['sentiment'] >= positive_threshold)
        ]
        negative_songs = self.data[
            (self.data['top genre'].isin(['neo mellow', 'detroit hip hop'])) &
            (self.data['sentiment'] <= negative_threshold)
        ]
        neutral_songs = self.data[
            (self.data['top genre'] == 'rock') &
            (abs(self.data['sentiment']) < positive_threshold)
        ]

        return positive_songs[['title', 'artist', 'release_year']], negative_songs[['title', 'artist', 'release_year']], neutral_songs[['title', 'artist', 'release_year']]

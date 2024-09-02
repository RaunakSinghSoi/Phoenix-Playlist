from song_filter import SongFilter
from sentiment_analysis import SentimentAnalyzer

def main():
    filename = "phoenixDATASET.csv"
    sentiment_analyzer = SentimentAnalyzer()
    song_filter = SongFilter(filename, sentiment_analyzer)

    positive_songs, negative_songs, neutral_songs = song_filter.filter_songs()

    print("Positive Songs:")
    print(positive_songs)
    print("Negative Songs:")
    print(negative_songs)
    print("Neutral Songs:")
    print(neutral_songs)

if __name__ == "__main__":
    main()

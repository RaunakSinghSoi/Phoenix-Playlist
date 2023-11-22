import csv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def sentiment_scores(sentence):
    sid_obj = SentimentIntensityAnalyzer()
    sentiment_dict = sid_obj.polarity_scores(sentence)

    if sentiment_dict['compound'] >= 0.05:
        return 'Positive'
    elif sentiment_dict['compound'] <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'

def sort_songs_by_sentiment_and_genre():
    sorter_positive = []
    sorter_negative = []
    sorter_neutral = []

    negative_genres = ['neo mellow', 'detroit hip hop']
    neutral_genres = ['rock']

    with open("phoenixDATASET.csv", 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for line in reader:
            sentiment_target = sentiment_scores(line['lyrics'])

            if sentiment_target == 'Positive' and line['top genre'] in ['dance pop', 'pop', 'hip pop']:
                sorter_positive.append(line['title'])
            elif sentiment_target == 'Negative' and line['top genre'] in negative_genres:
                sorter_negative.append(line['title'])
            elif sentiment_target == 'Neutral' and line['top genre'] in neutral_genres:
                sorter_neutral.append(line['title'])

    return sorter_positive, sorter_negative, sorter_neutral

# Example usage:
positive_songs, negative_songs, neutral_songs = sort_songs_by_sentiment_and_genre()
print("Positive Songs:", positive_songs)
print("Negative Songs:", negative_songs)
print("Neutral Songs:", neutral_songs)

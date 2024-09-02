from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class SentimentAnalyzer:
    def __init__(self):
        self.sid = SentimentIntensityAnalyzer()

    def analyze(self, text):
        sentiment_dict = self.sid.polarity_scores(text)
        return sentiment_dict['compound']

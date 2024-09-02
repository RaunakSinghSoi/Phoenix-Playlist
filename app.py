from flask import Flask, render_template, request
import pandas as pd
from sentiment_analysis import sentiment_scores
from song_sorter import sort_songs_by_sentiment_and_genre

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    positive_songs = []
    negative_songs = []
    neutral_songs = []

    if request.method == 'POST':
        file = request.files['dataset']
        file.save('phoenixDATASET.csv')
        positive_songs, negative_songs, neutral_songs = sort_songs_by_sentiment_and_genre('phoenixDATASET.csv')

    return render_template('index.html', 
                           positive_songs=positive_songs.to_dict(orient='records'),
                           negative_songs=negative_songs.to_dict(orient='records'),
                           neutral_songs=neutral_songs.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)

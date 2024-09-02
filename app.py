from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

# Dummy function to simulate your actual data fetching and processing
def sort_songs_by_sentiment_and_genre():
    # Simulated DataFrame (replace with actual data processing)
    data = {
        'title': ['Song1', 'Song2'],
        'artist': ['Artist1', 'Artist2'],
        'release_year': [2021, 2022]
    }
    df = pd.DataFrame(data)
    positive_songs = df[df['title'] == 'Song1']
    negative_songs = df[df['title'] == 'Song2']
    neutral_songs = df[df['release_year'] == 2021]
    return positive_songs, negative_songs, neutral_songs

@app.route('/')
def index():
    positive_songs, negative_songs, neutral_songs = sort_songs_by_sentiment_and_genre()

    # Convert DataFrame to dictionary
    positive_songs_dict = positive_songs.to_dict(orient='records')
    negative_songs_dict = negative_songs.to_dict(orient='records')
    neutral_songs_dict = neutral_songs.to_dict(orient='records')

    return render_template('index.html', 
                           positive_songs=positive_songs_dict, 
                           negative_songs=negative_songs_dict, 
                           neutral_songs=neutral_songs_dict)

if __name__ == '__main__':
    app.run(debug=True)

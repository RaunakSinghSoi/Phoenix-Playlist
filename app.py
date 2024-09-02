from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  # Directory to store uploaded files

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def sort_songs_by_sentiment_and_genre(file_path):
    # Read the uploaded CSV file
    data = pd.read_csv(file_path)

    # Dummy implementation: Replace with your actual logic
    positive_songs = data[data['top genre'].isin(['dance pop', 'pop', 'hip pop']) & 
                          (data['lyrics'].str.contains('good|happy|joy'))]
    negative_songs = data[data['top genre'].isin(['neo mellow', 'detroit hip hop']) & 
                          (data['lyrics'].str.contains('sad|down|bad'))]
    neutral_songs = data[data['top genre'] == 'rock' & 
                          (data['lyrics'].str.contains('neutral'))]

    return positive_songs, negative_songs, neutral_songs

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file upload
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and file.filename.endswith('.csv'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            positive_songs, negative_songs, neutral_songs = sort_songs_by_sentiment_and_genre(file_path)
            # Convert DataFrame to dictionary
            positive_songs_dict = positive_songs.to_dict(orient='records')
            negative_songs_dict = negative_songs.to_dict(orient='records')
            neutral_songs_dict = neutral_songs.to_dict(orient='records')
            return render_template('index.html', 
                                   positive_songs=positive_songs_dict, 
                                   negative_songs=negative_songs_dict, 
                                   neutral_songs=neutral_songs_dict)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

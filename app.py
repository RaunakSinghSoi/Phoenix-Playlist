from flask import Flask, render_template, request
import pandas as pd
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Set upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def sort_songs_by_sentiment_and_genre(filename):
    data = pd.read_csv(filename)

    # Dummy function to simulate actual data processing
    positive_songs = data[data['top genre'].isin(['dance pop', 'pop', 'hip pop']) & (data['lyrics'].str.contains('good|happy'))]
    negative_songs = data[data['top genre'].isin(['neo mellow', 'detroit hip hop']) & (data['lyrics'].str.contains('sad|down'))]
    neutral_songs = data[data['top genre'] == 'rock' & (~data['lyrics'].str.contains('good|happy|sad|down'))]

    return positive_songs, negative_songs, neutral_songs

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
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
    
    return render_template('index.html', 
                           positive_songs=[], 
                           negative_songs=[], 
                           neutral_songs=[])

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)

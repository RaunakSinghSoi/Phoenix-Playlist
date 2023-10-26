
#ProjectPhoenix
#YEAR 2023

import csv
#Part 1 set up vader
from vaderSentiment import SentimentIntensityAnalyzer
 

def sentiment_scores(sentence):
 
    sid_obj = SentimentIntensityAnalyzer()
 
    sentiment_dict = sid_obj.polarity_scores(sentence)
    
     
  
    if sentiment_dict['compound'] >= 0.05 :
        target='Positive'
        
 
    elif sentiment_dict['compound'] <= - 0.05 :
        target= 'Negative'
 
    else :
        target='Neutral'
#Part 2 sorting the csv file
    csvfile = open("phoenixDATASET.csv", 'r')
    reader = csv.DictReader(csvfile)
    library=list(reader)
    sorter=[]
    sorter_positive = []
    sorter_negative = []
    sorter_neutral = []
    negative_genres = ['neo mellow', 'detroit hip hop']
    neutral_genres = ['rock']
    for line in reader:
        if target == 'Positive' and (line['top genre'] in ['dance pop', 'pop', 'hip pop']):
                sorter_positive.append(line['title'])
        elif target == 'Negative' and (line['top genre'] in negative_genres):
                sorter_negative.append(line['title'])
        elif target == 'Neutral' and (line['top genre'] in neutral_genres):
                sorter_neutral.append(line['title'])
            
    return sorter_positive, sorter_negative, sorter_neutral    

import csv
from vaderSentiment import SentimentIntensityAnalyzer

def sentiment_scores(sentence):
    sid_obj = SentimentIntensityAnalyzer()
    sentiment_dict = sid_obj.polarity_scores(sentence)
    
    if sentiment_dict['compound'] >= 0.05:
        target = 'Positive'
    elif sentiment_dict['compound'] <= -0.05:
        target = 'Negative'
    else:
        target = 'Neutral'
    
    return target  # Return the sentiment target

def sort_songs_by_sentiment_and_genre():
    # Initialize lists to store sorted songs
    sorter_positive = []
    sorter_negative = []
    sorter_neutral = []

    negative_genres = ['neo mellow', 'detroit hip hop']
    neutral_genres = ['rock']

    # Open the CSV file and read it as a dictionary
    with open("phoenixDATASET.csv", 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for line in reader:
            # Get the sentiment target for the current song's lyrics
            target = sentiment_scores(line['lyrics'])

            # Sort songs into appropriate lists based on sentiment and genre
            if target == 'Positive' and line['top genre'] in ['dance pop', 'pop', 'hip pop']:
                sorter_positive.append(line['title'])
            elif target == 'Negative' and line['top genre'] in negative_genres:
                sorter_negative.append(line['title'])
            elif target == 'Neutral' and line['top genre'] in neutral_genres:
                sorter_neutral.append(line['title'])

    return sorter_positive, sorter_negative, sorter_neutral


                 
           


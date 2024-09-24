import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from urllib.parse import parse_qs, urlparse
import json
import pandas as pd
from datetime import datetime
import uuid
import os
from typing import Callable, Any
from wsgiref.simple_server import make_server

nltk.download('vader_lexicon', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('stopwords', quiet=True)

adj_noun_pairs_count = {}
sia = SentimentIntensityAnalyzer()
stop_words = set(stopwords.words('english'))

reviews = pd.read_csv('data/reviews.csv').to_dict('records')

valid_loca = {
    "Albuquerque, New Mexico", "Carlsbad, California", "Chula Vista, California",
    "Colorado Springs, Colorado", "Denver, Colorado", "El Cajon, California",
    "El Paso, Texas", "Escondido, California", "Fresno, California", "La Mesa, California",
    "Las Vegas, Nevada", "Los Angeles, California", "Oceanside, California",
    "Phoenix, Arizona", "Sacramento, California", "Salt Lake City, Utah",
    "San Diego, California", "Tucson, Arizona"
}

class ReviewAnalyzerServer:
    def __init__(self) -> None:
        # This method is a placeholder for future initialization logic
        pass

    def analyze_sentiment(self, review_body):
        sentiment_scores = sia.polarity_scores(review_body)
        return sentiment_scores

    def __call__(self, environ: dict[str, Any], start_response: Callable[..., Any]) -> bytes:
        """
        The environ parameter is a dictionary containing some useful
        HTTP request information such as: REQUEST_METHOD, CONTENT_LENGTH, QUERY_STRING,
        PATH_INFO, CONTENT_TYPE, etc.
        """

        if environ["REQUEST_METHOD"] == "GET":
            # Create the response body from the reviews and convert to a JSON byte string
            q_str = parse_qs(environ["QUERY_STRING"])
            loca = q_str.get('location', [None])[0]
            s_date = q_str.get('start_date', [None])[0]
            e_date = q_str.get('end_date', [None])[0]

            f_reviews = reviews
            print(loca,s_date,e_date)

            # Lcoation checking 
            if loca:
                if loca not in valid_loca:
                    print("Not val")
                    start_response("400 Bad Request", [("Content-Type", "application/json")])
                    return [b"Not valid location"]
                f_reviews = [review for review in f_reviews if review['Location']  == loca]

            # if s_date or e_date:

            response_body = json.dumps(f_reviews, indent=2).encode("utf-8")
            
            

            # Set the appropriate response headers
            start_response("200 OK", [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(response_body)))
             ])
            
            return [response_body]


        if environ["REQUEST_METHOD"] == "POST":
            # Write your code here
            return

if __name__ == "__main__":
    app = ReviewAnalyzerServer()
    port = os.environ.get('PORT', 8000)
    with make_server("", port, app) as httpd:
        print(f"Listening on port {port}...")
        httpd.serve_forever()
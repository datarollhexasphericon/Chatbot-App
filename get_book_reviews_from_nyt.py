import os
from dotenv import load_dotenv
import requests
import random

# Load environment variables from a .env file
load_dotenv()

def get_nyt_book_review(book_title, book_author):
    # Base URL for the New York Times book reviews API
    base_url = "https://api.nytimes.com/svc/books/v3/reviews.json"

    # Parameters for the API request, including the book title and API key
    params = {
        "title": book_title,
        "api-key": os.environ.get('NYT_API_KEY')
    }

    # Send a GET request to the NYT API
    response = requests.get(base_url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response as JSON
        data = response.json()
        # Get the list of results (reviews)
        results = data.get('results', [])

        if results:
            # Filter reviews to match the book author
            matching_reviews = [review for review in results if review['book_author'].lower() == book_author.lower()]

            if matching_reviews:
                # Randomly select one of the matching reviews
                selected_review = random.choice(matching_reviews)
                # Return the formatted review
                return f"Here is a review of {selected_review['book_title']} from the New York Times by {selected_review['byline'].title()}.\n{selected_review['summary']}"
            else:
                # Return a message if no reviews match the author
                return "Apologies, I couldn't find any book by the name you provided."
        else:
            # Return a message if no reviews match the title
            return "Apologies, there are no reviews in the New Your Times for the book title you provided."
    else:
        # Return a message if the request failed
        return f"Failed to retrieve book review. Status code: {response.status_code}"

# Example usage
# book_author = 'Stephen King'
# book_title = 'The Institute'
# print(get_nyt_book_review(book_title, book_author))


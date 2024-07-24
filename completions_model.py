from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from get_book_reviews_from_nyt import get_nyt_book_review

model = "gpt-4o-mini"

# System guidelines
chatbot_purpose = ("You are a sophisticated, knowledgeable, and friendly chatbot designed to assist users with "
                   "book-related inquiries. Your primary roles include providing personalized book recommendations "
                   "based on user preferences, offering detailed book reviews, and answering general questions "
                   "about books and authors. Your goal is to enhance the user's reading experience by guiding them "
                   "to books they'll love and providing insightful, accurate information. For unrelated queries, "
                   "output the message 'Sorry, I can only answer book-related inquiries.")

audience_guidelines = ("The target audience of the chatbot are book enthusiasts of all ages and backgrounds, ranging "
                       "from casual readers to avid bibliophiles, seeking personalized book recommendations and reviews.")

tone_guidelines = ("Use a friendly, knowledgeable, and approachable tone while interacting with users, ensuring "
                   "responses are clear, engaging, and supportive. Keep responses concise and to the point, not "
                   "exceeding 100 tokens.")

system_prompt = chatbot_purpose + audience_guidelines + tone_guidelines

# Function definition
function_definition = [
    {
    'type': 'function',
    'function':{
        'name': "provide_book_recommendations",
        "description": "Provide book recommendations based on user's preferences, interests or other books they have read if the user asks you to. "
                       "If the user does not state their preferences, interests or other books they have read, ask the user "
                       "to provide them. Recommend one book only.",
        "parameters": {
            'type': "object",
            'properties': {
                'book author': {"type": "string", "description": "Book author."},
                'book title': {"type": "string", "description": "Book title."},
                'book description': {"type": "string", "description": "Description of the book and why it may be "
                                                                      "of interest to the user."}},
            'required': ["book author", "book title", "book description"]
        }}},
    {
    'type': 'function',
    'function':{
        'name': "get_nyt_book_review",
        "description": "This function calls the The New York Times Book API to get reviews of a specific book based on "
                       "the book author name and the book title from the user input. If the user does not provide the "
                       "full name of the author, fetch it yourself.",
        "parameters": {
            'type': "object",
            'properties': {
                'book author': {"type": "string", "description": "Book author name to be passed to get_book_review function."},
                'book title': {"type": "string", "description": "Book title to be passed to get_book_review function."}},
            'required': ["book author", "book title"]
        }}}
    ]

# Load environment variables from a .env file
load_dotenv()

# Create the OpenAI client
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# Setting up system roles and sample prompts for in-context-learning
messages =[
    {"role":"system",
     "content": system_prompt},
    {"role":"user",
     "content": "What do you think of '1984' by George Orwell?"},
    {"role": "assistant",
     "content": "'1984' by George Orwell is a profound and thought-provoking novel that delves into themes of totalitarianism, surveillance, and individuality. Its chilling depiction of a dystopian future continues to be relevant and impactful. Highly recommended for readers interested in political and social commentary."}
]

def get_system_reply(question):
    # Append the user's question to the messages list
    messages.append({"role": "user", "content": question})

    # Send the conversation history to the chat completion API
    response = client.chat.completions.create(
        model=model,
        max_tokens=100,
        messages=messages,
        tools=function_definition,
        tool_choice='auto',
        temperature=0)

    # Check if the response includes tool calls
    if response.choices[0].finish_reason == 'tool_calls':
        # Extract the tool call information
        function_call = response.choices[0].message.tool_calls[0].function

        # If the tool call is for fetching a NYT book review
        if function_call.name == "get_nyt_book_review":
            # Extract the book title and author from the function arguments
            title_keyword = json.loads(function_call.arguments)["book title"]
            author_keyword = json.loads(function_call.arguments)["book author"]
            # Get the book review
            review = get_nyt_book_review(title_keyword, author_keyword)
            # Append the review to the messages list
            messages.append({"role": "user", "content": review})
            return review

        # If the tool call is for providing book recommendations
        elif function_call.name == "provide_book_recommendations":
            # Extract the book title, author, and description from the function arguments
            title_keyword = json.loads(function_call.arguments)["book title"]
            author_keyword = json.loads(function_call.arguments)["book author"]
            description_keyword = json.loads(function_call.arguments)["book description"]
            # Create a book suggestion
            suggestion = f"Here is a book you may like: {title_keyword} by {author_keyword}.\n{description_keyword}"
            # Append the suggestion to the messages list
            messages.append({"role": "user", "content": suggestion})
            return suggestion
        else:
            print("I am sorry, but I could not understand your request.")
    else:
        # If no tool call is needed, return the content of the response
        reply = response.choices[0].message.content
        messages.append({"role": "user", "content": reply})
        return reply

# Example usage
#book_author = 'Markus Zusak'
#book_title = 'The Book Thief'
#question1 = f"Can you provide a review for '{book_title}' by {book_author}?"
# question2 = "Are Harry Potter books a good read for adults?"
# question3 = "I like historical novels that are based on facts. Can you recommend a book?"

# Get the system reply
#reply1 = get_system_reply(question1)
#print(reply1)
#
# reply2 = get_system_reply(question2)
# print(reply2)
#
# reply3 = get_system_reply(question3)
# print(reply3)
from flask import Flask, render_template, request, jsonify, g
import sqlite3
import wikipedia
from googlesearch import search
import requests
from bs4 import BeautifulSoup
from nltk.chat.util import Chat, reflections
import datetime

app = Flask(__name__, static_url_path='/static', static_folder='static')

DATABASE = 'chatbot.db'

# Function to search Wikipedia
def search_wikipedia(query):
    try:
        result = wikipedia.summary(query, sentences=2)
        return result
    except wikipedia.exceptions.DisambiguationError as e:
        return "I found multiple results. Can you be more specific?"
    except wikipedia.exceptions.PageError as e:
        return None  # Return None when Wikipedia doesn't find any information

# Function to search Google and return search results with written information
def search_google(query):
    try:
        search_results = search(query, num=5, stop=5, pause=2)
        results_with_info = []
        for url in search_results:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            text = '\n'.join([p.get_text() for p in paragraphs])
            results_with_info.append((url, text))
        return results_with_info
    except Exception as e:
        return None  # Return None if there's an error during the search

# Function to get the database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Function to close the database connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Function to fetch pairs from the database
def fetch_pairs_from_database():
    with app.app_context():
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT user_input, bot_response FROM pairs")
        pairs = c.fetchall()
        return pairs

# Function to fetch conversation history from the database
def fetch_conversation_history():
    with app.app_context():
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT user_input, bot_response FROM conversations ORDER BY timestamp DESC")
        history = c.fetchall()
        return history

# Function to update the bot's knowledge based on pairs from the database
def update_bot_knowledge_from_database():
    pairs = fetch_pairs_from_database()
    return Chat(pairs, reflections)

# Create and train the chatbot
chatbot = update_bot_knowledge_from_database()

# Function to start the chat
@app.route('/')
def index():
    history = fetch_conversation_history()
    return render_template('application.html', history=history)

@app.route('/get_bot_response', methods=['POST'])
def get_bot_response_route():
    user_input = request.json.get('user_input')
    response = None
    prompt_correction = False  # Flag for update prompt

    # First, check the stored pairs in the database
    pairs = fetch_pairs_from_database()
    for pair in pairs:
        if user_input.lower() == pair[0].lower():
            response = pair[1]
            break
        elif user_input.lower() in pair[0].lower():
            response = pair[1]
            break

    if response is None:
        # If no response from pairs, check the conversation history
        history = fetch_conversation_history()
        for entry in history:
            if user_input.lower() in entry[0].lower():
                response = entry[1]
                break

    if response is None:
        # If still no response, check Wikipedia
        if "wikipedia" in user_input.lower():
            query = user_input.replace("wikipedia", "").strip()
            response = search_wikipedia(query)

    if response is None:
        # If still no response, search Google
        response = search_google(user_input)

    if isinstance(response, list):
        response = '\n'.join([f"{url}\n{text}\n" for url, text in response])
    elif response is None:
        # If no response found, set flag for update prompt
        response = "I couldn't find an answer to your question. Would you like to provide the correct response for this query?"
        prompt_correction = True

    return jsonify({"response": response, "prompt_correction": prompt_correction})

# Function to store conversation in the database
def store_conversation(user_input, bot_response):
    with app.app_context():
        conn = get_db()
        c = conn.cursor()
        timestamp = datetime.datetime.now()
        c.execute("INSERT INTO conversations (user_input, bot_response, timestamp) VALUES (?, ?, ?)", (user_input, bot_response, timestamp))
        conn.commit()

# Route to handle updating bot knowledge
@app.route('/update_knowledge', methods=['POST'])
def update_knowledge_route():
    data = request.json
    user_input = data.get('user_input')
    correct_response = data.get('correct_response')
    
    # Insert the new pair into the database
    with app.app_context():
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO pairs (user_input, bot_response) VALUES (?, ?)", (user_input, correct_response))
        conn.commit()
    
    # Update the chatbot with the new knowledge
    global chatbot
    chatbot = update_bot_knowledge_from_database()
    
    return jsonify({"message": "Bot knowledge updated successfully"})

if __name__ == '__main__':
    app.run(debug=True)

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
from chatterbot.conversation import Statement
from chatterbot.tagging import PosTags

# Create a custom POS tagger that doesn't depend on spaCy
class CustomPosTagger(PosTags):
    def get_pos_tags(self, text):
        return []

# Initialize ChatBot and connect to SQLite database
chatbot = ChatBot('InfoBot', storage_adapter='chatterbot.storage.SQLStorageAdapter',
                  database_uri='sqlite:///database.db', tagger=CustomPosTagger())

# Train the chatbot
trainer = ChatterBotCorpusTrainer(chatbot)

# Train using the English corpus
trainer.train('chatterbot.corpus.english')

# Optionally, train using custom data
trainer = ListTrainer(chatbot)
trainer.train([
    'What is your name?',
    'My name is InfoBot. I can provide you with information on various topics.'
    # Add more pairs as needed
])

# Implement chat loop
while True:
    try:
        user_input = input("You: ")

        # Get response from chatbot
        response = chatbot.get_response(user_input)

        # Print chatbot's response
        print("InfoBot:", response)

        # Save the conversation to the database
        statement = Statement(text=user_input)
        response_statement = Statement(text=str(response))
        chatbot.storage.create_conversation(statement, response_statement)

    except (KeyboardInterrupt, EOFError, SystemExit):
        break

# Save changes and close database connection
chatbot.storage.drop()

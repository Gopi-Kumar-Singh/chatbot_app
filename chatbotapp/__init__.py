import pandas as pd
import nltk
import string
import random
import re
import os
from django.shortcuts import render
from nltk.metrics.distance import jaccard_distance
from nltk.util import ngrams
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Specify NLTK data directory
nltk_data_dir = "../nltk"  # Change this to your desired directory

# Check if NLTK data directory exists, if not, create it
if not os.path.exists(nltk_data_dir):
    os.makedirs(nltk_data_dir)

# Set NLTK data directory
nltk.data.path.append(nltk_data_dir)

# Check if NLTK resources are already downloaded, if not, download them
if not os.path.exists(os.path.join(nltk_data_dir, "corpora", "stopwords")):
    # print("stopwords Not avaiable downloading")
    nltk.download('stopwords', download_dir=nltk_data_dir)

if not os.path.exists(os.path.join(nltk_data_dir, "corpora", "wordnet")):
    # print("wordnet Not avaiable downloading")
    nltk.download('wordnet', download_dir=nltk_data_dir)

if not os.path.exists(os.path.join(nltk_data_dir, "corpora", "words")):
    # print("wordnet Not avaiable downloading")
    nltk.download('words', download_dir=nltk_data_dir)

if not os.path.exists(os.path.join(nltk_data_dir, "tokenizers", "punkt")):
    # print("tokenizers and punkt Not avaiable downloading")
    nltk.download('punkt', download_dir=nltk_data_dir)

from nltk.corpus import stopwords
from nltk.corpus import words

correct_words = words.words()

exit_words = {'bye', 'exit', 'goodbye', 'quit'}
threshold_value = 0.1
feedback_suffix = "If you need any more help or have further questions, feel free to ask."
faq_database_csv_path = '/home/gopi/Desktop/my-projects/chatbot_app/chatbotapp/faqs_database.csv'
positive_feedback_responses = [
    "Thank you!",
    "Glad I could help!",
    "You're welcome!",
    "Happy to assist!",
    "Anytime!",
    "No problem!",
    "My pleasure!"
]

faq_database = pd.read_csv(faq_database_csv_path)


# this is a function for checking for spelling mistakes in the words and returning the closest correct word present
# in the list of correct words
def check_for_spelling_mistakes(givenWord):
    # Filter words starting with the same letter as givenWord
    filtered_words = [w for w in correct_words if w[0] == givenWord[0]]

    try:
        temp = [(jaccard_distance(set(ngrams(givenWord, 2)),
                                  set(ngrams(w, 2))), w)
                for w in filtered_words]

        # Sort and return the closest word with the lowest Jaccard distance
        closest_word = sorted(temp, key=lambda val: val[0])[0][1]
        return closest_word
    except Exception as e:
        print(f"Error in check_for_spelling_mistakes: {e}")
        return givenWord


# for preprocessing text
def preprocess_text(text):
    # Initialize lemmatizer
    lemmatizer = WordNetLemmatizer()

    # Define stopwords
    stop_words = set(stopwords.words("english"))

    # Initialize Stemmer
    stemmer = PorterStemmer()

    # Converting to lower-case
    text = text.lower()

    # Tokenize the text
    words = word_tokenize(text)

    # checking for spelling mistakes and correcting it.
    correct_words = [check_for_spelling_mistakes(word) for word in words]

    # Remove stopwords and punctuation
    filtered_words = [word for word in correct_words if word not in stop_words and word not in string.punctuation]

    # Stemming text
    stemmed_words = [stemmer.stem(word) for word in filtered_words]

    # Lemmatizating text
    lemmatized_words = {lemmatizer.lemmatize(word) for word in stemmed_words}

    return ' '.join(list(lemmatized_words))


# for generating tags
def generate_tags(question, answer):
    unprocessed_tag = question + " " + answer
    tag = preprocess_text(unprocessed_tag)
    return tag

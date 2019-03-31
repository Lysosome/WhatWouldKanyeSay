from flask import Flask, render_template, request, url_for, redirect, flash
import wtforms
app = Flask(__name__)

import keras
import gensim.downloader as api
import numpy as np
import pickle
import keras
from keras.models import Sequential
from keras.layers import Dense, LSTM
import language_check
import random
from google.cloud import texttospeech
from text_generation import generate_text

NUM_CLOSEST = 10 # number of closest words to use
CHAR_INPUT_LEN = 40 # number of chars the model takes
PERSONALITIES = ["kanye", "nietzsche"]

def build_model(num_chars):
    model = Sequential()
    model.add(LSTM(128, input_shape=(CHAR_INPUT_LEN, num_chars)))
    model.add(Dense(num_chars, activation='softmax'))
    return model

@app.route('/')
def index():
    return render_template('./templates/index.html')

@app.route('/result_page', methods = ['GET', 'POST'])
def result():
    personality = str(request.form.get('personality'))
    prompt = str(request.form.get('prompt'))

    # Generate Text
    generated_text = generate_text(
                        models[personality],
                        prompt,
                        word_vectors,
                        char_indices_dict[personality],
                        indices_char_dict[personality],
                        min_length=100,
                        max_length=200)

    picture = "./assets/" + personality + ".jpg"
    print("GENERATED TEXT: "+generated_text)
    print("PICTURE: "+picture)
    return render_template('./templates/results_page.html', pic_url=picture, text=generated_text)

if __name__ == '__main__':
    # Initialize
    models = {}
    char_indices_dict = {}
    indices_char_dict = {}
    for personality in PERSONALITIES:
        print("Loading dicts and models for personality '"+personality+"'...")
        # 1. load all Char-Index dictionaries
        CHAR_INDEX_FILE = "../models/char_index_" + personality + ".p"
        with open(CHAR_INDEX_FILE, "rb") as f:
            char_indices_dict[personality] = pickle.load(f)
            indices_char_dict[personality] = {v: k for k, v in char_indices_dict[personality].items()}

        # 2. load all Char-RNN models
        model = build_model(len(char_indices_dict[personality]))
        MODEL_FILE = "../models/" + personality + ".h5"
        model.load_weights(MODEL_FILE)
        models[personality] = model

    print("Loading word vectors...")
    # 3. load word vectors
    word_vectors = api.load("glove-wiki-gigaword-100")

    print("Starting server...")
    # Start fielding requests
    app.run(debug = True)
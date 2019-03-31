from flask import Flask, render_template, request, url_for, redirect, flash
app = Flask(__name__)

import keras
import gensim.downloader as api
import numpy as np
import pickle
from keras.models import Sequential
from keras.layers import Dense, LSTM
import language_check
import random
from google.cloud import texttospeech
from text_generation import generate_text, text_to_speech
import os

NUM_CLOSEST = 10 # number of closest words to use
CHAR_INPUT_LEN = 40 # number of chars the model takes
PERSONALITIES = ["kanye", "nietzsche", "cardib", "shakespeare", "tolkien", "tyson", "poe"]
MODEL_WARMUP = True

def build_model(num_chars):
    model = Sequential()
    model.add(LSTM(128, input_shape=(CHAR_INPUT_LEN, num_chars)))
    model.add(Dense(num_chars, activation='softmax'))
    return model

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result_page', methods = ['GET', 'POST'])
def result():
    personality = str(request.form.get('personality'))
    prompt = (str(request.form.get('prompt'))).lower()

    area = "en-US"
    gender = "male"
    autocorrect_on = True

    if(personality=="cardib"):
        autocorrect_on = False
    if(personality=="shakespeare" or personality=="tolkien"):
        area = "en-GB"
    if(personality=="nietzsche"):
        area="de-DE"
    if(personality=="cardib"):
        gender="female"

    # Generate Text
    generated_text = generate_text(
                        models[personality],
                        prompt,
                        word_vectors,
                        char_indices_dict[personality],
                        indices_char_dict[personality],
                        min_length=200,
                        max_length=250,
                        grammar_check=autocorrect_on)

    # Text To Speech
    rand = str(random.randint(0, 1e4)) # add a random number to prevent cache reusing old files with same name
    audio_fname = "./static/"+personality+"_"+prompt+"_"+rand+".mp3"
    text_to_speech(generated_text, audio_fname, area=area, gender=gender)

    picture = "https://github.com/Lysosome/WhatWouldKanyeSay/raw/master/web/assets/" + personality + ".jpg"
    # picture = "./assets/" + personality + ".jpg"
    print("GENERATED TEXT: "+generated_text)
    print("PICTURE: "+picture)
    return render_template('result_page.html', pic_url=picture, text=generated_text, song=audio_fname)

if __name__ == '__main__':
    # os.environ['THEANO_FLAGS'] = "device=cuda,floatX=float32"
    # Initialize

    models = {}
    char_indices_dict = {}
    indices_char_dict = {}
    for personality in PERSONALITIES:

        print("Loading models and dicts for personality '"+personality+"'...")
        # 1. load all Char-Index dictionaries
        CHAR_INDEX_FILE = "../models/char_index_" + personality + ".p"
        with open(CHAR_INDEX_FILE, "rb") as f:
            char_indices_dict[personality] = pickle.load(f)
            indices_char_dict[personality] = {v: k for k, v in char_indices_dict[personality].items()}

        # 2. load all Char-RNN models
        model = build_model(len(char_indices_dict[personality]))
        MODEL_FILE = "../models/" + personality + ".h5"
        model.load_weights(MODEL_FILE)
        if(MODEL_WARMUP): # warm up the model before using it to speed up inference later
            print("warming up "+personality+" model...")
            model.predict(np.zeros((1, CHAR_INPUT_LEN, len(char_indices_dict[personality]))), verbose=0)
        models[personality] = model



    print("Loading word vectors...")
    # 3. load word vectors
    word_vectors = api.load("glove-wiki-gigaword-50") #("glove-wiki-gigaword-100")

    print("Starting server...")
    # Start fielding requests
    app.run(debug = True)
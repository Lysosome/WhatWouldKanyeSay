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

PERSONALITY = "kanye"
NUM_CLOSEST = 10 # number of closest words to use
CHAR_INPUT_LEN = 40 # number of chars the model takes
CHAR_INDEX_FILE = "../models/char_index_"+PERSONALITY+".p"
MODEL_FILE = "../models/"+PERSONALITY+".h5"
AUDIO_FNAME = "../audio/"+PERSONALITY+'.mp3'

def build_model(num_chars):
    model = Sequential()
    model.add(LSTM(128, input_shape=(CHAR_INPUT_LEN, num_chars)))
    model.add(Dense(num_chars, activation='softmax'))
    return model

def sample(preds, temperature=1.0):
    # helper function to sample an index from a probability array
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)

# model = the Char-RNN model
# prompt = string containing the text prompt
# word_vectors = a Gensim KeyedVectors object with the word vectors we want to use for word similarity
# char_indices = dict of chars to their indexes
# indices_char = reverse
# temperature = temperature for generation (higher number = more random)
# min_length = minimum number of chars for the model to generate (once this is hit, it will terminate on sentence end)
# max_length = max number of chars (HARD CAP--will stop generating after this number)
# word_scatter = whether to pepper related words throughout the generated text or not
# language_check = whether to apply spelling and grammar check
def generate_text(model,
                  prompt,
                  word_vectors,
                  char_indices,
                  indices_char,
                  temperature=0.5,
                  min_length=250,
                  max_length=400,
                  word_scatter = True,
                  language_check = True):
    print("Generating text from prompt "+prompt)

    # 1. (OPTIONAL) SEED PROMPT WITH RELATED WORDS
    try:
        # close_words is a list of just the words in descending order
        close_words = [tup[0] for tup in word_vectors.most_similar_cosmul(positive=prompt.split(), topn=NUM_CLOSEST)]
        close_words_rev = reversed(close_words) # now ascending order of closeness
        modified_prompt = " ".join(close_words_rev) + " " + prompt
        modified_prompt = modified_prompt[-(CHAR_INPUT_LEN-1):] + " " # only keep the last CHAR_INPUT_LEN characters
    except KeyError:
        print("error: prompt '"+prompt+"' not in vocabulary")
        modified_prompt = prompt
    print("input sequence: " + modified_prompt)

    # 2. GENERATE NEW CHARS ONE BY ONE UNTIL LENGTH IS HIT
    output = prompt
    doneYet = False
    while not doneYet:
        # parse input string into chars
        x_pred = np.zeros((1, CHAR_INPUT_LEN, len(char_indices)))
        for t, char in enumerate(modified_prompt):
            if(char not in char_indices.keys()):
                continue
            x_pred[0, t, char_indices[char]] = 1.
        preds = model.predict(x_pred, verbose=0)[0]
        next_index = sample(preds, temperature)
        next_char = indices_char[next_index]
        output += next_char
        if(len(modified_prompt)>=CHAR_INPUT_LEN):
            modified_prompt = modified_prompt[1:] + next_char
        else:
            modified_prompt += next_char

        # if we're interspersing words, we can check here.
        if(word_scatter):
            word_to_add=""
            if(next_char==" " and random.random() < 0.1):
                word_to_add = close_words[random.randint(0, NUM_CLOSEST - 1)] # TODO: EDIT WORD PICKING DISTRIBUTION?
            elif( (next_char=="." or next_char==",") and random.random() < 0.3):
                word_to_add = " "+close_words[random.randint(0, NUM_CLOSEST-1)]
            if(word_to_add!=""):
                output += word_to_add
                modified_prompt = modified_prompt[len(word_to_add):] + word_to_add

        # check if done yet
        if( (len(output)>max_length) or (len(output)>min_length and output[-2:]==". ") ):
            doneYet = True

    # 3. RUN GRAMMAR / SPELL CHECK
    if(language_check):
        tool = language_check.LanguageTool('en-US')
        matches = tool.check(output)
        corrected_output = language_check.correct(output, matches)
        print("Number of grammar errors corrected:", len(matches))
        return corrected_output
    return output

def text_to_speech(words):
    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.types.SynthesisInput(text=words)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.types.VoiceSelectionParams(
        language_code='en-GB',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)

    # Select the type of audio file you want returned
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    # The response's audio_content is binary.
    out_fname = AUDIO_FNAME
    with open(out_fname, 'wb') as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print('Audio content written to file '+out_fname)

def main():
    # load model, word_vectors, char dictionaries
    with open(CHAR_INDEX_FILE, "rb") as f:
        char_indices = pickle.load(f)
        indices_char = {v: k for k, v in char_indices.items()}
    word_vectors = api.load("glove-wiki-gigaword-100")
    model = build_model(len(char_indices))
    model.load_weights(MODEL_FILE)

    # generate text
    out = generate_text(model, "potato chip", word_vectors, char_indices, indices_char)
    print(out)

    # text-to-speech
    text_to_speech(out)

if(__name__=="__main__"):
    main()
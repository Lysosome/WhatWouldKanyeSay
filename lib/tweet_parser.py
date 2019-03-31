# Cleans tweets and writes to output file
def clean_tweets(name, output):
    with open(name, encoding='unicode_escape') as file:
        text = file.read().lower()

    text = ''.join([t if ord(t) < 130 else '' for t in text])
    text = ''.join([t if ord(t) != 128 else "\'" for t in text])
    text = text.replace('\x81', ' ')
    text = text.replace('rt', '')
    text_file = open(output, "w")
    text_file.write(text)
    text_file.close()
    return


if __name__ == '__main__':
    # Pass in the name of the txt file created by tweet_dumper.py
    name = 'iamcardib_tweets.txt'

    # Pass in the name of the desired output file
    output = 'cardib_corpus.txt'

    clean_tweets(name, output)
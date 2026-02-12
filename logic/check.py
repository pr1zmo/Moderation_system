import csv
import string

# with open("test.csv", "r") as f:
#     reader = csv.reader(f, delimiter="\t")
#     for i, line in enumerate(reader):
#         print 'line[{}] = {}'.format(i, line)

def check_text(text: str) -> bool:
    # Placeholder for actual moderation logic
    # For demonstration, let's assume any text containing "bad" is not ok
    # words = sentence.split()
    # word_count = len(words)
    text = text.lower()
    if (len(text.split()) == 1):
        return one_word(text)
    else:
        return sentence(text)
    return True

def one_word(text: str) -> bool:
    with open("data/single_word.csv", "r") as f:
        reader = csv.reader(f, delimiter=",")
        for i, line in enumerate(reader):
            # print('line[{}] = {}'.format(i, line))
            if len(line) < 2:
                continue
            word = line[1].strip().lower()
            score = line[0].strip()
            # print("Score: ", score)
            if (word == text):
                if (int(scoring(word, score)) >= 5):
                    return False
    return True

def sentence(text) -> bool:
    preprocessing(text)
    return False

def preprocessing(text):
    '''
    This is the first step in parsing the word/sentence
    Removing white space, ponctuation and lowercasing the word.
    the end result should be a clear sentence. 
    '''
    translator = str.maketrans('', '', string.punctuation)
    # Apply the translation table to the sentence
    words = text.translate(translator).split()

def tokenize(text):
    '''
    Split the sentence into words, will use that to better pair those words with the preprocessed data
    and decide the result
    '''
    pass

def feature_extraction(text):
    pass

def scoring(text: str, score: int) -> int:
    return score

def Decision():
    return True

#Input text
# ↓
# Preprocessing
# ↓
# Tokenization
# ↓
# Feature extraction
# ↓
# Scoring
# ↓
# Decision (allow / warn / block)
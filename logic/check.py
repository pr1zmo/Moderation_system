import csv
import string
import pandas as pd
import re

i_la = ["|", "1", "!", "í", "ì", "î", "ï"]
a_la = ["4", "@", "á", "à", "â", "ä"]
e_la = ["3", "€", "é", "è", "ê", "ë"]
o_la = ["0", "ó", "ò", "ô", "ö"]
s_la = ["5", "$"]
g_la = ["6", "9"]
t_la = ["7", "+"]
b_la = ["8"]
z_la = ["2"]

LOOKALIKE_GROUPS = {
    "i": i_la,
    "a": a_la,
    "e": e_la,
    "o": o_la,
    "s": s_la,
    "g": g_la,
    "t": t_la,
    "b": b_la,
    "z": z_la,
}

DATA_PATH = "data/labeled_data.csv"
SINGLE_WORD = "data/single_word.csv"
PREPROCESSED = "data/preprocessed_data.csv"

LOOKALIKE_TO_CANON = {}
for canonical, variations in LOOKALIKE_GROUPS.items():
    LOOKALIKE_TO_CANON[canonical] = canonical
    for variation in variations:
        LOOKALIKE_TO_CANON[variation.lower()] = canonical

# with open("test.csv", "r") as f:
#     reader = csv.reader(f, delimiter="\t")
#     for i, line in enumerate(reader):
#         print 'line[{}] = {}'.format(i, line)

def check_text(text: str) -> bool:
    # Placeholder for actual moderation logic
    # For demonstration, let's assume any text containing "bad" is not ok
    # words = sentence.split()
    # word_count = len(words)
    text = normalize_lookalikes(text.lower())
    if (len(text.split()) == 1):
        return one_word(text)
    else:
        return sentence(text)
    return True


def normalize_lookalikes(text: str) -> str:
    return "".join(LOOKALIKE_TO_CANON.get(char.lower(), char.lower()) for char in text)

def one_word(text: str) -> bool:
    with open(SINGLE_WORD, "r") as f:
        reader = csv.reader(f, delimiter=",")
        for i, line in enumerate(reader):
            # print('line[{}] = {}'.format(i, line))
            if len(line) < 2:
                continue
            word = normalize_lookalikes(line[1].strip().lower())
            score = line[0].strip()
            # print("Score: ", score)
            if (word == text):
                if (int(scoring(word, score)) >= 5):
                    return False
    return True

def sentence(text) -> bool:
    preprocessing(text)
    return Decision()

def preprocessing(text):
    '''
    This is the first step in parsing the word/sentence
    Removing white space, ponctuation and lowercasing the word.
    the end result should be a clear sentence. 
    '''
    translator = str.maketrans('', '', string.punctuation)
    # Apply the translation table to the sentence
    words = text.translate(translator).split()
    tokenize(words)
    # =========================
    # Step 1 — Load Dataset
    # =========================
    # pd.set_option("display.max_colwidth", None)
    # df = pd.read_csv(DATA_PATH)

    

def tokenize(words: list):
    bigrams = []
    for i in range(len(words)):
        if i < len(words) - 1:
            bigrams.append(words[i] + " " + words[i + 1])


    '''
    Split the sentence into words, will use that to better pair those words with the preprocessed data
    and decide the result
    '''
    feature_extraction(bigrams)

def feature_extraction(bigrams):
    # Load the dataset
    df = pd.read_csv(DATA_PATH)

    # Create binary label: 1 if offensive or hate speech (class 0 or 1), 0 if neither (class 2)
    df['label'] = (df['class'] != 2).astype(int)

    # Extract only tweet and label columns
    df_subset = df[['tweet', 'label']].copy()

    # Clean tweets function
    def clean_tweet(text):
        # Remove usernames (@username)
        text = re.sub(r'@\w+', '', text)
        # Remove URLs
        text = re.sub(r'http\S+', '', text)
        # Remove HTML entities
        text = re.sub(r'&#?\w+;', '', text)
        # Remove punctuation and special characters
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Remove retweets (text starting with "rt")
        if text.startswith('RT '):
            text = ''
        text = text.lower()
        return text
    
    # Apply cleaning to tweets
    df_subset['tweet'] = df_subset['tweet'].apply(clean_tweet)
    
    # Display the cleaned data with labels
    X = df_subset["tweet"]
    y = df["label"]


    X_train
    X_test
    y_train
    y_test
    
    return df_subset



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
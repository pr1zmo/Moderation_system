import csv
import string
import pandas as pd
import pickle
import re
import os
from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import SGDClassifier
# from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from .append_file import append_file_contents

# SGDClassifier and HashingVectorizer

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

# DATA_PATH = "data/labeled_data.csv"
DATA_DIR = "/goinfre/zelbassa/data"
DATA_PATH_1 = f"{DATA_DIR}/train-1.csv"
DATA_PATH_2 = f"{DATA_DIR}/train-2.csv"
TEST_PATH = f"{DATA_DIR}/test-1.csv"
VALIDATION_PATH = f"{DATA_DIR}/validation-1.csv"
TRAIN_FILES = [DATA_PATH_1, DATA_PATH_2]
SINGLE_WORD = "data/single_word.csv"
PREPROCESSED = "data/preprocessed_data.csv"
FEEDBACK = "data/feedback.csv"
TOXICITY_THRESHOLD = 0.5

LOOKALIKE_TO_CANON = {}
for canonical, variations in LOOKALIKE_GROUPS.items():
	LOOKALIKE_TO_CANON[canonical] = canonical
	for variation in variations:
		LOOKALIKE_TO_CANON[variation.lower()] = canonical

# with open("test.csv", "r") as f:
#     reader = csv.reader(f, delimiter="\t")
#     for i, line in enumerate(reader):
#         print 'line[{}] = {}'.format(i, line)

def write_toFeedback(text: str, label: str, feedback_file: str):
	file_exists = os.path.exists(feedback_file)
	with open(feedback_file, "a+", newline="", encoding="utf-8") as f:
		f.seek(0)  # Move file pointer to beginning to read existing content
		reader = csv.reader(f, delimiter=",")
		for i, line in enumerate(reader):
			if text in line:
				return  # Avoid duplicate entries
		writer = csv.writer(f, delimiter=",")  # Use comma delimiter to match reader and file format
		if not file_exists:
			writer.writerow(["label", "sentence"])
		writer.writerow([label, text])

def save_feedback(text: str, original_result: str):
	"""
	Saves feedback from the UI into a CSV file for future model retraining.
	Since the user clicked "Incorrect", the true label is the opposite of original_result.
	If original_result is "ok" (Clean=0), true label is "1" (Offensive).
	If original_result is "ko" (Offensive=1), true label is "0" (Clean).
	"""
	feedback_file = FEEDBACK
	label = "1" if original_result == "ok" else "0"
	
	write_toFeedback(text, label, feedback_file)

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

loaded_vectorizer = None
loaded_model = None

def get_model():
	global loaded_vectorizer, loaded_model
	if loaded_vectorizer is None or loaded_model is None:
		base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		vec_path = os.path.join(base_dir, 'vectorizer.pkl')
		model_path = os.path.join(base_dir, 'model.pkl')

		if os.path.exists(vec_path) and os.path.exists(model_path):
			with open(vec_path, 'rb') as file:
				loaded_vectorizer = pickle.load(file)
			with open(model_path, 'rb') as file:
				loaded_model = pickle.load(file)
	return loaded_vectorizer, loaded_model

def clean_tweet(text):
	text = re.sub(r'@\w+', '', text)
	text = re.sub(r'http\S+', '', text)
	text = re.sub(r'&#?\w+;', '', text)
	text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
	text = re.sub(r'\s+', ' ', text).strip()
	if text.startswith('RT '):
		text = text[3:].strip()
	text = text.lower()
	return text

def sentence(text) -> bool:
	"""
	Evaluates a full sentence using the trained LogisticRegression model.
	Returns True if the sentence is allowed (clean), False if it is blocked (offensive).
	"""
	vec, mod = get_model()
	if vec is None or mod is None:
		# If the model isn't trained yet, train it and set vec, mod
		preprocessing(text)
		vec, mod = get_model()
		# return True
		
	cleaned = clean_tweet(text)
	X_test = vec.transform([cleaned])
	prediction = mod.predict(X_test)[0]
	if prediction == 0:
		print("Into the prediction")
		for word in cleaned.split():
			if not one_word(word):
				# print("Found clean word in sentence, allowing: ", word)
				# print("Original sentence: ", text)
				write_toFeedback(cleaned, "1", FEEDBACK)
				return False

	with open(FEEDBACK, "r") as f:
		feedback_lines = f.readlines()
		if len(feedback_lines) > 6:  # Header + 5 feedback entries
			new_prediction = retrain(text)
			append_file_contents(FEEDBACK, DATA_PATH_1)
			# Clear feedback except header
			with open(FEEDBACK, "w") as f_clear:
				f_clear.write(feedback_lines[0])  # Keep header only
			return new_prediction == 0
	return prediction == 0

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
	feature_extraction(bigrams, words)

def train_model_incremental():
	"""
	Train an SGDClassifier with HashingVectorizer incrementally
	on the large CSV files using chunked reading.
	"""
	import numpy as np

	vectorizer = HashingVectorizer(
		n_features=2**18,
		ngram_range=(1, 2),
		alternate_sign=False,
	)
	model = SGDClassifier(
		loss='log_loss',
		random_state=42,
	)

	classes = [0, 1]  # binary: clean vs toxic
	CHUNK_SIZE = 10_000
	# Moderate weight boost for the minority (toxic) class.
	# The dataset is ~93% clean / ~7% toxic.  'balanced' gives ~14x
	# which causes massive over-prediction of toxic.  3x is enough to
	# let the model learn toxic patterns without drowning out clean ones.
	TOXIC_WEIGHT = 3.0
	weight_map = {0: 1.0, 1: TOXIC_WEIGHT}

	for csv_path in TRAIN_FILES:
		if not os.path.exists(csv_path):
			print(f"Warning: {csv_path} not found, skipping.")
			continue
		print(f"Training on {csv_path} ...")
		for chunk in pd.read_csv(csv_path, chunksize=CHUNK_SIZE):
			if 'text' not in chunk.columns:
				print(f"  Skipping chunk — no 'text' column found.")
				continue
			chunk = chunk.dropna(subset=['text'])
			if chunk.empty:
				continue

			# Build binary label: toxic if any score >= threshold
			score_cols = [c for c in chunk.columns if c != 'text']
			chunk['label'] = (chunk[score_cols].max(axis=1) >= TOXICITY_THRESHOLD).astype(int)

			X_raw = chunk['text'].apply(clean_tweet)
			y = chunk['label']

			sample_weights = np.array([weight_map[label] for label in y])

			X_vec = vectorizer.transform(X_raw)
			model.partial_fit(X_vec, y, classes=classes, sample_weight=sample_weights)

	print("Training complete.")

	# Evaluate on test set
	if os.path.exists(TEST_PATH):
		print("Evaluating on test set ...")
		y_true_all, y_pred_all = [], []
		for chunk in pd.read_csv(TEST_PATH, chunksize=CHUNK_SIZE):
			if 'text' not in chunk.columns:
				continue
			chunk = chunk.dropna(subset=['text'])
			if chunk.empty:
				continue
			score_cols = [c for c in chunk.columns if c != 'text']
			chunk['label'] = (chunk[score_cols].max(axis=1) >= TOXICITY_THRESHOLD).astype(int)
			X_vec = vectorizer.transform(chunk['text'].apply(clean_tweet))
			y_true_all.extend(chunk['label'].tolist())
			y_pred_all.extend(model.predict(X_vec).tolist())
		if y_true_all:
			y_true = np.array(y_true_all)
			y_pred = np.array(y_pred_all)
			accuracy = np.mean(y_true == y_pred) * 100
			# Per-class metrics
			tp = np.sum((y_pred == 1) & (y_true == 1))
			fp = np.sum((y_pred == 1) & (y_true == 0))
			fn = np.sum((y_pred == 0) & (y_true == 1))
			precision = tp / (tp + fp) if (tp + fp) > 0 else 0
			recall = tp / (tp + fn) if (tp + fn) > 0 else 0
			f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
			print(f"Test accuracy: {accuracy:.2f}%")
			print(f"Toxic precision: {precision:.4f}  recall: {recall:.4f}  F1: {f1:.4f}")
			print(f"  (TP={tp}, FP={fp}, FN={fn})")

	# Save model and vectorizer
	base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	with open(os.path.join(base_dir, 'vectorizer.pkl'), 'wb') as file:
		pickle.dump(vectorizer, file)
		print("Vectorizer saved successfully!")
	with open(os.path.join(base_dir, 'model.pkl'), 'wb') as file:
		pickle.dump(model, file)
		print("Model saved successfully!")

	return model

def feature_extraction(bigrams, words):
	"""
	Trains the model from the new data files and saves the artifacts.
	"""
	train_model_incremental()

'''
# Source - https://stackoverflow.com/a/8858026
# Posted by ig0774, modified by community. See post 'Timeline' for change history
# Retrieved 2026-03-04, License - CC BY-SA 4.0

import os
import shutil

os.rename("path/to/current/file.foo", "path/to/new/destination/for/file.foo")
os.replace("path/to/current/file.foo", "path/to/new/destination/for/file.foo")
shutil.move("path/to/current/file.foo", "path/to/new/destination/for/file.foo")

'''

def retrain(text):
	print("Retraining")
	os.rename("model.pkl", "model-v2.pkl")
	os.rename("vectorizer.pkl", "vectorizer-v2.pkl")

	preprocessing(text)
	vec, mod = get_model()
		
	cleaned = clean_tweet(text)
	X_test = vec.transform([cleaned])
	prediction = mod.predict(X_test)[0]
	return prediction


def scoring(text: str, score: int) -> int:
	return score

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
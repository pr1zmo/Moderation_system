import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
# from sklearn import *
# import sklearn

# Load the data
df = pd.read_csv('data/labeled_data.csv')

print(df.head())

# Prepare features (X) and labels (y)
X = df['tweet']  # Tweet text
y = df['class']  # 0=hate, 1=offensive, 2=neither

# Split data for training/testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Convert text to numerical features
vectorizer = TfidfVectorizer(max_features=5000)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train a classifier
classifier = MultinomialNB()
classifier.fit(X_train_vec, y_train)

# Moderate new user input
def moderate_text(user_input):
    input_vec = vectorizer.transform([user_input])
    prediction = classifier.predict(input_vec)[0]
    
    if prediction == 0:
        return "REJECT: Hate speech detected"
    elif prediction == 1:
        return "WARN: Offensive language detected"
    else:
        return "APPROVE: Content is clean"

# Test it
print(moderate_text("I love You!"))
print(moderate_text("As a woman you shouldn't..."))
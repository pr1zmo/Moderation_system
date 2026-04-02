Perfect request. You should treat this as a small refactor in check.py plus one behavior change in explain.py.

## What changes conceptually

1. `HashingVectorizer` is stateless, so there is no `fit()` and no vectorizer.pkl requirement.
2. `SGDClassifier` becomes the only trained artifact you save/load (for example model.pkl).
3. Your training pipeline should read explicit train/test/validation CSVs from data, not the old single dataset path.
4. Your current explanation logic in explain.py relies on feature names. That breaks with hashing.

## Step-by-step migration plan

1. Fix your dataset paths first.
- In check.py, replace the current `DATA_PATH` constants with real file paths under data (for example `train.csv`, `test.csv`, `validation.csv`).
- Use `pathlib.Path` + repo-relative paths so deployment works everywhere.

2. Replace old training code with an SGD + Hashing training function.
- Keep your `clean_tweet()` preprocessing.
- Build vectorizer once with fixed config.
- Train `SGDClassifier` on transformed train set.
- Evaluate on test and validation sets.
- Save only the model.

Template:

```python
from pathlib import Path
import pandas as pd
import pickle
from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.metrics import classification_report, accuracy_score

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
TRAIN_PATH = DATA_DIR / "train.csv"
TEST_PATH = DATA_DIR / "test.csv"
VAL_PATH = DATA_DIR / "validation.csv"
MODEL_PATH = BASE_DIR / "model.pkl"

def load_split(path):
    df = pd.read_csv(path)
    # adjust column names to your files
    # expected: sentence/tweet text + binary label
    X = df["sentence"].astype(str).map(clean_tweet)
    y = df["label"].astype(int)
    return X, y

def train_sgd_hashing():
    X_train, y_train = load_split(TRAIN_PATH)
    X_test, y_test = load_split(TEST_PATH)
    X_val, y_val = load_split(VAL_PATH)

    vec = HashingVectorizer(
        n_features=2**20,
        alternate_sign=False,
        ngram_range=(1, 2),
        norm="l2"
    )

    X_train_h = vec.transform(X_train)
    X_test_h = vec.transform(X_test)
    X_val_h = vec.transform(X_val)

    model = SGDClassifier(
        loss="log_loss",
        class_weight="balanced",
        random_state=42,
        max_iter=2000,
        tol=1e-3
    )
    model.fit(X_train_h, y_train)

    print("TEST accuracy:", accuracy_score(y_test, model.predict(X_test_h)))
    print("VAL accuracy:", accuracy_score(y_val, model.predict(X_val_h)))
    print(classification_report(y_val, model.predict(X_val_h)))

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
```

3. Update model loading for inference.
- In check.py, `get_model()` should create a `HashingVectorizer(...)` in code and load only model.pkl.
- Return `(vec, model)` as before so your `sentence()` call pattern stays similar.

4. Update prediction flow.
- In `sentence(text)`, keep:
  - `cleaned = clean_tweet(text)`
  - `X_test = vec.transform([cleaned])`
  - `prediction = mod.predict(X_test)[0]`

5. Replace retraining entrypoint.
- Your current `preprocessing()` currently routes to old training path and references `TfidfVectorizer`/`LogisticRegression`.
- Point retraining to `train_sgd_hashing()` instead.
- Remove vectorizer.pkl rename/save logic, since hashing vectorizer isn’t persisted.

6. Adjust explanation behavior.
- In explain.py, this line of approach will fail with hashing:
  - `feature_names = vec.get_feature_names_out()`
- With hashing, you have no direct token names from indices.
- Options:
  1. Keep only high-level probability explanation for sentence mode.
  2. Switch explanation path to a second explainable model/vectorizer (for diagnostics only).
  3. Keep `TfidfVectorizer` only for explanation, SGD+Hashing for production prediction.

## How to wire your new data folder safely

Because you said new train/test/validation files will replace data:
- Keep fixed expected filenames in code.
- Validate at startup:

```python
for p in [TRAIN_PATH, TEST_PATH, VAL_PATH]:
    if not p.exists():
        raise FileNotFoundError(f"Missing dataset: {p}")
```

- Validate columns once before training:
  - text column exists
  - label column exists
  - labels are binary integers

## What to remove from current code

In check.py, remove old/unused pieces once migrated:
- `logistic_regression(...)`
- Any `TfidfVectorizer` and `LogisticRegression` references
- vectorizer.pkl save/load/rename logic
- Old single-file dataset assumption (`DATA_PATH` with one CSV)

## Quick verification checklist

1. Train function runs end-to-end with new files in data.
2. model.pkl is produced.
3. Flask `POST /moderate` still returns `ok`/`ko`.
4. First request on cold start loads model without errors.
5. explain.py no longer tries `get_feature_names_out()` on hashing vectorizer.

If you want, next I can review your updated check.py and explain.py and give you a targeted “what’s correct / what will break” pass without editing anything.
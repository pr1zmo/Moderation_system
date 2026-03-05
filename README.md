# Automated Content Moderation System

Welcome to my Automated Content Moderation System! This is a personal project I built to explore Natural Language Processing (NLP) and how machine learning can be used to automatically detect and filter out inappropriate, hateful, or offensive text.

## How It Works Under the Hood

### 1. Data Cleaning
Real-world text is messy. Before the model can learn anything, I have to clean the raw data. This pipeline involves:
* Stripping out URLs, special characters, and punctuation.
* Converting all text to lowercase to ensure uniformity.
* Removing "stop words" (common, uninformative words like "the", "a", "is").
* Applying stemming or lemmatization to reduce words to their root or base forms (e.g., converting "running", "runs" -> "run").
This critical step removes noise and distills the text down to its most meaningful components.

### 2. Vectorization (The Math)
Machine learning models require numbers, not strings. To bridge this gap, I map the cleaned text into a multidimensional mathematical space using vectorization techniques (like TF-IDF or Word Embeddings). 

In this high-dimensional vector space $\mathbb{R}^n$, every document or word is represented as a mathematical vector $\mathbf{v}$. This allows the system to analyze the semantic meaning of text by measuring the angles and distances between vectors. For example, the system can determine how closely related two sentences are by calculating their cosine similarity:

$$ \cos(\theta) = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|} $$

Through this vector mapping, text relationships become quantifiable, algebraic properties.

### 3. Model Training
Once the text is vectorized, I use the data to train the classification models. The algorithm's objective is to find an optimal decision boundary (a hyperplane) in that $n$-dimensional space that distinctly separates "safe" text vectors from "offensive" text vectors. During training, the model iteratively adjusts its internal weights to minimize a loss function (such as Cross-Entropy Loss), continually improving its predictive accuracy against the labeled dataset.

### 4. Web Interface
To make the project interactive and easy to showcase, I wrapped the moderation logic in a Flask web application. When text is submitted through the UI, it goes through the exact same data cleaning and vectorization pipeline in real-time before the trained model outputs a safety prediction.

## How to Run It

### 1. Prerequisites
Make sure you have Python installed. It is highly recommended to set up and use a virtual environment.

### 2. Install Dependencies
Install all the required packages to run the system:
```bash
pip install -r requirements.txt
```

### 3. Run the Application
You can start the main program by running:
```bash
python main.py
```

### 4. Head to the Web Interface
Open your web browser and navigate to `http://localhost:5000`. You will see a simple interface where you can input text and get an instant prediction on whether it is safe or offensive.

*The model learns from your feedback! If you click on the "Incorrect" button for any text, it will be added to the training dataset, allowing the system to improve over time.*
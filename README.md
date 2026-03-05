# Automated Content Moderation System

Welcome to the Automated Content Moderation System! This project is designed to help detect and filter out inappropriate, hateful, or offensive text content automatically.

## Concepts (Surface Level)

At its core, this system uses **Machine Learning (AI)** to function:
* **The "Brain" (AI Models):** We use trained algorithms to read and understand text. Just like a human learns what words might be offensive, our models are trained on large amounts of provided data to spot bad behavior.
* **Data Processing:** Before the AI can read the text, we clean it up and standardize it so the system can understand it easily.
* **Moderation Logic:** The system applies specific checks against submitted text to determine its safety score and whether it should be flagged.
* **Web Interface:** We include a web-based interface (using Flask) where users can submit text and interact with the moderation logic in real-time.

## How to Run It

### 1. Prerequisites
Make sure you have Python installed. It is highly recommended to use a virtual environment.

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
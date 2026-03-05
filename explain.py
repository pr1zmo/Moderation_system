import numpy as np
from logic.check import *

def explain_decision(text: str):
    """
    Explains which words contributed most to the model's decision.
    """
    vec, mod = get_model()
    if vec is None or mod is None:
        print("Model not loaded.")
        return

    cleaned = clean_tweet(text)
    
    # Transform the text into features
    X_test = vec.transform([cleaned])
    
    # Get the feature names (vocabulary) and the model coefficients
    feature_names = vec.get_feature_names_out()
    coefs = mod.coef_[0]
    
    # Find the non-zero features in the input text
    non_zero_indices = X_test[0].nonzero()[1]
    
    print(f"\nAnalyzing text: '{cleaned}'")
    print("-" * 40)
    
    contributions = []
    for idx in non_zero_indices:
        word = feature_names[idx]
        tfidf_value = X_test[0, idx]
        weight = coefs[idx]
        contribution = tfidf_value * weight
        contributions.append((word, contribution))
    
    # Sort contributions by their impact (positive values -> offensive, negative -> clean)
    contributions.sort(key=lambda x: x[1], reverse=True)
    
    print("Words pushing towards OFFENSIVE (Blocked):")
    for word, contrib in contributions:
        if contrib > 0:
            print(f"  {word}: +{contrib:.4f}")
            
    print("\nWords pushing towards CLEAN (Allowed):")
    for word, contrib in reversed(contributions):
        if contrib < 0:
            print(f"  {word}: {contrib:.4f}")
            
    prediction = mod.predict(X_test)[0]
    print(f"\nFinal Prediction: {'Offensive (0)' if prediction == 1 else 'Clean (1)'}")

explain_decision("youfuckingnigger")
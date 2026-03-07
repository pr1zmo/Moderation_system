import csv
from logic.check import SINGLE_WORD, clean_tweet, get_model, normalize_lookalikes, scoring


def _format_contribution(term: str, score: float) -> dict:
    return {
        "term": term,
        "score": round(float(score), 4),
    }


def _single_word_explanation(text: str) -> dict:
    normalized = normalize_lookalikes(text.lower()).strip()

    with open(SINGLE_WORD, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=",")
        for line in reader:
            if len(line) < 2:
                continue

            word = normalize_lookalikes(line[1].strip().lower())
            if word != normalized:
                continue

            score = int(scoring(word, line[0].strip()))
            flagged = score >= 5

            return {
                "mode": "single_word",
                "cleaned_text": normalized,
                "summary": (
                    f"The single-word filter matched '{word}' with severity score {score}, which exceeds the block threshold."
                    if flagged
                    else f"The single-word filter matched '{word}' with severity score {score}, which stays below the block threshold."
                ),
                "flagged_terms": [_format_contribution(word, score)] if flagged else [],
                "allowed_terms": [_format_contribution(word, score)] if not flagged else [],
                "decision_basis": "dictionary",
            }

    return {
        "mode": "single_word",
        "cleaned_text": normalized,
        "summary": "No single-word rule matched this input, so it was evaluated without dictionary evidence.",
        "flagged_terms": [],
        "allowed_terms": [],
        "decision_basis": "dictionary",
    }


def _sentence_explanation(text: str) -> dict:
    vec, mod = get_model()
    cleaned = clean_tweet(text)

    if vec is None or mod is None:
        return {
            "mode": "sentence",
            "cleaned_text": cleaned,
            "summary": "The model is not loaded yet, so detailed feature contributions are unavailable.",
            "flagged_terms": [],
            "allowed_terms": [],
            "decision_basis": "model_unavailable",
        }

    transformed = vec.transform([cleaned])
    feature_names = vec.get_feature_names_out()
    coefficients = mod.coef_[0]
    non_zero_indices = transformed[0].nonzero()[1]

    contributions = []
    for index in non_zero_indices:
        term = feature_names[index]
        tfidf_value = transformed[0, index]
        weight = coefficients[index]
        contribution = float(tfidf_value * weight)
        contributions.append((term, contribution))

    contributions.sort(key=lambda item: item[1], reverse=True)

    flagged_terms = [_format_contribution(term, score) for term, score in contributions if score > 0][:5]
    allowed_terms = [_format_contribution(term, score) for term, score in sorted(contributions, key=lambda item: item[1]) if score < 0][:5]

    prediction = mod.predict(transformed)[0]
    summary = (
        "The model found stronger offensive-weighted terms in the sentence."
        if prediction == 1
        else "The model found stronger clean-weighted terms in the sentence."
    )

    if not flagged_terms and not allowed_terms:
        summary = "The model classified the sentence, but no individual weighted terms were exposed for this exact input."

    return {
        "mode": "sentence",
        "cleaned_text": cleaned,
        "summary": summary,
        "flagged_terms": flagged_terms,
        "allowed_terms": allowed_terms,
        "decision_basis": "model",
    }


def explain_decision(text: str) -> dict:
    """Return structured explanation data for the moderation decision."""
    normalized = normalize_lookalikes(text.lower()).strip()
    if len(normalized.split()) == 1:
        return _single_word_explanation(normalized)
    return _sentence_explanation(normalized)
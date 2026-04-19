const form = document.getElementById('moderationForm');
const resultDiv = document.getElementById('result');
const resultPanel = document.getElementById('result-panel');
const resultState = document.getElementById('result-state');
const resultCopy = document.getElementById('result-copy');
const explanationBox = document.getElementById('explanation-box');
const explanationMode = document.getElementById('explanation-mode');
const explanationSummary = document.getElementById('explanation-summary');
const flaggedTerms = document.getElementById('flagged-terms');
const allowedTerms = document.getElementById('allowed-terms');
const watermark = document.getElementById('bg-watermark');
const watermarkText = watermark.querySelector('.watermark-text');
const feedbackBtn = document.getElementById('feedback-btn');
const feedbackMsg = document.getElementById('feedback-msg');
const submitBtn = document.getElementById('submit-btn');

let lastInput = '';
let lastResult = '';

function renderTerms(container, terms, variant) {
    container.innerHTML = '';

    if (!terms || terms.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'empty-terms';
        empty.textContent = 'No strong term-level signals were available for this side of the decision.';
        container.appendChild(empty);
        return;
    }

    terms.forEach((item) => {
        const chip = document.createElement('div');
        chip.className = `term-chip ${variant}`;
        chip.innerHTML = `<span>${item.term}</span><span class="term-score">${item.score}</span>`;
        container.appendChild(chip);
    });
}

function showExplanation(explanation) {
    if (!explanation) {
        explanationBox.style.display = 'none';
        return;
    }

    explanationMode.textContent = (explanation.mode || 'analysis').replace('_', ' ');
    explanationSummary.textContent = explanation.summary || 'No explanation is currently available.';
    renderTerms(flaggedTerms, explanation.flagged_terms, 'flagged');
    renderTerms(allowedTerms, explanation.allowed_terms, 'allowed');
    explanationBox.style.display = 'grid';
}

function showResult(result, explanation) {
    const cls = result === 'OK' ? 'ok' : 'ko';
    const copy = result === 'OK'
        ? 'This submission passed the current moderation check and appears safe under the configured rules.'
        : 'This submission was flagged by the current moderation check and may require intervention.';
    const stateText = result === 'OK' ? 'Approved' : 'Flagged';

    resultDiv.textContent = result;
    resultPanel.className = `result-panel ${cls}`;
    resultPanel.style.display = 'block';
    resultState.textContent = stateText;
    resultCopy.textContent = copy;
    showExplanation(explanation);

    resultPanel.style.animation = 'none';
    void resultPanel.offsetWidth;
    resultPanel.style.animation = 'rise-in 420ms cubic-bezier(0.22, 1, 0.36, 1) forwards';

    watermark.classList.remove('visible', 'ok', 'ko');
    watermark.style.transition = 'none';
    void watermark.offsetWidth;

    watermark.style.transition = '';
    watermarkText.textContent = result;
    watermark.classList.add(cls, 'visible');

    feedbackBtn.style.display = 'block';
    feedbackMsg.style.display = 'none';
}

function setSubmitting(isSubmitting) {
    submitBtn.classList.toggle('is-loading', isSubmitting);
    submitBtn.textContent = isSubmitting ? 'Analyzing...' : 'Analyze content';
}

form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const input = document.getElementById('inputText').value.trim();

    if (!input) {
        return;
    }

    lastInput = input;
    setSubmitting(true);

    try {
        const response = await fetch('/moderate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: input })
        });

        const data = await response.json();
        lastResult = (data.result || 'ko').toLowerCase();
        showResult(lastResult.toUpperCase(), data.explanation || null);
    } catch (error) {
        console.error('Error:', error);
        lastResult = 'ko';
        showResult('KO', null);
    } finally {
        setSubmitting(false);
    }
});

feedbackBtn.addEventListener('click', async () => {
    try {
        await fetch('/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: lastInput,
                original_result: lastResult
            })
        });

        feedbackBtn.style.display = 'none';
        feedbackMsg.style.display = 'block';
    } catch (error) {
        console.error('Error sending feedback:', error);
    }
});

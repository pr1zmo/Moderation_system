from flask import Flask, jsonify, render_template, request
from explain import explain_decision
from logic.check import check_text, save_feedback

app = Flask(__name__, template_folder="www")

@app.route("/", methods=["GET", "POST"])
def home():
    text = request.form.get("text")
    message = f"You entered: {text}" if text else "Please enter some text to moderate."
    return render_template("index.html", message=message)


@app.route("/moderate", methods=["POST"])
def moderate():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if (check_text(text)):
        result = "ok"
    else:
        result = "ko"
    explanation = explain_decision(text) if text else None
    return jsonify({"result": result, "explanation": explanation})

@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    original_result = (data.get("original_result") or "").lower()
    
    if text and original_result in ["ok", "ko"]:
        save_feedback(text, original_result)
        return jsonify({"status": "success"})
    
    return jsonify({"status": "error", "message": "Invalid input"}), 400

if __name__ == "__main__":
    app.run(debug=True)
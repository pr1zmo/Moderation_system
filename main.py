from flask import Flask, jsonify, render_template, request
from logic.check import check_text

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
    return jsonify({"result": result})

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request, jsonify
from nlp_engine import FAQChatbot

app = Flask(__name__)
bot = FAQChatbot()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"answer": "Please type a message.", "confidence": 0.0}), 400

    response_data = bot.get_response(user_message)
    return jsonify(response_data)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
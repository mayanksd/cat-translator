# app.py — Flask backend for Cat Translator
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/translate", methods=["POST"])
def translate_cat_sound():
    audio_data = request.data  # This will be raw binary audio
    print(f"Received audio data of length: {len(audio_data)} bytes")

    # 🐱 Dummy translation for now
    translation = "Your cat says: 'I am the boss of this house!'"
    return jsonify({"translation": translation})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8506)

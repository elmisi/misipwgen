#!/usr/bin/env python
"""
Simple Flask web application for misipwgen
Exposes word, phrase, and sentence generation via web interface
"""

import os
from flask import Flask, render_template, request, jsonify
from misipwgen import MisiPwGen

app = Flask(__name__)


@app.route("/")
def index():
    """Main page with generation forms"""
    return render_template("index.html")


@app.route("/api/generate/word", methods=["POST"])
def generate_word():
    """Generate a single word"""
    try:
        data = request.get_json()
        length = int(data.get("length", 7))
        language = data.get("language", "it")

        # Validate inputs
        if length < 1 or length > 50:
            return jsonify({"error": "Length must be between 1 and 50"}), 400
        if language not in ["it", "es"]:
            return jsonify({"error": "Language must be 'it' or 'es'"}), 400

        pwg = MisiPwGen.from_language(language)
        word = pwg.generate_word(length)

        return jsonify({"result": word, "type": "word", "language": language})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate/phrase", methods=["POST"])
def generate_phrase():
    """Generate a phrase with multiple words"""
    try:
        data = request.get_json()
        word_lengths = data.get("word_lengths", [5, 5, 5])
        separator = data.get("separator", "_")
        language = data.get("language", "it")

        # Validate inputs
        if not word_lengths or len(word_lengths) > 10:
            return jsonify({"error": "Provide 1-10 word lengths"}), 400
        if any(l < 1 or l > 50 for l in word_lengths):
            return jsonify({"error": "Each word length must be between 1 and 50"}), 400
        if language not in ["it", "es"]:
            return jsonify({"error": "Language must be 'it' or 'es'"}), 400

        pwg = MisiPwGen.from_language(language)
        phrase = pwg.phrase(*word_lengths, sep=separator)

        return jsonify({
            "result": phrase,
            "type": "phrase",
            "language": language,
            "word_count": len(word_lengths)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate/sentence", methods=["POST"])
def generate_sentence():
    """Generate a sentence with automatic word splitting"""
    try:
        data = request.get_json()
        total_length = int(data.get("total_length", 24))
        separator = data.get("separator", "_")
        language = data.get("language", "it")

        # Validate inputs
        if total_length < 1 or total_length > 100:
            return jsonify({"error": "Total length must be between 1 and 100"}), 400
        if language not in ["it", "es"]:
            return jsonify({"error": "Language must be 'it' or 'es'"}), 400

        pwg = MisiPwGen.from_language(language)
        sentence = pwg.sentence(total_length, sep=separator)

        return jsonify({
            "result": sentence,
            "type": "sentence",
            "language": language,
            "total_length": total_length
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # For local development
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "True").lower() == "true"
    app.run(debug=debug, host="0.0.0.0", port=port)

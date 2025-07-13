from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import sqlite3
import os

app = Flask(__name__)

# 🔑 Gemini API Key
genai.configure(api_key="AIzaSyCMvzkhnTxRL5F8GueLqr-FUor0g5StBu0+")  # ← Replace this with your actual key

# ⚙️ Gemini Model Settings
generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

# 🚀 Load Gemini Model
model = genai.GenerativeModel(
    model_name="models/gemini-1.5-flash-latest",
    generation_config=generation_config
)

# 🛠️ Create SQLite DB for notes (if not exists)
if not os.path.exists("notes.db"):
    conn = sqlite3.connect("notes.db")
    conn.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT)")
    conn.close()

# ----------------- ROUTES -------------------

@app.route('/')
def landing():
    return render_template('home.html')

@app.route('/chat')
def chat():
    return render_template('index.html')

@app.route('/timer')
def timer():
    return render_template('timer.html')

@app.route('/voice')
def voice():
    return render_template('voice.html')

@app.route('/notes')
def notes():
    return render_template('notes.html')

@app.route('/stats')
def stats():
    return render_template('stats.html')

# 🔁 AI Response Route
@app.route('/get', methods=['POST'])
def chatbot_response():
    user_message = request.json['message']

    prompt = f"""
You are StudyBuddy — a friendly, funny, and motivating AI best friend for students.

🎯 Your goals:
- Help students study with focus and joy
- Solve their subject doubts with clear and simple explanations
- Gently guide them away from distractions like social media
- Motivate them when they feel low or lazy
- Use humor and jokes occasionally to make them smile 😄
- Act like a mix of a best friend + a wise mentor
- Be strict only when absolutely necessary

Here is what the student said: {user_message}
"""

    try:
        response = model.generate_content(prompt)
        return jsonify({'reply': response.text.strip()})
    except Exception as e:
        return jsonify({'reply': f"Oops! Error: {str(e)}"})

# 📤 Save Note to SQLite
@app.route('/save_note', methods=['POST'])
def save_note():
    data = request.get_json()
    note_content = data.get("note", "")
    try:
        conn = sqlite3.connect("notes.db")
        conn.execute("INSERT INTO notes (content) VALUES (?)", (note_content,))
        conn.commit()
        conn.close()
        return jsonify({"message": "✅ Note saved to server!"})
    except Exception as e:
        return jsonify({"message": f"❌ Failed to save: {str(e)}"})

# ----------------- RUN APP -------------------

if __name__ == '__main__':
    import os

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
@app.route('/view_notes')
def view_notes():
    try:
        conn = sqlite3.connect("notes.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, content FROM notes ORDER BY id DESC")
        notes = cursor.fetchall()
        conn.close()
        return render_template("view_notes.html", notes=notes)
    except Exception as e:
        return f"Failed to load notes: {e}"

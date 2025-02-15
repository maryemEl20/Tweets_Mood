from flask import Flask, render_template, request
import joblib
import sqlite3
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime
import matplotlib.dates as mdates

app = Flask(__name__)
app.secret_key = "secret_key"

# Charger le modèle et le vectorizer
model = joblib.load('model/svm_model.pkl')
vectorizer = joblib.load('model/vectorizer.pkl')

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS sentiments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        text TEXT,
                        prediction TEXT,
                        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        session_id TEXT)''')  # Correction de la faute de frappe
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        text = request.form['text']
        text_vec = vectorizer.transform([text])
        prediction = model.predict(text_vec)
        sentiment = "Positif 🙂" if prediction[0] == 'Positive' else "Négatif 😡" if prediction[0] == 'Negative' else "Neutre 😐"

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sentiments (text, prediction) VALUES (?, ?)", (text, prediction[0]))
        conn.commit()
        conn.close()
        
        return render_template('index.html', prediction_text=f'Sentiment: {sentiment}')

def create_graph(dates_str, y, title, color):
    dates = [datetime.strptime(d, '%Y-%m-%d %H:%M:%S') for d in dates_str]
    fig, ax = plt.subplots()
    ax.plot(dates, y, marker='o', linestyle='-', color=color)
    ax.set_title(title)
    ax.set_xlabel("Temps")
    ax.set_ylabel("Nombre de Messages")
    
    # Formatage des dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    img = BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plt.close(fig)
    return base64.b64encode(img.getvalue()).decode('utf-8')

@app.route('/stats')
def stats():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT date, prediction FROM sentiments ORDER BY date")
    sentiment_data = cursor.fetchall()
    conn.close()

    if not sentiment_data:
        return render_template('stats.html', message="Aucun message enregistré.")

    dates, positives, neutrals, negatives = [], [], [], []
    pos_count = neu_count = neg_count = 0

    for date, sentiment in sentiment_data:
        dates.append(date)
        if sentiment == 'Positive':
            pos_count += 1
        elif sentiment == 'Neutral':
            neu_count += 1
        elif sentiment == 'Negative':
            neg_count += 1
        positives.append(pos_count)
        neutrals.append(neu_count)
        negatives.append(neg_count)
    
    img_pos = create_graph(dates, positives, "Évolution des Positifs", "green")
    img_neu = create_graph(dates, neutrals, "Évolution des Neutres", "gray")
    img_neg = create_graph(dates, negatives, "Évolution des Négatifs", "red")
    
    return render_template('stats.html', img_pos=img_pos, img_neu=img_neu, img_neg=img_neg)

if __name__ == "__main__":
    app.run(debug=True)
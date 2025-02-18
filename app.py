from flask import Flask, render_template, request
import joblib
import sqlite3
from io import BytesIO
import base64
from datetime import datetime
import matplotlib.dates as mdates

import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = "secret_key"

# Load the model and vectorizer
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
                        session_id TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        text = request.form['text']
        text_vec = vectorizer.transform([text])
        prediction = model.predict(text_vec)

        if prediction[0] == 'Positive':
            sentiment = "Positive </br> <img src='/static/images/happy.png' alt='Positif' width='40' height='40'>"
        elif prediction[0] == 'Negative':
            sentiment = "Negative </br> <img src='/static/images/angry.png' alt='Négatif' width='40' height='40'>"
        else:
            sentiment = "Neutral </br> <img src='/static/images/neutral.png' alt='Neutre' width='40' height='40'>"

        # Create the message with sentiment
        message_with_sentiment = f"{text} : {sentiment}"

        # Save to the database
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sentiments (text, prediction) VALUES (?, ?)", (text, prediction[0]))
        conn.commit()
        conn.close()

        # Pass the message and sentiment to the template
        return render_template('how_it_works.html', prediction_text=message_with_sentiment)

def create_graph(dates_str, y, title, color):
    dates = [datetime.strptime(d, '%Y-%m-%d %H:%M:%S') for d in dates_str]
    fig, ax = plt.subplots()
    ax.plot(dates, y, marker='o', linestyle='-', color=color)
    ax.set_title(title)
    ax.set_xlabel("Temps")
    ax.set_ylabel("Nombre de Messages")
    
    # Format dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    img = BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plt.close(fig)  # Close the figure to free memory
    return base64.b64encode(img.getvalue()).decode('utf-8')

@app.route('/stats')
def stats():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT date, prediction FROM sentiments WHERE date >= datetime('now', '-1 hour') ORDER BY date;")    
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
    img_neu = create_graph(dates, neutrals, "Évolution des Neutres", "yellow")
    img_neg = create_graph(dates, negatives, "Évolution des Négatifs", "red")
    
    return render_template('stats.html', img_pos=img_pos, img_neu=img_neu, img_neg=img_neg)

if __name__ == "__main__":
    app.run(debug=True, port=8080)  # Use a different port

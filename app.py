from flask import Flask, render_template, request
import joblib
import sqlite3
from io import BytesIO
import base64
from datetime import datetime
import matplotlib.dates as mdates

import matplotlib
matplotlib.use('Agg')  # Utiliser un backend non interactif
import matplotlib.pyplot as plt

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
<<<<<<< HEAD

        # Debug - Afficher le texte et la prédiction
        print(f"Text: {text} | Sentiment: {prediction[0]}")

        if prediction[0] == 'Positive':
            sentiment = "Positif </br> <img src='/static/images/happy.png' alt='Positif' width='40' height='40'>"
        elif prediction[0] == 'Negative':
            sentiment = "Negative </br> <img src='/static/images/angry.png' alt='Négatif' width='40' height='40'>"
        else:
            sentiment = "Neutral </br> <img src='/static/images/neutral.png' alt='Neutre' width='40' height='40'>"

        # Créer le message
        message_with_sentiment = f"{text} : {sentiment}"
=======

        # Debug - Afficher le texte et la prédiction
        print(f"Text: {text} | Sentiment: {prediction[0]}")

        if prediction[0] == 'Positive':
            sentiment = "Positif <img src='/static/images/happy.png' alt='Positif' width='30' height='30'>"
        elif prediction[0] == 'Negative':
            sentiment = "Negatif <img src='/static/images/angry.png' alt='Négatif' width='30' height='30'>"
        else:
            sentiment = "neutral <img src='/static/images/neutral.png' alt='Neutre' width='30' height='30'>"

        # Créer le message
        message_with_sentiment = f"Message: {text} - Sentiment: {sentiment}"

        # Debug - Afficher ce qui sera envoyé au template
        print(f"Message with sentiment: {message_with_sentiment}")
>>>>>>> ef075006b025a1af406f6ea4dae18834e0589002

        # Sauvegarder dans la base de données
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sentiments (text, prediction) VALUES (?, ?)", (text, prediction[0]))
        conn.commit()
        conn.close()
<<<<<<< HEAD

        # Passer le message et le sentiment au template
        return render_template('how_it_works.html', prediction_text=message_with_sentiment)  # Renvoie le message complet
=======
<<<<<<< HEAD

        # Passer le message et le sentiment au template
        return render_template('index.html', prediction_text=message_with_sentiment)  # Renvoie le message complet

=======
        
        return render_template('how_it_works.html', prediction_text=f'Sentiment: {sentiment}')
    else:
        return "Méthode non autorisée", 405  # Retourne une erreur 405 si la méthode n'est pas POST
>>>>>>> ef075006b025a1af406f6ea4dae18834e0589002
    
    
>>>>>>> c0ba539d2e7e60a49231e2d7eb78c7aef718b323
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
    plt.close(fig)  # Fermer la figure pour libérer la mémoire
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
    app.run(debug=True, port=8080)  # Utilisez un port différent
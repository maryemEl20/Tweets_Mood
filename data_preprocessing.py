import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import svm
import nltk
from nltk.corpus import stopwords
import string
import joblib
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import re

nltk.download('stopwords')

def clean_text(text):
    text = text.lower()  # Mettre en minuscule
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)  # Supprimer les liens
    text = re.sub(r'\@\w+|\#','', text)  # Supprimer les mentions et hashtags
    text = re.sub(r'\d+', '', text)  # Supprimer les chiffres
    return text

def load_data(filepath):
    # Charger les données
    data = pd.read_csv(filepath)
    return data

def preprocess_data(data):
    # Supprimer les lignes où la colonne 'tweet' est manquante ou NaN
    data = data.dropna(subset=['tweet']).copy()  # Utiliser .copy() pour éviter les avertissements
    
    # Convertir la colonne 'tweet' en type string (au cas où elle contient des nombres)
    data.loc[:, 'tweet'] = data['tweet'].astype(str)  # Utiliser .loc pour éviter les avertissements
    
    # Nettoyage du texte (minuscule, suppression des liens, mentions, chiffres, etc.)
    data.loc[:, 'tweet'] = data['tweet'].apply(clean_text)

    # Supprimer les stopwords et la ponctuation
    stop_words = set(stopwords.words('english'))
    data.loc[:, 'tweet'] = data['tweet'].apply(lambda x: ' '.join([word for word in x.split() if word.lower() not in stop_words]))
    data.loc[:, 'tweet'] = data['tweet'].apply(lambda x: x.translate(str.maketrans('', '', string.punctuation)))
    
    return data


def split_data(data):
    # Diviser les données en ensembles d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(data['tweet'], data['sentiment'], test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test

def vectorize_data(X_train, X_test):
    # Vectoriser les textes avec TF-IDF
    vectorizer = TfidfVectorizer()
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    return X_train_vec, X_test_vec, vectorizer

def train_model(X_train_vec, y_train):
    # Entraîner un modèle SVM
    model = svm.SVC(kernel='linear', probability=True)  
    model.fit(X_train_vec, y_train)
    return model

def evaluate_model(model, X_test_vec, y_test):
    y_pred = model.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=['Positive', 'Negative', 'Neutral'])
    return accuracy, cm, report

if __name__ == "__main__":
    # Charger et prétraiter les données
    data = load_data('data/tweets.csv')
    data = preprocess_data(data)
    
    # Diviser les données
    X_train, X_test, y_train, y_test = split_data(data)
    
    # Vectoriser les données
    X_train_vec, X_test_vec, vectorizer = vectorize_data(X_train, X_test)
    
    # Entraîner le modèle
    model = train_model(X_train_vec, y_train)
    
    # Sauvegarder le modèle et le vectorizer
    joblib.dump(model, 'model/svm_model.pkl')
    joblib.dump(vectorizer, 'model/vectorizer.pkl')
  
    print("Modèle entraîné et sauvegardé avec succès !")

    accuracy, cm, report = evaluate_model(model, X_test_vec, y_test)    
    print(f"Prediction Accuracy: {accuracy * 100:.2f}%")
    print("\nConfusion Matrix:")
    print(cm)
    print("\nClassification Report:")
    print(report)

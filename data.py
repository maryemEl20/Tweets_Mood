import os
import nltk
import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import string

if not os.path.exists(os.path.join(nltk.data.find("corpora"), "stopwords")):
    nltk.download('stopwords')

from nltk.corpus import stopwords

def load_data(filepath):
    data = pd.read_csv(filepath)
    return data

def preprocess_data(data):
    data = data.dropna(subset=['tweet']).copy()
    
    data.loc[:, 'tweet'] = data['tweet'].astype(str)
    
    stop_words = set(stopwords.words('english'))
    data.loc[:, 'tweet'] = data['tweet'].apply(lambda x: ' '.join([word for word in x.split() if word.lower() not in stop_words]))
    data.loc[:, 'tweet'] = data['tweet'].apply(lambda x: x.translate(str.maketrans('', '', string.punctuation)))
    return data

def split_data(data):
    X_test = data['tweet']
    y_test = data['sentiment']
    return X_test, y_test

def vectorize_data(X_test, vectorizer):
    X_test_vec = vectorizer.transform(X_test)
    return X_test_vec

def evaluate_model(model, X_test_vec, y_test):
    y_pred = model.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=['Positive', 'Negative', 'Neutral','Irrelevant'])
    return accuracy, cm, report

if __name__ == "__main__":
    data = load_data('data/tweets.csv')
    data = preprocess_data(data)
    
    X_test, y_test = split_data(data)
    
    model = joblib.load('model/svm_model.pkl')
    vectorizer = joblib.load('model/vectorizer.pkl')
    
    X_test_vec = vectorize_data(X_test, vectorizer)
    
    accuracy, cm, report = evaluate_model(model, X_test_vec, y_test)
    
    print(f"Prediction Accuracy: {accuracy * 100:.2f}%")
    print("\nConfusion Matrix:")
    print(cm)
    print("\nClassification Report:")
    print(report)

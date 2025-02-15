import sqlite3

# Connexion à la base de données (créera le fichier s'il n'existe pas)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Création de la table sentiments
cursor.execute('''CREATE TABLE IF NOT EXISTS sentiments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT,
                    prediction TEXT,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT)''')

# Validation des changements
conn.commit()

# Affichage des données de la table sentiments
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM sentiments;")
rows = cursor.fetchall()
print("Données dans la table sentiments :")
for row in rows:
    print(row)
conn.close()

# Fermeture de la connexion
conn.close()

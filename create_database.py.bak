import pandas as pd
import sqlite3

# Chemins des fichiers Excel
file_produits = './data/article.xlsx'
file_stocks = './data/stock.xlsx'
file_clients = './data/client.xlsx'
file_ventes = './data/vente.xlsx'

# Connexion à la base de données SQLite
db_name = 'gestion_ventes_stocks.db'
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Supprimer les tables existantes si elles existent
cursor.execute('DROP TABLE IF EXISTS Produits')
cursor.execute('DROP TABLE IF EXISTS Stocks')
cursor.execute('DROP TABLE IF EXISTS Clients')
cursor.execute('DROP TABLE IF EXISTS Ventes')

# Création des tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS Produits (
    id_produit INTEGER PRIMARY KEY,
    nom_produit TEXT NOT NULL,
    description_produit TEXT,
    categorie TEXT,
    prix_unitaire REAL,
    prix_de_vente_ht REAL,
    tva REAL,
    commission REAL,
    type_com TEXT,
    ean TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Stocks (
    id_produit INTEGER PRIMARY KEY,
    quantite_stock INTEGER,
    FOREIGN KEY (id_produit) REFERENCES Produits(id_produit)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Clients (
    id_client INTEGER PRIMARY KEY,
    nom_client TEXT NOT NULL,
    email_client TEXT,
    telephone_client TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Ventes (
    id_vente INTEGER PRIMARY KEY AUTOINCREMENT,
    id_produit INTEGER,
    id_client INTEGER,
    date_vente TEXT,
    quantite_vendue INTEGER,
    num_piece TEXT,
    designation TEXT,
    prix_achat REAL,
    montant_total REAL,
    nom_representant TEXT,
    nom_client TEXT,
    FOREIGN KEY (id_produit) REFERENCES Produits(id_produit),
    FOREIGN KEY (id_client) REFERENCES Clients(id_client)
)
''')

# Charger les fichiers Excel
data_produits = pd.read_excel(file_produits)
data_stocks = pd.read_excel(file_stocks)
data_clients = pd.read_excel(file_clients)
data_ventes = pd.read_excel(file_ventes)

# Afficher les colonnes pour diagnostic
print("Colonnes disponibles dans data_produits :", data_produits.columns)
print("Colonnes disponibles dans data_stocks :", data_stocks.columns)
print("Colonnes disponibles dans data_clients :", data_clients.columns)
print("Colonnes disponibles dans data_ventes :", data_ventes.columns)

# Vérifier et renommer les colonnes pour Produits
data_produits.rename(columns={
    'Code Article': 'id_produit',
    'Nom produit': 'nom_produit',
    'Description': 'description_produit',
    'Categorie': 'categorie',
    'Prix unitaire': 'prix_unitaire',
    'PRIX DE VENTE HT': 'prix_de_vente_ht',
    'TVA': 'tva',
    'Commission': 'commission',
    'TypeCom': 'type_com',
    'Ean': 'ean'
}, inplace=True)

# Vérifier et renommer les colonnes pour Stocks
data_stocks.rename(columns={
    'Code Article': 'id_produit',
    'Stock': 'quantite_stock'
}, inplace=True)

# Vérifier et renommer les colonnes pour Clients
data_clients.rename(columns={
    'Code Client': 'id_client',
    'Nom': 'nom_client',
    'Email': 'email_client',
    'Téléphone': 'telephone_client'
}, inplace=True)

# Vérifier et renommer les colonnes pour Ventes
data_ventes.rename(columns={
    'Date': 'date_vente',
    'Code Article': 'id_produit',
    'Code client': 'id_client',
    'Quantite': 'quantite_vendue',
    'Quantité': 'quantite_vendue',
    'Num pièce': 'num_piece',
    'Désignation': 'designation',
    'Prix achat': 'prix_achat',
    'Montant total': 'montant_total',
    'Nom representant': 'nom_representant',
    'Nom client': 'nom_client'
}, inplace=True)

# Afficher les colonnes après renommage
print("Colonnes après renommage dans data_ventes :", data_ventes.columns)

# Convertir les colonnes en types compatibles avec SQLite
data_produits['id_produit'] = pd.to_numeric(data_produits['id_produit'], errors='coerce').astype('Int64')
data_stocks['id_produit'] = pd.to_numeric(data_stocks['id_produit'], errors='coerce').astype('Int64')
data_stocks['quantite_stock'] = pd.to_numeric(data_stocks['quantite_stock'], errors='coerce')
data_clients['id_client'] = pd.to_numeric(data_clients['id_client'], errors='coerce').astype('Int64')
data_ventes['id_produit'] = pd.to_numeric(data_ventes['id_produit'], errors='coerce').astype('Int64')
data_ventes['id_client'] = pd.to_numeric(data_ventes['id_client'], errors='coerce').astype('Int64')
data_ventes['quantite_vendue'] = pd.to_numeric(data_ventes['quantite_vendue'], errors='coerce')
data_ventes['prix_achat'] = pd.to_numeric(data_ventes['prix_achat'], errors='coerce')
data_ventes['montant_total'] = pd.to_numeric(data_ventes['montant_total'], errors='coerce')

# Insérer les données dans Produits
if 'id_produit' in data_produits.columns and 'nom_produit' in data_produits.columns:
    data_produits.to_sql('Produits', conn, if_exists='append', index=False)
else:
    print("Les colonnes essentielles pour Produits sont manquantes. Veuillez vérifier le fichier Excel.")

# Insérer les données dans Stocks
if 'id_produit' in data_stocks.columns and 'quantite_stock' in data_stocks.columns:
    data_stocks.to_sql('Stocks', conn, if_exists='append', index=False)
else:
    print("Les colonnes essentielles pour Stocks sont manquantes. Veuillez vérifier le fichier Excel.")

# Insérer les données dans Clients
if 'id_client' in data_clients.columns and 'nom_client' in data_clients.columns:
    data_clients.to_sql('Clients', conn, if_exists='append', index=False)
else:
    print("Les colonnes essentielles pour Clients sont manquantes. Veuillez vérifier le fichier Excel.")

# Insérer les données dans Ventes
if 'id_produit' in data_ventes.columns and 'id_client' in data_ventes.columns and 'date_vente' in data_ventes.columns:
    data_ventes.to_sql('Ventes', conn, if_exists='append', index=False)
else:
    print("Les colonnes essentielles pour Ventes sont manquantes. Veuillez vérifier le fichier Excel.")

# Validation des changements et fermeture de la connexion
conn.commit()
conn.close()

print("Base de données créée et données importées avec succès !")

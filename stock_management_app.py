from flask import Flask, render_template, request, jsonify
import pandas as pd
import sqlite3
import os
import matplotlib
matplotlib.use('Agg')  # Utiliser un backend non interactif
import matplotlib.pyplot as plt
from app_config import app
from routes_product_details import product_details
# Initialisation de l'application Flask
app = Flask(__name__)

# Configuration de la base de données SQLite
db_name = 'gestion_ventes_stocks.db'

# Register the product_details route
product_details(app, db_name)


# Connectez-vous à la base de données
conn = sqlite3.connect('gestion_ventes_stocks.db')
cursor = conn.cursor()




# Vérifiez si la colonne existe avant de tenter de la supprimer
cursor.execute("PRAGMA table_info(LogistiqueProduits);")
columns = [info[1] for info in cursor.fetchall()]

if 'stock_securite' in columns:
    cursor.execute("CREATE TABLE LogistiqueProduits_new AS SELECT code_article, poids, nb_par_carton, largeur_carton, longueur_carton, hauteur_carton, poids_carton, delai_reapprovisionnement FROM LogistiqueProduits;")
    cursor.execute("DROP TABLE LogistiqueProduits;")
    cursor.execute("ALTER TABLE LogistiqueProduits_new RENAME TO LogistiqueProduits;")
    print("Colonne 'stock_securite' supprimée avec succès.")
else:
    print("La colonne 'stock_securite' n'existe pas.")

conn.commit()
conn.close()



# Fonction pour recréer la base de données avec les bonnes structures
def recreate_database():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Ne réinitialise pas la table des informations logistiques
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS LogistiqueProduits (
        code_article TEXT PRIMARY KEY,
        poids REAL,
        nb_par_carton INTEGER,
        largeur_carton REAL,
        longueur_carton REAL,
        hauteur_carton REAL,
        poids_carton REAL,
        FOREIGN KEY (code_article) REFERENCES Produits (code_article)
    );
    """)

    # Recréation des tables
    cursor.execute("DROP TABLE IF EXISTS Produits;")
    cursor.execute("DROP TABLE IF EXISTS Stocks;")
    cursor.execute("DROP TABLE IF EXISTS Ventes;")
    cursor.execute("DROP TABLE IF EXISTS Achats;")

    cursor.execute("""
    CREATE TABLE Produits (
        code_article TEXT PRIMARY KEY,
        nom_produit TEXT,
        poids REAL DEFAULT 0,
        nb_par_carton INTEGER DEFAULT 0,
        largeur_carton REAL DEFAULT 0,
        longueur_carton REAL DEFAULT 0,
        hauteur_carton REAL DEFAULT 0,
        poids_carton REAL DEFAULT 0
    );
    """)

    cursor.execute("""
    CREATE TABLE Stocks (
        code_article TEXT,
        quantite_stock INTEGER,
        FOREIGN KEY (code_article) REFERENCES Produits (code_article)
    );
    """)

    cursor.execute("""
    CREATE TABLE Ventes (
        id_vente INTEGER PRIMARY KEY AUTOINCREMENT,
        code_article TEXT,
        date_vente TEXT,
        quantite_vendue INTEGER,
        prix_achat INTEGER,
        nom_representant TEXT,
        pharmacie TEXT,
        FOREIGN KEY (code_article) REFERENCES Produits (code_article)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE Achats (
        id_achat INTEGER PRIMARY KEY AUTOINCREMENT,
        code_document INTEGER,
        numero_document TEXT,
        date_document TEXT,
        fournisseur TEXT,
        quantite INTEGER,
        code_article TEXT,
        FOREIGN KEY (code_article) REFERENCES Produits (code_article)
    );
    """)

    conn.commit()
    conn.close()
    print("Base de données recréée avec succès.")
    
conn = sqlite3.connect(db_name)
print(pd.read_sql_query("SELECT * FROM Achats LIMIT 5", conn))
conn.close()
    
    
    
def update_database_schema():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    try:
        # Ajouter la colonne delai_reapprovisionnement si elle n'existe pas
        cursor.execute("""
            ALTER TABLE LogistiqueProduits ADD COLUMN delai_reapprovisionnement INTEGER;
        """)
    except sqlite3.OperationalError as e:
        print(f"Colonne 'delai_reapprovisionnement' déjà existante : {e}")

    try:
        # Ajouter la colonne stock_securite si elle n'existe pas
        cursor.execute("""
            ALTER TABLE LogistiqueProduits ADD COLUMN stock_securite INTEGER;
        """)
    except sqlite3.OperationalError as e:
        print(f"Colonne 'stock_securite' déjà existante : {e}")

    conn.commit()
    conn.close()

def create_client_table():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Client (
            code_client TEXT PRIMARY KEY,
            nom_client TEXT NOT NULL,
            representant TEXT,
            tel TEXT,
            email TEXT,
            date_creation TEXT,
            adresse TEXT,
            cp TEXT,
            ville TEXT,
            pays TEXT
        );
    """)
    conn.commit()
    conn.close()
    print("Table Client créée avec succès ou existante.")


def import_client_data():
    file_clients = './data/client.xlsx'
    if not os.path.exists(file_clients):
        print("Fichier client.xlsx introuvable dans le dossier ./data. Vérifiez le chemin et réessayez.")
        return

    try:
        data_clients = pd.read_excel(file_clients)
        print("Colonnes disponibles dans le fichier clients :")
        print(data_clients.columns)

        # Renommer les colonnes pour correspondre à la base de données
        data_clients.rename(columns={
            'Code Client': 'code_client',
            'nom': 'nom_client',
            'representant': 'representant',
            'tel': 'telephone',
            'email': 'email',
            'DATE CREATION': 'date_creation',
            'ADRESSE': 'adresse',
            'CP': 'cp',  # Assurez-vous de mapper 'CP' vers 'cp'
            'VILLE ': 'ville',  # Corrigez pour inclure l'espace final
            'PAYS': 'pays'
        }, inplace=True)

        # Sélectionner uniquement les colonnes nécessaires
        data_clients = data_clients[['code_client', 'nom_client', 'representant', 'telephone', 
                                     'email', 'date_creation', 'adresse', 'cp', 'ville', 'pays']]

        conn = sqlite3.connect(db_name)
        data_clients.to_sql('Client', conn, if_exists='replace', index=False)
        conn.close()
        print("Données insérées avec succès dans la table Client.")

    except Exception as e:
        print(f"Erreur lors de l'importation des données clients : {e}")

    
def check_client_table():
    conn = sqlite3.connect(db_name)
    query = "SELECT * FROM Client LIMIT 5;"
    try:
        df = pd.read_sql_query(query, conn)
        print("Exemple de données dans la table Client :")
        print(df)
    except Exception as e:
        print(f"Erreur lors de la vérification de la table Client : {e}")
    conn.close()
    
def check_client_table_structure():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(Client);")
    columns = cursor.fetchall()
    conn.close()
    print("Structure de la table Client :")
    for column in columns:
        print(column)
    
    
# Fonction pour importer les données des produits
def import_produits():
    file_produits = './data/produits.xlsx'
    if not os.path.exists(file_produits):
        print("Fichier produits.xlsx introuvable dans le dossier ./data. Vérifiez le chemin et réessayez.")
        return

    try:
        data_produits = pd.read_excel(file_produits)
        print("Colonnes disponibles dans le fichier produits :")
        print(data_produits.columns)

        data_produits.rename(columns={
            'Code Article': 'code_article',
            'Nom produit': 'nom_produit'
        }, inplace=True)

        print("Colonnes après renommage :")
        print(data_produits.columns)

        # Ajoutez des colonnes par défaut pour les nouvelles données
        data_produits['poids'] = 0
        data_produits['nb_par_carton'] = 0
        data_produits['largeur_carton'] = 0
        data_produits['longueur_carton'] = 0
        data_produits['hauteur_carton'] = 0
        data_produits['poids_carton'] = 0

        conn = sqlite3.connect(db_name)
        data_produits.to_sql('Produits', conn, if_exists='replace', index=False)
        conn.close()
        print("Données insérées avec succès dans la table Produits.")
    except Exception as e:
        print(f"Erreur lors de l'importation des produits : {e}")

        


# Fonction pour vérifier les tables et leurs données
def check_database_tables():
    conn = sqlite3.connect(db_name)
    tables = ['Produits', 'Stocks', 'Ventes']
    for table in tables:
        print(f"\nDonnées dans la table {table}:")
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 5", conn)
            print(df)
        except Exception as e:
            print(f"Erreur lors de l'accès à la table {table} : {e}")
    conn.close()

# Route pour afficher le formulaire d'ajout des détails du produit
@app.route('/add_product_form')
def add_product_form():
    code_article = request.args.get('code_article', '')
    existing_data = None

    if code_article:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT code_article, poids, nb_par_carton, largeur_carton, longueur_carton, hauteur_carton, 
                   poids_carton, delai_reapprovisionnement
            FROM LogistiqueProduits WHERE code_article = ?
        """, (code_article,))
        existing_entry = cursor.fetchone()
        conn.close()

        if existing_entry:
            existing_data = {
                'code_article': existing_entry[0],
                'poids': existing_entry[1],
                'nb_par_carton': existing_entry[2],
                'largeur_carton': existing_entry[3],
                'longueur_carton': existing_entry[4],
                'hauteur_carton': existing_entry[5],
                'poids_carton': existing_entry[6],
                'delai_reapprovisionnement': existing_entry[7]
            }

    return render_template('add_product_form.html', code_article=code_article, existing_data=existing_data)


# Route pour ajouter ou mettre à jour les informations logistiques du produit
@app.route('/add_product_details', methods=['POST'])
def add_product_details():
    # Récupérer les données du formulaire
    code_article = request.form['code_article']
    poids = request.form['poids']
    nb_par_carton = request.form['nb_par_carton']
    largeur_carton = request.form['largeur_carton']
    longueur_carton = request.form['longueur_carton']
    hauteur_carton = request.form['hauteur_carton']
    poids_carton = request.form['poids_carton']
    delai_reapprovisionnement = request.form['delai_reapprovisionnement']

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Vérifier si des données logistiques existent déjà pour ce produit
    cursor.execute("SELECT * FROM LogistiqueProduits WHERE code_article = ?", (code_article,))
    existing_entry = cursor.fetchone()

    if existing_entry:
        # Si les données existent, les mettre à jour
        cursor.execute("""
            UPDATE LogistiqueProduits
            SET poids = ?, nb_par_carton = ?, largeur_carton = ?, longueur_carton = ?, hauteur_carton = ?, 
                poids_carton = ?, delai_reapprovisionnement = ?
            WHERE code_article = ?;
        """, (poids, nb_par_carton, largeur_carton, longueur_carton, hauteur_carton, poids_carton, delai_reapprovisionnement, code_article))
        message = f"Les détails du produit {code_article} ont été mis à jour avec succès."
    else:
        # Sinon, insérer une nouvelle entrée
        cursor.execute("""
            INSERT INTO LogistiqueProduits (code_article, poids, nb_par_carton, largeur_carton, longueur_carton, hauteur_carton, 
                                            poids_carton, delai_reapprovisionnement)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, (code_article, poids, nb_par_carton, largeur_carton, longueur_carton, hauteur_carton, poids_carton, delai_reapprovisionnement))
        message = f"Les détails du produit {code_article} ont été ajoutés avec succès."

    conn.commit()
    conn.close()
    return message




        

# Fonction pour importer les données des ventes
def import_ventes():
    file_ventes = './data/ventes.xlsx'
    if not os.path.exists(file_ventes):
        print("Fichier ventes.xlsx introuvable dans le dossier ./data. Vérifiez le chemin et réessayez.")
        return

    try:
        # Lecture du fichier Excel
        data_ventes = pd.read_excel(file_ventes)
        print("Colonnes disponibles dans le fichier ventes :")
        print(data_ventes.columns)

        # Renommage des colonnes pour correspondre aux noms de la base de données
        data_ventes.rename(columns={
            'Code client': 'code_client',
            'Code Article': 'code_article',
            'Date': 'date_vente',
            'Quantite': 'quantite_vendue',
            'Nom representant': 'nom_representant',
            'Nom client': 'nom_client',
            'Prix achat': 'prix_achat'
        }, inplace=True)

        print("Colonnes après renommage :")
        print(data_ventes.columns)

        # Insertion des données dans la table `Ventes`
        conn = sqlite3.connect(db_name)
        data_ventes[['code_client', 'code_article', 'date_vente', 'quantite_vendue', 'prix_achat', 'nom_representant', 'nom_client']].to_sql(
            'Ventes', conn, if_exists='replace', index=False)
        conn.close()
        print("Données insérées avec succès dans la table Ventes.")
    except Exception as e:
        print(f"Erreur lors de l'importation des ventes : {e}")





# Fonction pour importer les données des stocks
def import_stocks():
    file_stocks = './data/stock.xlsx'
    if not os.path.exists(file_stocks):
        print("Fichier stock.xlsx introuvable dans le dossier ./data. Vérifiez le chemin et réessayez.")
        return

    try:
        data_stocks = pd.read_excel(file_stocks)
        print("Colonnes disponibles dans le fichier stocks :")
        print(data_stocks.columns)

        data_stocks.rename(columns={
            'Code Article': 'code_article',
            'Stock': 'quantite_stock'
        }, inplace=True)

        print("Colonnes après renommage :")
        print(data_stocks.columns)

        conn = sqlite3.connect(db_name)
        data_stocks[['code_article', 'quantite_stock']].to_sql(
            'Stocks', conn, if_exists='replace', index=False)
        conn.close()
        print("Données insérées avec succès dans la table Stocks.")
    except Exception as e:
        print(f"Erreur lors de l'importation des stocks : {e}")


def import_achats():
    file_achats = './data/achats.xlsx'
    if not os.path.exists(file_achats):
        print("Fichier achats.xlsx introuvable dans le dossier ./data. Vérifiez le chemin et réessayez.")
        return

    try:
        # Charger les données Excel
        data_achats = pd.read_excel(file_achats)
        print("Colonnes disponibles dans le fichier achats :")
        print(data_achats.columns)

        # Renommer les colonnes pour correspondre à la base de données
        data_achats.rename(columns={
            'code_document': 'code_document',
            'numero_document': 'numero_document',
            'date_document': 'date_document',
            'fournisseur': 'fournisseur',
            'quantite': 'quantite',
            'code_article': 'code_article'
        }, inplace=True)

        # Correction des dates
        def convert_date(date):
            try:
                if isinstance(date, (int, float)):
                    # Convertir les nombres au format attendu
                    return pd.to_datetime(str(int(date)).zfill(6), format='%d%m%y', errors='coerce')
                else:
                    return pd.to_datetime(date, errors='coerce')
            except Exception as e:
                print(f"Erreur de conversion de la date : {date} - {e}")
                return None

        data_achats['date_document'] = data_achats['date_document'].apply(convert_date)

        # Supprimer les lignes avec des dates invalides
        data_achats = data_achats.dropna(subset=['date_document'])
        data_achats['date_document'] = data_achats['date_document'].dt.strftime('%Y-%m-%d')

        # Filtrer les colonnes nécessaires
        data_achats = data_achats[['code_document', 'numero_document', 'date_document', 'fournisseur', 'quantite', 'code_article']]

        # Connecter à la base de données et insérer les données
        conn = sqlite3.connect(db_name)
        data_achats.to_sql('Achats', conn, if_exists='replace', index=False)
        conn.close()
        print("Données insérées avec succès dans la table Achats.")
    except Exception as e:
        print(f"Erreur lors de l'importation des achats : {e}")


def reset_ventes_table():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Ventes;")
    conn.commit()
    conn.close()
    print("Table Ventes réinitialisée.")




# Fonction pour obtenir le palmarès des ventes
# avec correction des ventes annuelles
# Fonction corrigée pour obtenir le palmarès des ventes 
def get_palmares(order_by='vente_2024 DESC'):
    conn = sqlite3.connect(db_name)

    # Requête SQL simplifiée et corrigée
    query = f'''
    SELECT 
        p.code_article AS code_article,
        p.nom_produit,
        COALESCE(s.quantite_stock, 0) AS quantite_stock,
        COALESCE(lp.delai_reapprovisionnement, 0) AS delai_reapprovisionnement,
        -- Calcul du stock de sécurité basé sur les ventes mensuelles moyennes
        ROUND((AVG(CASE 
                    WHEN strftime('%Y-%m', v.date_vente) >= strftime('%Y-%m', date('now', '-12 months')) 
                    THEN v.quantite_vendue 
                    ELSE 0 
                  END) / 30) * lp.delai_reapprovisionnement + 
              AVG(CASE 
                    WHEN strftime('%Y-%m', v.date_vente) >= strftime('%Y-%m', date('now', '-12 months')) 
                    THEN v.quantite_vendue 
                    ELSE 0 
                  END), 2) AS stock_securite,
        -- Somme des ventes pour chaque année
        SUM(CASE WHEN strftime('%Y', v.date_vente) = '2023' THEN v.quantite_vendue ELSE 0 END) AS vente_2023,
        SUM(CASE WHEN strftime('%Y', v.date_vente) = '2024' THEN v.quantite_vendue ELSE 0 END) AS vente_2024,
        SUM(CASE WHEN strftime('%Y', v.date_vente) = '2025' THEN v.quantite_vendue ELSE 0 END) AS vente_2025
    FROM 
        Produits p
    LEFT JOIN 
        Stocks s ON p.code_article = s.code_article
    LEFT JOIN 
        LogistiqueProduits lp ON p.code_article = lp.code_article
    LEFT JOIN 
        Ventes v ON p.code_article = v.code_article
    GROUP BY 
        p.code_article, p.nom_produit, s.quantite_stock, lp.delai_reapprovisionnement
    ORDER BY 
        {order_by};
    '''

    # Exécution de la requête
    result = pd.read_sql_query(query, conn)
    conn.close()

    # Vérification des données brutes
    print("Données brutes après exécution de la requête SQL :")
    print(result.head())

    # Nettoyage des données
    result['quantite_stock'] = result['quantite_stock'].fillna(0).astype(int)
    result['vente_2023'] = result['vente_2023'].fillna(0).astype(int)
    result['vente_2024'] = result['vente_2024'].fillna(0).astype(int)
    result['vente_2025'] = result['vente_2025'].fillna(0).astype(int)
    result['stock_securite'] = result['stock_securite'].fillna(0).astype(float)
    result['delai_reapprovisionnement'] = result['delai_reapprovisionnement'].fillna(0).astype(int)

    # Diagnostic intermédiaire
    print("Vérification des données après nettoyage :")
    print(result[['code_article', 'quantite_stock', 'vente_2023', 'vente_2024', 'vente_2025']])

    # Ajouter une colonne "Alerte" basée sur les critères spécifiés
    def calculate_alert(row):
        if row['delai_reapprovisionnement'] > 0:
            if row['quantite_stock'] < row['stock_securite']:
                return "Recommander"
            else:
                return "OK"
        return "Aucune Alerte"

    result['alerte'] = result.apply(calculate_alert, axis=1)

    # Vérification finale
    print("Résultats finaux du palmarès des ventes :")
    print(result[['code_article', 'alerte']])

    return result





# Fonction pour obtenir les ventes par représentant pour un produit spécifique
def get_sales_by_representative(code_article):
    conn = sqlite3.connect(db_name)
    query = f'''
    SELECT
        COALESCE(c.representant, 'Inconnu') AS nom_representant,
        p.nom_produit,
        SUM(CASE WHEN strftime('%Y', v.date_vente) = '2023' THEN v.quantite_vendue ELSE 0 END) AS vente_2023,
        SUM(CASE WHEN strftime('%Y', v.date_vente) = '2024' THEN v.quantite_vendue ELSE 0 END) AS vente_2024,
        SUM(CASE WHEN strftime('%Y', v.date_vente) = '2025' THEN v.quantite_vendue ELSE 0 END) AS vente_2025
    FROM
        Ventes v
    LEFT JOIN
        Produits p ON v.code_article = p.code_article
    LEFT JOIN
        Client c ON v.code_client = c.code_client
    WHERE
        v.code_article = ?
    GROUP BY
        c.representant, p.nom_produit
    ORDER BY
        vente_2024 DESC, vente_2023 DESC, vente_2025 DESC;
    '''
    result = pd.read_sql_query(query, conn, params=[code_article])
    conn.close()
    
    # Diagnostic des résultats
    print(f"Ventes par représentant pour le produit {code_article} :")
    print(result)
    
    return result


# Fonction pour obtenir les produits vendus par un représentant
def get_products_by_representative(nom_representant):
    conn = sqlite3.connect(db_name)
    query = f'''
    SELECT
        p.nom_produit,
        SUM(CASE WHEN strftime('%Y', v.date_vente) = '2023' THEN v.quantite_vendue ELSE 0 END) AS vente_2023,
        SUM(CASE WHEN strftime('%Y', v.date_vente) = '2024' THEN v.quantite_vendue ELSE 0 END) AS vente_2024,
        SUM(CASE WHEN strftime('%Y', v.date_vente) = '2025' THEN v.quantite_vendue ELSE 0 END) AS vente_2025
    FROM
        Ventes v
    JOIN
        Produits p ON v.code_article = p.code_article
    JOIN
        Client c ON v.code_client = c.code_client
    WHERE
        c.representant = ?
    GROUP BY
        p.nom_produit
    ORDER BY
        vente_2024 DESC, vente_2023 DESC, vente_2025 DESC;
    '''
    result = pd.read_sql_query(query, conn, params=[nom_representant])
    conn.close()

    # Diagnostic : afficher les résultats dans la console pour vérification
    print(f"Produits vendus par le représentant {nom_representant} :")
    print(result)

    return result

    



# Fonction mise à jour pour obtenir les ventes mensuelles et la moyenne des ventes
def get_monthly_sales_and_average():
    conn = sqlite3.connect(db_name)
    query = '''
    SELECT
        c.representant AS nom_representant,
        strftime('%Y-%m', v.date_vente) AS mois,
        SUM(v.quantite_vendue * v.prix_achat) AS chiffre_affaire
    FROM
        Ventes v
    JOIN
        Client c ON v.code_client = c.code_client
    GROUP BY
        c.representant, strftime('%Y-%m', v.date_vente)
    ORDER BY
        c.representant, mois;
    '''
    
    # Récupérer les données
    sales_data = pd.read_sql_query(query, conn)

    # Pivot pour obtenir une ligne par représentant et une colonne par mois
    sales_pivot = sales_data.pivot_table(
        index='nom_representant',
        columns='mois',
        values='chiffre_affaire',
        fill_value=0
    ).reset_index()

    # Calcul de la moyenne des ventes par mois (ligne par mois)
    monthly_totals = sales_pivot.drop(columns='nom_representant').sum(axis=0)  # Totaux mensuels
    num_representants = sales_pivot.shape[0]  # Nombre total de représentants
    average_sales = monthly_totals / num_representants  # Moyenne par mois

    conn.close()

    print("Données des ventes mensuelles (pivot) :")
    print(sales_pivot)
    print("Chiffre d'affaires moyen par mois :")
    print(average_sales)

    return sales_pivot, average_sales




# Fonction pour obtenir les ventes mensuelles par produit
def get_monthly_sales_by_product(code_article):
    conn = sqlite3.connect(db_name)
    query = f'''
    SELECT 
        strftime('%Y-%m', date_vente) AS mois,
        v.code_article,
        p.nom_produit,
        SUM(v.quantite_vendue) AS quantite_vendue
    FROM 
        Ventes v
    JOIN 
        Produits p ON v.code_article = p.code_article
    WHERE 
        v.code_article = ?
    GROUP BY 
        mois, v.code_article, p.nom_produit
    ORDER BY 
        mois ASC;
    '''
    result = pd.read_sql_query(query, conn, params=[code_article])
    conn.close()
    print(f"Ventes mensuelles pour le produit {code_article} :")
    print(result)
    return result
 
def get_monthly_sales_and_purchases(code_article):
    conn = sqlite3.connect(db_name)

    # Requête pour les ventes
    sales_query = '''
    SELECT
        strftime('%Y-%m', date_vente) AS mois,
        SUM(quantite_vendue) AS quantite_vendue
    FROM
        Ventes
    WHERE
        code_article = ?
    GROUP BY
        mois
    ORDER BY
        mois;
    '''
    sales_data = pd.read_sql_query(sales_query, conn, params=[code_article])

    # Requête pour les produits reçus
    received_query = '''
    SELECT
        strftime('%Y-%m', date_document) AS mois,
        SUM(quantite) AS quantite_achetee
    FROM
        Achats
    WHERE
        code_article = ? AND code_document = 16
    GROUP BY
        mois
    ORDER BY
        mois;
    '''
    received_data = pd.read_sql_query(received_query, conn, params=[code_article])

    # Requête pour les produits commandés
    ordered_query = '''
    SELECT
        strftime('%Y-%m', date_document) AS mois,
        SUM(quantite) AS quantite_commandee
    FROM
        Achats
    WHERE
        code_article = ? AND code_document = 12
    GROUP BY
        mois
    ORDER BY
        mois;
    '''
    ordered_data = pd.read_sql_query(ordered_query, conn, params=[code_article])

    # Fusionner les données
    combined_data = pd.merge(sales_data, received_data, on='mois', how='outer', suffixes=('_v', '_r')).fillna(0)
    combined_data = pd.merge(combined_data, ordered_data, on='mois', how='outer', suffixes=('', '_o')).fillna(0)

    combined_data['quantite_vendue'] = combined_data['quantite_vendue'].astype(int)
    combined_data['quantite_achetee'] = combined_data['quantite_achetee'].astype(int)
    combined_data['quantite_commandee'] = combined_data['quantite_commandee'].astype(int)

    conn.close()
    return combined_data


@app.route('/all_representative_sales')
def dynamic_representative_sales():
    conn = sqlite3.connect(db_name)
    query = '''
    SELECT
        c.representant AS nom_representant,
        strftime('%Y-%m', v.date_vente) AS mois,
        SUM(v.quantite_vendue * v.prix_achat) AS chiffre_affaire
    FROM
        Ventes v
    JOIN
        Client c ON v.code_client = c.code_client
    GROUP BY
        c.representant, strftime('%Y-%m', v.date_vente)
    ORDER BY
        c.representant, mois;
    '''
    sales_data = pd.read_sql_query(query, conn)
    conn.close()

    # Transformation en pivot pour créer des colonnes mois par mois
    sales_pivot = sales_data.pivot_table(
        index='nom_representant',
        columns='mois',
        values='chiffre_affaire',
        fill_value=0
    ).reset_index()

    # Calcul du CA moyen pour chaque mois
    average_sales = sales_pivot.drop(columns=['nom_representant']).mean().to_dict()

    # Transformer les données pour le JavaScript
    representative_sales = sales_pivot.to_dict(orient='records')

    return render_template(
        'all_representative_sales.html',
        representative_sales=representative_sales,
        average_sales=average_sales
    )



def get_monthly_sales_and_average():
    conn = sqlite3.connect(db_name)

    # Étape 1 : Requête SQL pour obtenir les ventes mensuelles par représentant
    query = '''
    SELECT
        c.representant AS nom_representant,
        strftime('%Y-%m', v.date_vente) AS mois,
        SUM(v.quantite_vendue * v.prix_achat) AS chiffre_affaire
    FROM
        Ventes v
    JOIN
        Client c ON v.code_client = c.code_client
    GROUP BY
        c.representant, strftime('%Y-%m', v.date_vente)
    ORDER BY
        c.representant, mois;
    '''
    sales_data = pd.read_sql_query(query, conn)

    # Étape 2 : Calcul du chiffre d'affaires moyen par mois
    # Calculer la moyenne en divisant par le nombre de représentants ayant passé une commande
    average_sales = (
        sales_data.groupby('mois')['chiffre_affaire']
        .sum()  # Total du CA par mois
        / sales_data.groupby('mois')['nom_representant'].nunique()  # Nombre unique de représentants actifs
    ).reset_index()

    average_sales.columns = ['mois', 'ca_moyen']

    conn.close()

    print("Données de vente mensuelles par représentant :")
    print(sales_data)

    print("Chiffre d'affaires moyen par mois :")
    print(average_sales)

    return sales_data, average_sales
 

# Route principale pour afficher le palmarès
@app.route('/')
def palmares():
    order_by = request.args.get('order_by', 'vente_2024 DESC')
    palmares_data = get_palmares(order_by)
    return render_template('palmares.html', tables=palmares_data.to_dict(orient='records'), order_by=order_by)

# Route pour afficher les ventes par représentant
@app.route('/product/<code_article>')
def product_sales(code_article):
    sales_data = get_sales_by_representative(code_article)
    return render_template('product_sales.html', tables=sales_data.to_dict(orient='records'), code_article=code_article)

# Route pour afficher les produits vendus par un représentant
@app.route('/representative/<nom_representant>')
def representative_sales(nom_representant):
    products_data = get_products_by_representative(nom_representant) 
    return render_template('representative_sales.html', tables=products_data.to_dict(orient='records'), nom_representant=nom_representant)
    
 # Route pour afficher les ventes mensuelles par pharmacie pour un produit
@app.route('/product/<code_article>/monthly_sales')
def monthly_sales(code_article):
    monthly_sales_data = get_monthly_sales_by_pharmacy(code_article)
    return render_template('monthly_sales.html', tables=monthly_sales_data.to_dict(orient='records'), code_article=code_article)

# Fonction pour obtenir les ventes mensuelles par pharmacie pour un produit spécifique
def get_monthly_sales_by_pharmacy(code_article):
    conn = sqlite3.connect(db_name)
    query = '''
    SELECT
        c.code_client AS code_client,
        c.nom_client AS nom_pharmacie,
        c.representant AS nom_representant,
        strftime('%Y-%m', v.date_vente) AS mois,
        SUM(v.quantite_vendue * v.prix_achat) AS chiffre_affaire
    FROM
        Ventes v
    JOIN
        Client c ON v.code_client = c.code_client
    WHERE
        v.code_article = ?
    GROUP BY
        c.code_client, c.nom_client, c.representant, strftime('%Y-%m', v.date_vente)
    ORDER BY
        c.nom_client, mois;
    '''
    sales_data = pd.read_sql_query(query, conn, params=[code_article])

    # Transformation en table pivot
    sales_pivot = sales_data.pivot_table(
        index=['code_client', 'nom_pharmacie', 'nom_representant'],
        columns='mois',
        values='chiffre_affaire',
        fill_value=0
    ).reset_index()

    conn.close()
    print(f"Ventes mensuelles par pharmacie pour le produit {code_article} :")
    print(sales_pivot)
    return sales_pivot
    

# Route pour afficher les ventes, produits reçus et produits commandés mensuels par produit
@app.route('/product/<code_article>/monthly_sales_product')
def monthly_sales_product(code_article):
    monthly_data = get_monthly_sales_and_purchases(code_article)
    return render_template('monthly_sales_product.html', tables=monthly_data.to_dict(orient='records'), code_article=code_article)

# Route pour gerer le moteur de recherche
@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT code_article, nom_produit
        FROM Produits
        WHERE LOWER(code_article) LIKE ? OR LOWER(nom_produit) LIKE ?
        LIMIT 10
    """, (f'%{query}%', f'%{query}%'))
    results = cursor.fetchall()
    conn.close()
    print(f"Requête reçue pour : {query}")
    return jsonify([{'code_article': row[0], 'nom_produit': row[1]} for row in results])



def show_logistic_data():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LogistiqueProduits;")
    rows = cursor.fetchall()
    conn.close()
    print("Données dans LogistiqueProduits :")
    for row in rows:
        print(row)

# Appeler cette fonction après insertion pour vérifier
show_logistic_data()  
    
# Route pour afficher les données dans la table Achats
@app.route('/view_achats')
def view_achats():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Récupérer toutes les données de la table Achats
    query = "SELECT * FROM Achats;"
    cursor.execute(query)
    rows = cursor.fetchall()

    conn.close()

    # Convertir les résultats en HTML simple
    achats_html = """
    <h1>Données dans la table Achats</h1>
    <table border="1">
        <tr>
            <th>ID Achat</th>
            <th>Code Document</th>
            <th>Numéro Document</th>
            <th>Date Document</th>
            <th>Fournisseur</th>
            <th>Quantité</th>
            <th>Code Article</th>
        </tr>
    """
    for row in rows:
        achats_html += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
    achats_html += "</table>"

    return achats_html


# Page d'accueil (Tableau de bord)
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", title="Tableau de Bord")

# Palmarès des ventes
@app.route('/sales_palmares')
def sales_palmares():
    try:
        palmares_data = get_palmares()  # Appel à la fonction qui génère les données du palmarès
        if palmares_data.empty:
            print("Aucune donnée disponible pour le palmarès.")
        return render_template('sales_palmares.html', tables=palmares_data.to_dict(orient='records'))
    except Exception as e:
        print(f"Erreur lors du chargement des données du palmarès : {e}")
        return render_template('error.html', message=str(e))

# Ajouter des données logistiques
@app.route("/add_logistics")
def add_logistics():
    return render_template("add_logistics.html", title="Ajouter des Données Logistiques")

# Ventes moyennes
@app.route("/average_sales")
def average_sales():
    sales_data, average_sales = get_monthly_sales_and_average()  # Fonction déjà créée
    return render_template("average_sales.html", title="Ventes Moyennes", data=sales_data, averages=average_sales)



   

if __name__ == '__main__':
    recreate_database()
    create_client_table()
    reset_ventes_table()
    import_client_data()
    check_client_table()
    import_achats()
    import_produits()
    import_stocks()
    import_ventes()
    check_database_tables()
    update_database_schema()  # Mettre à jour le schéma de la base de données
    app.run(debug=True)


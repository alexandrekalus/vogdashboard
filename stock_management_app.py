from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values, RealDictCursor
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import os
import matplotlib
matplotlib.use('Agg')  # Utiliser un backend non interactif
import matplotlib.pyplot as plt
from app_config import app
import folium
import geopandas as gpd
import json  # Import du module json
import seaborn as sns
from datetime import datetime, timedelta
import traceback

# Initialisation de l'application Flask
app = Flask(__name__)

# PostgreSQL Configuration
DATABASE_URL = "postgresql://vogdashboard_user:gXuIhJVeM7XqfsHe77LO0kMbInSLTOIi@dpg-cu9lbptsvqrc73dh3l1g-a.oregon-postgres.render.com/vogdashboard"

DB_CONFIG = {
    "dbname": "vogdashboard",
    "user": "vogdashboard_user",
    "password": "gXuIhJVeM7XqfsHe77LO0kMbInSLTOIi",
    "host": "dpg-cu9lbptsvqrc73dh3l1g-a.oregon-postgres.render.com",
    "port": "5432"
}


from sqlalchemy import create_engine

# Remplacez get_db_connection par l'utilisation d'un moteur SQLAlchemy
def get_db_connection():
    engine = create_engine(f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}")
    return engine

def get_db_connection():
    """Créer une connexion à la base de données PostgreSQL."""
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"Erreur de connexion à la base de données : {e}")
        return None

def get_db_connection():
    """Créer une connexion PostgreSQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"Erreur de connexion à la base de données : {e}")
        return None


        
@app.route("/initialize_db")
def initialize_db():
    create_tables()
    return "Tables créées ou existantes."


@app.route("/test_db")
def test_db():
    engine = get_db_connection()
    if engine:
        try:
            query = "SELECT * FROM ventes LIMIT 5;"
            df = pd.read_sql_query(query, engine)
            return df.to_html()
        except Exception as e: 
            return f"Erreur lors de l'exécution de la requête : {e}"
    else:
        return "Impossible de se connecter à la base de données."

def list_tables():
    engine = get_db_connection()
    if engine:
        try:
            query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
            df = pd.read_sql_query(query, engine)
            print("Tables existantes :")
            print(df)
        except Exception as e:
            print(f"Erreur lors de la récupération des tables : {e}")


# on efface les donnees des tables avant ajout des fichiers excel

def truncate_table(table_name, engine):
    """
    Vide une table spécifique dans la base de données en forçant le commit.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY CASCADE;'))
            conn.commit()  # Force la validation de la transaction
            print(f"La table {table_name} a été vidée avec succès.")
    except Exception as e:
        print(f"Erreur lors du vidage de la table {table_name} : {e}")


# en crée les bases de données
def create_tables():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Achats (
                    id_achat SERIAL PRIMARY KEY,
                    code_document INTEGER,
                    numero_document TEXT,
                    date_document DATE,
                    fournisseur TEXT,
                    quantite INTEGER,
                    code_article TEXT
                );
                
                CREATE TABLE IF NOT EXISTS LogistiqueProduits (
                    code_article TEXT PRIMARY KEY,
                    poids REAL,
                    nb_par_carton INTEGER,
                    largeur_carton REAL,
                    longueur_carton REAL,
                    hauteur_carton REAL,
                    poids_carton REAL,
                    delai_reapprovisionnement INTEGER
                );
                

            """)
            # Création de la table Stocks
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Stocks (
                    code_article TEXT PRIMARY KEY,
                    quantite_stock INTEGER NOT NULL DEFAULT 0
                );
            """)
            print("Table 'Stocks' créée ou déjà existante.")


            conn.commit()
        except Exception as e:
            print(f"Erreur lors de la création des tables : {e}")
        finally:
            conn.close()

def create_product_table():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Produits (
                    code_article TEXT PRIMARY KEY,
                    nom_produit TEXT
                );
            """)
            conn.commit()
        except Exception as e:
            print(f"Erreur lors de la création de la table Produits : {e}")
        finally:
            conn.close()


def group_similar_agents():
    """Regroupe les agents ayant des noms similaires dans la base de données"""
    engine = create_engine(DATABASE_URL)
    similar_agents = {
        'PASCALE BERNARD': ['PASCALE BERNARD', 'PASCALE BERNARD 2'],
        'CHARLOTTE PERES': ['PERES', 'PERES 2'],
        'DAVID ATTIAS': ['DAVID', 'DAVID2'],
        'CHRISTELLE VIAUD': ['CHRISTELLE VIAUD', 'CHRISTELLE VIAUD 2'],
        'VERONIQUE CHUPIN': ['CHUPIN', 'CHUPIN VERONIQUE', 'CHUPIN PAUL LOUP'],
        'CHRISTINE JAHN': ['CHRISTINE JAHN', 'CHRISTINE JAHN 2'],
        'ISABELLE BIRE': ['ISABELLE BIRE', 'ISABELLE BIRE 2']
    }

    with engine.connect() as connection:
        for canonical_name, variations in similar_agents.items():
            placeholders = ', '.join([f"'{name.strip()}'" for name in variations])
            query = text(f"""
                UPDATE client
                SET representant = :canonical_name
                WHERE TRIM(representant) IN ({placeholders});
            """)
            connection.execute(query, {'canonical_name': canonical_name})
        
        # Valider les modifications
        connection.commit()
        print("Regroupement des agents terminé.")


def import_client_data():
    file_clients = './data/client.xlsx'
    if not os.path.exists(file_clients):
        print("Fichier client.xlsx introuvable dans le dossier ./data. Vérifiez le chemin et réessayez.")
        return

    try:
        # Lecture du fichier Excel
        data_clients = pd.read_excel(file_clients)
        print("Colonnes disponibles dans le fichier clients :")
        print(data_clients.columns)

        # Renommer les colonnes pour correspondre aux noms de la base de données
        data_clients.rename(columns={
            'Code Client': 'code_client',
            'nom': 'nom_client',
            'representant': 'representant',
            'tel': 'tel',
            'email': 'email',
            'DATE CREATION': 'date_creation',
            'ADRESSE': 'adresse',
            'CP': 'cp',
            'VILLE ': 'ville',
            'PAYS': 'pays'
        }, inplace=True)

        # Ajouter un zéro aux codes postaux à 4 chiffres
        data_clients['cp'] = data_clients['cp'].apply(lambda x: str(int(x)).zfill(5) if pd.notnull(x) else x)

        # Vérifier les colonnes après modification
        print("Données prêtes pour insertion :")
        print(data_clients.head())

        # Connexion à PostgreSQL via SQLAlchemy
        engine = create_engine(DATABASE_URL)
        
        # Vider la table avant importation
        with engine.begin() as connection:
            connection.execute(text("TRUNCATE TABLE client RESTART IDENTITY CASCADE;"))
            print("Table client vidée avec succès.")
        
        # Insérer les données dans la table client
        if engine:
            data_clients.to_sql('client', con=engine, if_exists='append', index=False, method='multi')
            print("Données clients importées avec succès.")
        else:
            print("Erreur : impossible de créer un moteur SQLAlchemy.")

    except Exception as e:
        print(f"Erreur lors de l'importation des données clients : {e}")
        return  # Arrêter l'exécution si une erreur survient

    # Exécuter le regroupement des agents après l'importation
    group_similar_agents()





# Fonction pour importer les données des stocks
def import_stock_data():
    file_stocks = './data/stock.xlsx'
    if not os.path.exists(file_stocks):
        print("Fichier stock.xlsx introuvable dans le dossier ./data. Vérifiez le chemin et réessayez.")
        return

    try:
        # Charger les données du fichier Excel
        data_stocks = pd.read_excel(file_stocks)
        print("Colonnes disponibles dans le fichier stocks :")
        print(data_stocks.columns)

        # Renommer les colonnes
        data_stocks.rename(columns={
            'Code Article': 'code_article',
            'Stock': 'quantite_stock'
        }, inplace=True)

        # Connexion à la base PostgreSQL via SQLAlchemy
        engine = create_engine(DATABASE_URL)

        # Vider la table stocks avant l'importation
        truncate_table('stocks', engine)

        # Récupérer la liste des `code_article` existants dans la table produits
        query = "SELECT code_article FROM produits;"
        existing_articles = pd.read_sql_query(query, engine)['code_article'].tolist()

        # Filtrer les données pour ne garder que les articles valides
        data_stocks_valid = data_stocks[data_stocks['code_article'].isin(existing_articles)]

        # Vérifier s'il y a des données valides à insérer
        if data_stocks_valid.empty:
            print("Aucune donnée valide à insérer dans la table stocks.")
        else:
            # Insérer uniquement les données valides dans la table stocks
            data_stocks_valid.to_sql('stocks', con=engine, if_exists='append', index=False, method='multi')
            print("Données stocks importées avec succès.")

        # Fermeture de la connexion
        engine.dispose()
    except Exception as e:
        print(f"Erreur lors de l'importation des données stocks : {e}")


# Fonction pour importer les données des produits

    
        
def import_product_data():
    file_products = './data/produits.xlsx'
    
    # Vérifier si le fichier existe
    if not os.path.exists(file_products):
        print("Fichier produits.xlsx introuvable dans le dossier ./data.")
        return "Fichier produits.xlsx introuvable.", 404

    try:
        # Charger les données du fichier Excel
        data_products = pd.read_excel(file_products)
        print("Colonnes disponibles dans le fichier produits :", data_products.columns.tolist())

        # Renommer les colonnes pour correspondre à la base de données
        data_products.rename(columns={
            'Code Article': 'code_article',
            'Nom produit': 'nom_produit',
            'Ean': 'ean',
            'Delai_livraison': 'delai_livraison'  # Utilise le nom exact de la colonne
        }, inplace=True)

        # Sélectionner uniquement les colonnes nécessaires
        data_products = data_products[['code_article', 'nom_produit', 'ean', 'delai_livraison']]

        # Convertir 'ean' en chaîne de caractères pour éviter la notation scientifique
        data_products['ean'] = data_products['ean'].apply(lambda x: f"{int(x):013d}" if pd.notna(x) else None)

        # Afficher un aperçu des données avant l'insertion
        print("Données prêtes pour insertion :\n", data_products.head())

        # Connexion à PostgreSQL avec psycopg2 pour vider la table produits
        try:
            with psycopg2.connect(**DB_CONFIG) as conn:
                with conn.cursor() as cursor:
                    # Vider la table produits
                    cursor.execute("TRUNCATE TABLE produits RESTART IDENTITY CASCADE;")
                    conn.commit()
                    print("Table produits vidée avec succès.")

                    # Charger les données dans la table produits
                    engine = create_engine(DATABASE_URL)
                    data_products[['code_article', 'nom_produit', 'ean']].to_sql(
                        'produits', con=engine, if_exists='append', index=False, method='multi')
                    print("Données produits importées avec succès.")

                    # Gérer les données dans la table logistiqueproduits
                    for index, row in data_products.iterrows():
                        code_article = row['code_article']
                        delai_livraison = row['delai_livraison']

                        # Vérifier si le code_article existe déjà
                        cursor.execute(
                            "SELECT COUNT(*) FROM logistiqueproduits WHERE code_article = %s;", (code_article,))
                        exists = cursor.fetchone()[0]

                        if exists:
                            # Mise à jour du délai de réapprovisionnement
                            cursor.execute(
                                "UPDATE logistiqueproduits "
                                "SET delai_reapprovisionnement = %s "
                                "WHERE code_article = %s;",
                                (delai_livraison, code_article)
                            )
                            print(f"Produit {code_article} mis à jour dans logistiqueproduits.")
                        else:
                            # Insertion d'une nouvelle ligne
                            cursor.execute(
                                "INSERT INTO logistiqueproduits (code_article, delai_reapprovisionnement) "
                                "VALUES (%s, %s);",
                                (code_article, delai_livraison)
                            )
                            print(f"Produit {code_article} inséré dans logistiqueproduits.")

                        conn.commit()

            return "Données produits et logistique importées avec succès.", 200
        except Exception as e:
            print("Erreur lors de l'insertion des données :", e)
            print(traceback.format_exc())  # Affichage complet de l'erreur
            return f"Erreur lors de l'insertion des données : {e}", 500

    except Exception as e:
        print("Erreur lors de l'importation :", e)
        print(traceback.format_exc())  # Affichage complet de l'erreur
        return f"Erreur lors de l'importation : {e}", 500       
        

# Fonction pour importer les données des ventes
# Fonction pour importer les données des ventes
def import_sales_data():
    file_sales = './data/ventes.xlsx'
    if not os.path.exists(file_sales):
        print("Fichier ventes.xlsx introuvable dans le dossier ./data. Vérifiez le chemin et réessayez.")
        return

    try:
        # Charger le fichier Excel
        data_sales = pd.read_excel(file_sales)
        print("Colonnes disponibles dans le fichier ventes :")
        print(data_sales.columns)

        # Renommer les colonnes pour correspondre à la base de données
        data_sales.rename(columns={
            'Date': 'date_vente',
            'Num pièce': 'num_piece',
            'Code client': 'code_client',
            'Code Article': 'code_article',
            'Quantite': 'quantite_vendue',
            'Prix achat': 'prix_achat'
        }, inplace=True)

        # Conserver uniquement les colonnes nécessaires
        expected_columns = ['date_vente', 'num_piece', 'code_client', 'code_article', 'quantite_vendue', 'prix_achat']
        if not all(col in data_sales.columns for col in expected_columns):
            missing_columns = [col for col in expected_columns if col not in data_sales.columns]
            print(f"Colonnes manquantes dans le fichier Excel : {missing_columns}")
            return

        data_sales = data_sales[expected_columns]

        # Conversion des dates
        data_sales['date_vente'] = pd.to_datetime(data_sales['date_vente'], errors='coerce')

        # Supprimer les lignes avec des dates invalides ou des valeurs manquantes dans les colonnes clés
        data_sales = data_sales.dropna(subset=['date_vente', 'code_client', 'code_article', 'quantite_vendue', 'prix_achat'])

        # Remplacer les valeurs non valides par des zéros
        data_sales['quantite_vendue'] = pd.to_numeric(data_sales['quantite_vendue'], errors='coerce').fillna(0).astype(int)
        data_sales['prix_achat'] = pd.to_numeric(data_sales['prix_achat'], errors='coerce').fillna(0.0).astype(float)

        # Connexion à la base PostgreSQL via SQLAlchemy
        engine = create_engine(DATABASE_URL)

        # Vider la table avant importation
        try:
            truncate_table('Ventes', engine)
        except Exception as e:
            print(f"Erreur lors du vidage de la table Ventes : {e}")
            return

        # Vérifier si la table est bien vidée
        with engine.connect() as conn:
            result = conn.execute(text('SELECT COUNT(*) FROM "Ventes";'))
            count = result.scalar()
            print(f"Nombre de lignes dans la table Ventes après vidage : {count}")
            if count != 0:
                print("La table Ventes n'a pas été vidée correctement. Vérifiez la commande TRUNCATE.")
                return

        # Vérifier que les clients existent dans la table client
        query = "SELECT code_client FROM client"
        existing_clients = pd.read_sql_query(query, engine)['code_client'].tolist()

        # Filtrer les ventes pour ne conserver que celles avec des clients existants
        data_sales = data_sales[data_sales['code_client'].isin(existing_clients)]
        if data_sales.empty:
            print("Aucune donnée valide à insérer dans la table Ventes.")
            return

        # Afficher un aperçu des données prêtes pour insertion
        print("Données prêtes pour insertion :")
        print(data_sales.head())

        # Insérer les données dans PostgreSQL
        with engine.begin() as conn:
            data_sales.to_sql('Ventes', con=conn, if_exists='append', index=False, method='multi')

        # Vérification post-insertion
        with engine.connect() as conn:
            result = conn.execute(text('SELECT COUNT(*) FROM "Ventes";'))
            count_after = result.scalar()
            print(f"Nombre de lignes dans la table Ventes après insertion : {count_after}")

        print("Données ventes importées avec succès.")

    except Exception as e:
        print(f"Erreur lors de l'importation des données ventes : {e}")



# Fonction pour importer les données des achats après avoir vidé la table
def import_purchase_data():
    file_purchases = './data/achats.xlsx'
    
    if not os.path.exists(file_purchases):
        print("Fichier achats.xlsx introuvable dans le dossier ./data.")
        return "Fichier achats.xlsx introuvable.", 404

    try:
        # Charger le fichier Excel
        data_purchases = pd.read_excel(file_purchases)
        print("Colonnes initiales :", data_purchases.columns.tolist())

        # Supprimer explicitement la colonne 'rien' si elle existe
        if 'rien' in data_purchases.columns:
            data_purchases.drop(columns=['rien'], inplace=True)
            print("Colonne 'rien' supprimée.")
        
        print("Colonnes disponibles après suppression :", data_purchases.columns.tolist())

        # Renommer les colonnes pour correspondre à la base de données
        expected_columns = {
            'code_document': 'code_document',
            'numero_document': 'numero_document',
            'date_document': 'date_document',
            'fournisseur': 'fournisseur',
            'quantite': 'quantite',
            'code_article': 'code_article'
        }

        # Vérifier si toutes les colonnes attendues sont présentes
        missing_columns = [col for col in expected_columns.keys() if col not in data_purchases.columns]
        if missing_columns:
            print(f"Erreur : Colonnes manquantes dans le fichier Excel : {missing_columns}")
            return f"Colonnes manquantes : {missing_columns}", 400

        # Renommer uniquement les colonnes existantes
        data_purchases.rename(columns=expected_columns, inplace=True)

        # Conserver uniquement les colonnes nécessaires
        data_purchases = data_purchases[list(expected_columns.values())]
        print("Données après renommage et sélection des colonnes :")
        print(data_purchases.head())

        # Vérifier et convertir les dates si nécessaire
        if pd.api.types.is_datetime64_any_dtype(data_purchases['date_document']):
            print("Les dates sont déjà au format datetime.")
            # Si les dates sont déjà des objets datetime, les convertir au format attendu
            data_purchases['date_document'] = data_purchases['date_document'].dt.strftime('%Y-%m-%d')
        else:
            print("Conversion des dates depuis un format texte.")
            def convert_date(date_str):
                try:
                    return pd.to_datetime(date_str, format='%d/%m/%Y').strftime('%Y-%m-%d')
                except ValueError:
                    try:
                        # Si le format initial échoue, tenter avec 2 chiffres pour l'année
                        return pd.to_datetime(date_str, format='%d/%m/%y').strftime('%Y-%m-%d')
                    except ValueError:
                        return None
            data_purchases['date_document'] = data_purchases['date_document'].astype(str).apply(convert_date)

        print("Données après conversion des dates :")
        print(data_purchases.head())

        # Supprimer les lignes avec des dates invalides ou des valeurs manquantes
        data_purchases.dropna(subset=['date_document', 'code_article'], inplace=True)
        print("Données après suppression des lignes avec des valeurs manquantes :")
        print(data_purchases.head())

        # Connexion PostgreSQL pour vider la table "achats"
        try:
            with psycopg2.connect(**DB_CONFIG) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("TRUNCATE TABLE achats RESTART IDENTITY CASCADE;")
                    conn.commit()
                    print("Table achats vidée avec succès.")
        except Exception as e:
            print(f"Erreur lors du TRUNCATE de la table achats : {e}")
            return f"Erreur lors du TRUNCATE : {e}", 500

        # Récupérer les articles existants dans la table produits
        engine = create_engine(DATABASE_URL)
        query = "SELECT code_article FROM produits"
        existing_articles = pd.read_sql_query(query, engine)['code_article'].tolist()
        print(f"Articles existants récupérés : {len(existing_articles)} articles")

        # Filtrer les achats pour ne conserver que ceux avec des articles existants
        data_purchases = data_purchases[data_purchases['code_article'].isin(existing_articles)]
        print("Données après filtrage des articles existants :")
        print(data_purchases.head())

        if data_purchases.empty:
            print("Aucune donnée valide à insérer dans la table achats.")
            return "Aucune donnée valide à insérer.", 204

        # Insérer les données dans PostgreSQL
        try:
            data_purchases.to_sql('achats', con=engine, if_exists='append', index=False, method='multi')
            print("Données achats importées avec succès.")
            return "Données achats importées avec succès.", 200
        except Exception as e:
            print("Erreur lors de l'insertion des données achats :", e)
            print(traceback.format_exc())  # Affichage complet de l'erreur
            return f"Erreur lors de l'insertion des données achats : {e}", 500

    except Exception as e:
        print("Erreur lors de l'importation des achats :", e)
        print(traceback.format_exc())  # Affichage complet de l'erreur
        return f"Erreur lors de l'importation : {e}", 500

#affichage de la page palmares 
#affichage de la page palmares
@app.route("/sales_palmares")
def sales_palmares():
    # Utilisation du moteur SQLAlchemy pour la connexion
    engine = create_engine(DATABASE_URL)
    try:
        # Requête SQL corrigée
        query = text('''
        SELECT 
            p.code_article AS code_article,
            p.nom_produit,
            COALESCE(s.quantite_stock, 0) AS quantite_stock,
            lp.delai_reapprovisionnement,
            COALESCE(ROUND((SUM(CASE WHEN v.date_vente >= CURRENT_DATE - INTERVAL '30 days' 
                AND v.num_piece LIKE 'FA%' THEN v.quantite_vendue ELSE 0 END) / 30.0)::numeric, 0), 0) AS ventes_moy_30_jours,
            SUM(CASE WHEN EXTRACT(YEAR FROM v.date_vente) = 2023 AND v.num_piece LIKE 'FA%' OR v.num_piece LIKE 'CO%' THEN v.quantite_vendue ELSE 0 END) AS vente_2023,
            SUM(CASE WHEN EXTRACT(YEAR FROM v.date_vente) = 2024 AND v.num_piece LIKE 'FA%' OR v.num_piece LIKE 'CO%' THEN v.quantite_vendue ELSE 0 END) AS vente_2024,
            SUM(CASE WHEN EXTRACT(YEAR FROM v.date_vente) = 2025 AND v.num_piece LIKE 'FA%' OR v.num_piece LIKE 'CO%' THEN v.quantite_vendue ELSE 0 END) AS vente_2025
        FROM 
            produits p
        LEFT JOIN 
            stocks s ON p.code_article = s.code_article
        LEFT JOIN 
            logistiqueproduits lp ON p.code_article = lp.code_article
        LEFT JOIN 
            "Ventes" v ON p.code_article = v.code_article
        GROUP BY 
            p.code_article, p.nom_produit, s.quantite_stock, lp.delai_reapprovisionnement
        ORDER BY 
            vente_2025 DESC;
        ''')

        # Exécuter la requête avec pandas
        df = pd.read_sql_query(query, engine)

        # Vérification si la requête a retourné des résultats
        if df.empty:
            return "<h1>Aucune donnée disponible pour le palmarès des ventes.</h1>"

        # Ajouter la colonne "Alerte" avec les détails des calculs
        def calculate_alert(row):
            # Extraire les valeurs nécessaires
            delai = int(row['delai_reapprovisionnement']) if pd.notnull(row['delai_reapprovisionnement']) else 0
            ventes_moy_30 = int(row['ventes_moy_30_jours']) if pd.notnull(row['ventes_moy_30_jours']) else 0
            stock_actuel = int(row['quantite_stock']) if pd.notnull(row['quantite_stock']) else 0

            # Calculs
            stock_securite = ventes_moy_30 * 5
            seuil_reapprovisionnement = ventes_moy_30 * delai
            quantite_a_commander = max((stock_securite + seuil_reapprovisionnement) - stock_actuel, 0)

            # Vérifier si une commande est nécessaire
            if quantite_a_commander > 0:
                return f"Recommander: {quantite_a_commander}"
            else:
                return "OK"

        # Appliquer la fonction sur chaque ligne
        df['alerte'] = df.apply(calculate_alert, axis=1)

        # Convertir toutes les valeurs numériques en entiers pour l'affichage
        for col in ['quantite_stock', 'ventes_moy_30_jours', 'vente_2023', 'vente_2024', 'vente_2025']:
            df[col] = df[col].fillna(0).astype(int)

        # Convertir les données en dict pour affichage
        sales_data = df.to_dict(orient="records")

        # Renvoyer les données au template HTML
        return render_template("sales_palmares.html", sales=sales_data)

    except Exception as e:
        print(f"Erreur lors de l'exécution de la requête : {e}")
        return f"Erreur lors de l'exécution de la requête : {e}"

    finally:
        # Fermez correctement la connexion à la base de données
        engine.dispose()







        
#fonction pour la recherche
@app.route('/search')
def search():
    # Utilisez un moteur SQLAlchemy pour la connexion
    engine = create_engine(DATABASE_URL)
    query = request.args.get('q', '').strip().lower()  # Nettoyer et convertir la requête en minuscule
    if not query:
        return jsonify([])  # Retourne une liste vide si aucun mot-clé n'est fourni

    try:
        # Connexion à la base de données
        with engine.connect() as conn:
            search_query = text("""
                SELECT code_article, nom_produit
                FROM produits
                WHERE LOWER(code_article) LIKE :query OR LOWER(nom_produit) LIKE :query
                LIMIT 10
            """)
            results = conn.execute(search_query, {"query": f"%{query}%"}).fetchall()

            print(f"Requête reçue pour : {query}")  # Log pour debug

            # Retourner les résultats sous forme de JSON
            return jsonify([
                {"code_article": row[0], "nom_produit": row[1]}
                for row in results
            ])
    except Exception as e:
        print(f"Erreur lors de l'exécution de la requête de recherche : {e}")
        return jsonify({"error": "Une erreur s'est produite lors de la recherche"}), 500
        
        
#affichage de la page representant        
@app.route('/all_representative_sales')
def dynamic_representative_sales():
    engine = create_engine(DATABASE_URL)  # Remplacez par votre `DATABASE_URL`
    try:
        # Requête SQL mise à jour
        query = '''
        SELECT
            c.representant AS nom_representant,
            TO_CHAR(v.date_vente, 'YYYY-MM') AS mois,
            SUM(v.quantite_vendue * v.prix_achat) AS chiffre_affaire
        FROM
            "Ventes" v
        JOIN
            client c ON v.code_client = c.code_client
        WHERE
            v.code_client IN (
                SELECT DISTINCT v1.code_client
                FROM "Ventes" v1
                WHERE v1.date_vente >= CURRENT_DATE - INTERVAL '4 months' -- Dernière commande il y a plus de 6 mois
            )
        GROUP BY
            c.representant, TO_CHAR(v.date_vente, 'YYYY-MM')
        ORDER BY
            c.representant, mois;
        '''
        # Utilisation de `read_sql_query` avec le moteur SQLAlchemy
        sales_data = pd.read_sql_query(query, con=engine)

        # Vérifier si les données sont vides
        if sales_data.empty:
            return "<h1>Aucune donnée disponible pour les représentants.</h1>"

        # Transformation en tableau pivot pour créer des colonnes mois par mois
        sales_pivot = sales_data.pivot_table(
            index='nom_representant',
            columns='mois',
            values='chiffre_affaire',
            fill_value=0
        ).reset_index()

        # Calcul du chiffre d'affaires moyen pour chaque mois
        average_sales = sales_pivot.drop(columns=['nom_representant']).mean().to_dict()

        # Préparation des données pour le modèle
        representative_sales = sales_pivot.to_dict(orient='records')

        return render_template(
            'all_representative_sales.html',
            representative_sales=representative_sales,
            average_sales=average_sales
        )

    except Exception as e:
        return f"Erreur lors de l'exécution de la requête : {e}"

    finally:
        engine.dispose()



# Fonction pour obtenir les ventes mensuelles par représentant et le CA moyen
def get_monthly_sales_and_average():
    engine = create_engine(DATABASE_URL)

    try:
        # Étape 1 : Requête SQL pour obtenir les ventes mensuelles par représentant (uniquement les factures)
        query = '''
        SELECT
            c.representant AS nom_representant,
            TO_CHAR(v.date_vente, 'YYYY-MM') AS mois,
            SUM(v.quantite_vendue * v.prix_achat) AS chiffre_affaire
        FROM
            "Ventes" v
        JOIN
            client c ON v.code_client = c.code_client
        WHERE
            v.num_piece LIKE 'FA%'  -- Filtrer uniquement les factures
        GROUP BY
            c.representant, TO_CHAR(v.date_vente, 'YYYY-MM')
        ORDER BY
            c.representant, mois;
        '''
        sales_data = pd.read_sql_query(text(query), engine)

        # Vérifier s'il y a des données
        if sales_data.empty:
            print("Aucune donnée disponible pour les ventes.")
            return None, None

        # Étape 2 : Calcul du chiffre d'affaires moyen par mois
        average_sales = (
            sales_data.groupby('mois')['chiffre_affaire']
            .sum()  # Total du CA par mois
            / sales_data.groupby('mois')['nom_representant'].nunique()  # Nombre unique de représentants actifs
        ).reset_index()

        average_sales.columns = ['mois', 'ca_moyen']

        print("Données de vente mensuelles par représentant :")
        print(sales_data.head())

        print("Chiffre d'affaires moyen par mois :")
        print(average_sales.head())

        # Étape 3 : Création du diagramme avec Seaborn
        plt.figure(figsize=(12, 6))
        sns.lineplot(
            data=sales_data,
            x="mois",
            y="chiffre_affaire",
            hue="nom_representant",
            marker="o",
            linewidth=2
        )
        sns.lineplot(
            data=average_sales,
            x="mois",
            y="ca_moyen",
            color="black",
            linestyle="dashed",
            label="Moyenne"
        )

        plt.title("Chiffre d'affaires mensuel par représentant")
        plt.xlabel("Mois")
        plt.ylabel("Chiffre d'affaires (€)")
        plt.xticks(rotation=45)
        plt.legend(title="Représentant")
        plt.grid(True)
        plt.show()

        return sales_data, average_sales

    except Exception as e:
        print(f"Erreur lors de l'exécution de la requête : {e}")
        return None, None

    finally:
        engine.dispose()

# Appel de la fonction
get_monthly_sales_and_average()


@app.route("/representative_top_products/<representant>")
def representative_top_products(representant):
    engine = create_engine(DATABASE_URL)

    try:
        # Requête SQL mise à jour pour inclure la table `client` et utiliser le pivot `code_client`
        query = text('''
        SELECT
            p.code_article,
            p.nom_produit,
            SUM(v.quantite_vendue) AS quantite_totale,
            MAX(v.date_vente) AS derniere_commande
        FROM
            "Ventes" v
        JOIN
            produits p ON v.code_article = p.code_article
        JOIN
            client c ON v.code_client = c.code_client
        WHERE
            c.representant = :representant
            AND v.date_vente >= CURRENT_DATE - INTERVAL '24 months'
        GROUP BY
            p.code_article, p.nom_produit
        ORDER BY
            quantite_totale DESC
        LIMIT 50;
        ''')

        # Exécuter la requête avec le représentant passé en paramètre
        result = pd.read_sql_query(query, engine, params={"representant": representant})

        # Formater la colonne `derniere_commande` au format `jj/mm/aaaa`
        result["derniere_commande"] = pd.to_datetime(result["derniere_commande"]).dt.strftime('%d/%m/%Y')

        return result.to_dict(orient="records")

    except Exception as e:
        print(f"Erreur lors de l'exécution de la requête : {e}")
        return {"error": str(e)}, 500

    finally:
        engine.dispose()


# Route pour afficher les ventes mensuelles par pharmacie pour un produit
@app.route('/product/<code_article>/monthly_sales')
def monthly_sales(code_article):
    # Obtenir les ventes mensuelles par pharmacie
    monthly_sales_data = get_monthly_sales_by_pharmacy(code_article)

    # Si aucune donnée n'est retournée, afficher un message approprié
    if monthly_sales_data is None or monthly_sales_data.empty:
        return f"<h1>Aucune donnée de vente disponible pour le produit : {code_article}</h1>"

    # Rendu de la page HTML avec les données
    return render_template(
        'monthly_sales.html',
        tables=monthly_sales_data.to_dict(orient='records'),
        code_article=code_article
    )


# Fonction pour obtenir les ventes mensuelles par pharmacie pour un produit spécifique
def get_monthly_sales_by_pharmacy(code_article):
    engine = create_engine(DATABASE_URL)  # Créez un moteur SQLAlchemy
    query = '''
    SELECT
        c.code_client AS code_client,
        c.nom_client AS nom_pharmacie,
        c.representant AS nom_representant,
        TO_CHAR(v.date_vente, 'YYYY-MM') AS mois,
        SUM(v.quantite_vendue * v.prix_achat) AS chiffre_affaire
    FROM
        "Ventes" v
    JOIN
        Client c ON v.code_client = c.code_client
    WHERE
        v.code_article = %(code_article)s
    GROUP BY
        c.code_client, c.nom_client, c.representant, TO_CHAR(v.date_vente, 'YYYY-MM')
    ORDER BY
        c.nom_client, mois;
    '''
    try:
        # Exécutez la requête avec SQLAlchemy
        sales_data = pd.read_sql_query(query, con=engine, params={'code_article': code_article})

        # Transformation en table pivot
        if not sales_data.empty:
            sales_pivot = sales_data.pivot_table(
                index=['code_client', 'nom_pharmacie', 'nom_representant'],
                columns='mois',
                values='chiffre_affaire',
                fill_value=0
            ).reset_index()
        else:
            sales_pivot = pd.DataFrame(columns=['code_client', 'nom_pharmacie', 'nom_representant'])

        print(f"Ventes mensuelles par pharmacie pour le produit {code_article} :")
        print(sales_pivot)
        return sales_pivot
    except Exception as e:
        print(f"Erreur lors de la récupération des ventes mensuelles par pharmacie : {e}")
        return None
    finally:
        engine.dispose()  # Disposez du moteur SQLAlchemy pour libérer les ressources


# Route pour afficher les ventes, produits reçus et produits commandés mensuels par produit
@app.route('/product/<code_article>/monthly_sales_product')
def monthly_sales_product(code_article):
    monthly_data = get_monthly_sales_and_purchases(code_article)
    if monthly_data is None or monthly_data.empty:
        return f"<h1>Aucune donnée disponible pour le produit : {code_article}</h1>"
    return render_template('monthly_sales_product.html', tables=monthly_data.to_dict(orient='records'), code_article=code_article)


# Fonction pour obtenir les ventes, achats et commandes mensuels pour un produit spécifique
def get_monthly_sales_and_purchases(code_article):
    engine = create_engine(DATABASE_URL)  # Créez un moteur SQLAlchemy

    try:
        # Requête pour les ventes
        sales_query = '''
        SELECT
            TO_CHAR(date_vente, 'YYYY-MM') AS mois,
            SUM(quantite_vendue) AS quantite_vendue
        FROM
            "Ventes"
        WHERE
            code_article = %s
        GROUP BY
            mois
        ORDER BY
            mois;
        '''
        sales_data = pd.read_sql_query(sales_query, engine, params=(code_article,))  # Passez un tuple

        # Requête pour les produits reçus
        received_query = '''
        SELECT
            TO_CHAR(date_document, 'YYYY-MM') AS mois,
            SUM(quantite) AS quantite_achetee
        FROM
            "achats"
        WHERE
            code_article = %s AND code_document = 16
        GROUP BY
            mois
        ORDER BY
            mois;
        '''
        received_data = pd.read_sql_query(received_query, engine, params=(code_article,))  # Passez un tuple

        # Requête pour les produits commandés
        ordered_query = '''
        SELECT
            TO_CHAR(date_document, 'YYYY-MM') AS mois,
            SUM(quantite) AS quantite_commandee
        FROM
            "achats"
        WHERE
            code_article = %s AND code_document = 12
        GROUP BY
            mois
        ORDER BY
            mois;
        '''
        ordered_data = pd.read_sql_query(ordered_query, engine, params=(code_article,))  # Passez un tuple

        # Fusionner les données
        combined_data = pd.merge(sales_data, received_data, on='mois', how='outer', suffixes=('_v', '_r')).fillna(0)
        combined_data = pd.merge(combined_data, ordered_data, on='mois', how='outer', suffixes=('', '_o')).fillna(0)

        # Convertir les colonnes en types numériques
        combined_data['quantite_vendue'] = pd.to_numeric(combined_data['quantite_vendue'], errors='coerce').fillna(0).astype(int)
        combined_data['quantite_achetee'] = pd.to_numeric(combined_data['quantite_achetee'], errors='coerce').fillna(0).astype(int)
        combined_data['quantite_commandee'] = pd.to_numeric(combined_data['quantite_commandee'], errors='coerce').fillna(0).astype(int)

        print(f"Données combinées pour le produit {code_article} :")
        print(combined_data)

        return combined_data
    except Exception as e:
        print(f"Erreur lors de la récupération des données pour le produit {code_article} : {e}")
        return None
    finally:
        engine.dispose()  # Ferme le moteur proprement



# Route pour afficher les ventes par représentant PAR PRODUIT
@app.route('/product/<code_article>')
def product_sales(code_article):
    try:
        sales_data = get_sales_by_representative(code_article)
        if sales_data.empty:
            return f"<h1>Aucune donnée de vente trouvée pour le produit {code_article}.</h1>"

        return render_template(
            'product_sales.html',
            tables=sales_data.to_dict(orient='records'),
            code_article=code_article
        )
    except Exception as e:
        return f"Erreur lors de la récupération des ventes pour le produit {code_article} : {e}"

# Fonction pour obtenir les ventes par représentant pour un produit spécifique
def get_sales_by_representative(code_article):
    engine = create_engine(DATABASE_URL)  # Utilise SQLAlchemy pour la connexion

    query = '''
    SELECT
        COALESCE(c.representant, 'Inconnu') AS nom_representant,
        p.nom_produit,
        SUM(CASE WHEN EXTRACT(YEAR FROM v.date_vente) = 2023 THEN v.quantite_vendue ELSE 0 END) AS vente_2023,
        SUM(CASE WHEN EXTRACT(YEAR FROM v.date_vente) = 2024 THEN v.quantite_vendue ELSE 0 END) AS vente_2024,
        SUM(CASE WHEN EXTRACT(YEAR FROM v.date_vente) = 2025 THEN v.quantite_vendue ELSE 0 END) AS vente_2025
    FROM
        "Ventes" v
    LEFT JOIN
        "produits" p ON v.code_article = p.code_article
    LEFT JOIN
        "client" c ON v.code_client = c.code_client
    WHERE
        v.code_article = %s
    GROUP BY
        c.representant, p.nom_produit
    ORDER BY
        vente_2024 DESC, vente_2023 DESC, vente_2025 DESC;
    '''
    try:
        result = pd.read_sql_query(query, engine, params=(code_article,))
        print(f"Données récupérées pour le produit {code_article} :")
        print(result)
        return result
    except Exception as e:
        print(f"Erreur lors de la récupération des ventes pour le produit {code_article} : {e}")
        raise
    finally:
        engine.dispose()  # Ferme proprement le moteur SQLAlchemy


# Route pour afficher le formulaire d'ajout ou de modification des détails d'un produit
@app.route('/add_product_form')
def add_product_form():
    engine = create_engine(DATABASE_URL)  # Utilise SQLAlchemy pour la connexion
    code_article = request.args.get('code_article', '')
    existing_data = None

    if code_article:
        with engine.connect() as conn:
            query = """
                SELECT code_article, poids, nb_par_carton, largeur_carton, longueur_carton, hauteur_carton, 
                       poids_carton, delai_reapprovisionnement
                FROM logistiqueproduits
                WHERE code_article = :code_article;
            """
            result = conn.execute(text(query), {"code_article": code_article}).fetchone()

            if result:
                # Convertir le résultat en dictionnaire pour faciliter l'accès dans le template
                existing_data = dict(result)

    return render_template('add_product_form.html', code_article=code_article, existing_data=existing_data)

# Route pour traiter le formulaire et insérer ou mettre à jour les données
@app.route('/add_product_details', methods=['POST'])
def add_product_details():
    engine = create_engine(DATABASE_URL)  # Utilise SQLAlchemy pour la connexion
    # Récupérer les données du formulaire
    code_article = request.form['code_article']
    poids = request.form['poids']
    nb_par_carton = request.form['nb_par_carton']
    largeur_carton = request.form['largeur_carton']
    longueur_carton = request.form['longueur_carton']
    hauteur_carton = request.form['hauteur_carton']
    poids_carton = request.form['poids_carton']
    delai_reapprovisionnement = request.form['delai_reapprovisionnement']

    try:
        with engine.connect() as conn:
            transaction = conn.begin()  # Démarre une transaction

            try:
                # Vérifier si des données logistiques existent déjà pour ce produit
                check_query = "SELECT 1 FROM logistiqueproduits WHERE code_article = :code_article;"
                existing_entry = conn.execute(text(check_query), {"code_article": code_article}).fetchone()

                if existing_entry:
                    # Si les données existent, les mettre à jour
                    update_query = """
                        UPDATE logistiqueproduits
                        SET poids = :poids, nb_par_carton = :nb_par_carton, largeur_carton = :largeur_carton, 
                            longueur_carton = :longueur_carton, hauteur_carton = :hauteur_carton, 
                            poids_carton = :poids_carton, delai_reapprovisionnement = :delai_reapprovisionnement
                        WHERE code_article = :code_article;
                    """
                    conn.execute(text(update_query), {
                        "poids": poids,
                        "nb_par_carton": nb_par_carton,
                        "largeur_carton": largeur_carton,
                        "longueur_carton": longueur_carton,
                        "hauteur_carton": hauteur_carton,
                        "poids_carton": poids_carton,
                        "delai_reapprovisionnement": delai_reapprovisionnement,
                        "code_article": code_article
                    })
                    message = f"Les détails du produit {code_article} ont été mis à jour avec succès."
                else:
                    # Sinon, insérer une nouvelle entrée
                    insert_query = """
                        INSERT INTO logistiqueproduits 
                        (code_article, poids, nb_par_carton, largeur_carton, longueur_carton, hauteur_carton, 
                         poids_carton, delai_reapprovisionnement)
                        VALUES (:code_article, :poids, :nb_par_carton, :largeur_carton, :longueur_carton, 
                                :hauteur_carton, :poids_carton, :delai_reapprovisionnement);
                    """
                    conn.execute(text(insert_query), {
                        "code_article": code_article,
                        "poids": poids,
                        "nb_par_carton": nb_par_carton,
                        "largeur_carton": largeur_carton,
                        "longueur_carton": longueur_carton,
                        "hauteur_carton": hauteur_carton,
                        "poids_carton": poids_carton,
                        "delai_reapprovisionnement": delai_reapprovisionnement
                    })
                    message = f"Les détails du produit {code_article} ont été ajoutés avec succès."

                transaction.commit()  # Valider la transaction

            except Exception as e:
                transaction.rollback()  # Annuler la transaction en cas d'erreur
                return f"Erreur lors de l'ajout ou de la mise à jour des détails du produit : {e}"

        return message

    except Exception as e:
        return f"Erreur lors de la connexion ou de l'exécution de la requête : {e}"
        

@app.route('/afficheproduit/<code_article>')
def product_details_route(code_article):
    engine = create_engine(DATABASE_URL)  # Utilise SQLAlchemy pour la connexion
    try:
        with engine.connect() as conn:
            # Récupérer les détails du produit
            query_product_details = text("""
                SELECT 
                    p.code_article, p.nom_produit, 
                    lp.poids, lp.nb_par_carton, lp.largeur_carton, 
                    lp.longueur_carton, lp.hauteur_carton, lp.poids_carton,
                    lp.delai_reapprovisionnement
                FROM produits p
                    LEFT JOIN logistiqueproduits lp ON p.code_article = lp.code_article
                WHERE p.code_article = :code_article
            """)
            product_details = conn.execute(query_product_details, {"code_article": code_article}).fetchone()

            if not product_details:
                return f"Produit avec le code {code_article} introuvable.", 404

            # Calculer le stock moyen
            query_received = text("""
                SELECT SUM(quantite) AS total_recu
                FROM achats
                WHERE code_article = :code_article
            """)
            total_recu = conn.execute(query_received, {"code_article": code_article}).scalar() or 0

            query_sold = text("""
                SELECT SUM(quantite_vendue) AS total_vendu
                FROM "Ventes"
                WHERE code_article = :code_article
            """)
            total_vendu = conn.execute(query_sold, {"code_article": code_article}).scalar() or 0

            stock_moyen = total_recu - total_vendu

            # Calculer la quantité moyenne mensuelle vendue sur les 12 derniers mois
            query_avg_monthly_sales = text("""
                SELECT AVG(monthly_sales.total) AS avg_monthly_sales
                FROM (
                SELECT SUM(v.quantite_vendue) AS total
                FROM "Ventes" v
                WHERE v.code_article = :code_article 
                AND v.date_vente >= CURRENT_DATE - INTERVAL '12 months'
                GROUP BY DATE_TRUNC('month', v.date_vente)
                ) AS monthly_sales
            """)
            avg_monthly_sales = conn.execute(query_avg_monthly_sales, {"code_article": code_article}).scalar() or 0

            avg_daily_sales = avg_monthly_sales / 30 if avg_monthly_sales else 0
            delai_reapprovisionnement = product_details[8] or 0
            stock_securite_total = round(avg_daily_sales * delai_reapprovisionnement + avg_monthly_sales, 2)

            # Récupérer le stock actuel
            query_current_stock = text("""
                SELECT quantite_stock
                FROM stocks
                WHERE code_article = :code_article
            """)
            current_stock = conn.execute(query_current_stock, {"code_article": code_article}).scalar() or 0

            # Récupérer les données mensuelles des ventes
            query_monthly_data = text("""
                SELECT TO_CHAR(date_vente, 'YYYY-MM') AS mois,
                       SUM(quantite_vendue) AS total_vendu
                FROM "Ventes"
                WHERE code_article = :code_article
                GROUP BY TO_CHAR(date_vente, 'YYYY-MM')
                ORDER BY mois ASC
            """)
            ventes_mensuelles = conn.execute(query_monthly_data, {"code_article": code_article}).fetchall()

            # Récupérer les données mensuelles des achats
            query_stock_monthly_data = text("""
                SELECT TO_CHAR(date_document, 'YYYY-MM') AS mois,
                       SUM(quantite) AS total_stock
                FROM achats
                WHERE code_article = :code_article AND code_document = 16
                GROUP BY TO_CHAR(date_document, 'YYYY-MM')
                ORDER BY mois ASC 
            """)
            stocks_mensuels = conn.execute(query_stock_monthly_data, {"code_article": code_article}).fetchall()

            # Structurer les données pour le graphique en filtrant les dates invalides
            mois_labels = sorted({row[0] for row in ventes_mensuelles if row[0]} | {row[0] for row in stocks_mensuels if row[0]})
            ventes_dict = {row[0]: row[1] for row in ventes_mensuelles if row[0]}
            stocks_dict = {row[0]: row[1] for row in stocks_mensuels if row[0]}
            data_ventes = [ventes_dict.get(mois, 0) for mois in mois_labels]
            data_stocks = [stocks_dict.get(mois, 0) for mois in mois_labels]

            # Rendre la page HTML
            return render_template('product_details.html',
                                   product={
                                       'code_article': product_details[0],
                                       'nom_produit': product_details[1],
                                       'poids': product_details[2],
                                       'nb_par_carton': product_details[3],
                                       'largeur_carton': product_details[4],
                                       'longueur_carton': product_details[5],
                                       'hauteur_carton': product_details[6],
                                       'poids_carton': product_details[7],
                                       'delai_reapprovisionnement': delai_reapprovisionnement,
                                       'stock_moyen': stock_moyen,
                                       'avg_monthly_sales': round(avg_monthly_sales, 2),
                                       'avg_daily_sales': round(avg_daily_sales, 2),
                                       'stock_securite_total': stock_securite_total,
                                       'current_stock': current_stock
                                   },
                                   chart_data={
                                       'labels': mois_labels,
                                       'ventes': data_ventes,
                                       'stocks': data_stocks
                                   })
    except Exception as e:
        print(f"Erreur lors de la récupération des détails du produit : {e}")
        return f"Erreur lors de la récupération des détails du produit : {e}", 500  



@app.route('/')
def dashboard():
    engine = create_engine(DATABASE_URL)  # Utilise SQLAlchemy pour la connexion
    try:
        with engine.connect() as conn:
            # 1. Chiffre d'affaires global du mois
            ca_mois = conn.execute(text("""
                SELECT 
                    COALESCE(SUM(quantite_vendue * prix_achat), 0) AS ca_mois
                FROM "Ventes"
                WHERE DATE_TRUNC('month', date_vente) = DATE_TRUNC('month', CURRENT_DATE);
            """)).scalar() or 0

            # 2. Évolution du chiffre d'affaires
            evolution_data = conn.execute(text("""
                WITH ca_courant AS (
                    SELECT 
                        COALESCE(SUM(quantite_vendue * prix_achat), 0) AS ca_mois_courant
                    FROM "Ventes"
                    WHERE DATE_TRUNC('month', date_vente) = DATE_TRUNC('month', CURRENT_DATE)
                ),
                ca_annee_precedente AS (
                    SELECT 
                        COALESCE(SUM(quantite_vendue * prix_achat), 0) AS ca_mois_precedent
                    FROM "Ventes"
                    WHERE DATE_TRUNC('month', date_vente) = DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 year'
                )
                SELECT 
                    CAST(ROUND(ca_courant.ca_mois_courant) AS INTEGER) AS ca_mois_courant,
                    CAST(ROUND(ca_annee_precedente.ca_mois_precedent) AS INTEGER) AS ca_mois_precedent,
                    CAST(ROUND(
                        ((ca_courant.ca_mois_courant - ca_annee_precedente.ca_mois_precedent) 
                        / NULLIF(ca_annee_precedente.ca_mois_precedent, 0)) * 100
                    ) AS INTEGER) AS evolution
                FROM ca_courant, ca_annee_precedente;
            """)).fetchone()

            ca_mois_courant = evolution_data[0] or 0
            ca_mois_precedent = evolution_data[1] or 0
            evolution = evolution_data[2] or 0

            # 3. Top 10 des produits les plus vendus
            top_products = conn.execute(text("""
                SELECT 
                    v.code_article,
                    p.nom_produit,
                    SUM(v.quantite_vendue) AS quantite_totale,
                    CAST(SUM(v.quantite_vendue * v.prix_achat) AS INTEGER) AS chiffre_affaire
                FROM "Ventes" v
                JOIN produits p ON v.code_article = p.code_article
                WHERE DATE_TRUNC('month', v.date_vente) = DATE_TRUNC('month', CURRENT_DATE)
                GROUP BY v.code_article, p.nom_produit
                ORDER BY quantite_totale DESC
                LIMIT 10;
            """)).fetchall()

            # 4. Top 5 des représentants ayant fait le plus de chiffre
            top_representatives = conn.execute(text("""
                SELECT 
                    c.representant AS nom_representant,
                    CAST(SUM(v.quantite_vendue * v.prix_achat) AS INTEGER) AS chiffre_affaire
                FROM "Ventes" v
                JOIN client c ON v.code_client = c.code_client
                WHERE DATE_TRUNC('month', v.date_vente) = DATE_TRUNC('month', CURRENT_DATE)
                GROUP BY c.representant
                ORDER BY chiffre_affaire DESC
                LIMIT 5;
            """)).fetchall()

        # Retourne les données pour affichage
        return render_template(
            'dashboard.html', 
            ca_mois=ca_mois_courant,
            evolution=evolution,
            top_products=top_products,
            top_representatives=top_representatives
        )
    except Exception as e:
        return f"Erreur lors du chargement du tableau de bord : {e}", 500
        


# gestion de la carte des representants
@app.route('/carte_ventes_agents')
def carte_ventes_agents():
    engine = create_engine(DATABASE_URL)
    try:
        # Charger le fichier departements.csv
        department_mapping = pd.read_csv("./data/departements.csv")
        department_mapping["code"] = department_mapping["code"].astype(str).str.zfill(2)

        # Récupérer les données des ventes et agents
        query = text("""
            SELECT
                LEFT(c.cp::TEXT, 2) AS code_departement,
                COUNT(DISTINCT c.code_client) AS nb_clients,
                STRING_AGG(DISTINCT c.representant, ', ') AS nom_agents
            FROM client c
            JOIN "Ventes" v ON c.code_client = v.code_client
            WHERE v.date_vente >= '2024-01-01' AND v.date_vente < '2025-01-01'
            GROUP BY LEFT(c.cp::TEXT, 2)
        """)
        data = pd.read_sql_query(query, engine)
        data["code_departement"] = data["code_departement"].astype(str).str.zfill(2)

        # Charger les données géographiques
        france_departments = gpd.read_file("https://france-geojson.gregoiredavid.fr/repo/departements.geojson")
        france_departments["code"] = france_departments["code"].astype(str).str.zfill(2)

        # Fusionner les données
        data.rename(columns={"code_departement": "code"}, inplace=True)
        map_data = france_departments.merge(data, on="code", how="left")
        map_data = map_data.merge(department_mapping, on="code", how="left")
        map_data["nom"] = map_data["nom_x"].combine_first(map_data["nom_y"])
        map_data.drop(columns=["nom_x", "nom_y"], inplace=True)

        # Calculer le ratio
        map_data["ratio_clients_pharmacies"] = (
            map_data["nb_clients"] / map_data["nb_pharmacies"]
        ).fillna(0).round(2)

        # Convertir les géométries en GeoJSON
        map_data["geometry"] = map_data["geometry"].apply(lambda geom: geom.__geo_interface__ if geom else None)

        # Générer les données à transmettre au template
        department_data = map_data[[
            "code", "nom", "geometry", "nb_clients", "nom_agents", "nb_pharmacies", "ratio_clients_pharmacies"
        ]].to_dict(orient="records")
        department_data = map_data.apply(
            lambda row: {
                "type": "Feature",
                "properties": {
                    "code": row["code"],
                    "nom": row["nom"],
                    "nb_clients": row["nb_clients"] or 0,
                    "nom_agents": row["nom_agents"] or "Aucun",
                    "nb_pharmacies": row["nb_pharmacies"] or 0,
                    "ratio_clients_pharmacies": row["ratio_clients_pharmacies"] or 0
                },
                "geometry": row["geometry"]
            },
            axis=1
        ).tolist()



        agent_data = (
            data.explode("nom_agents")
            .groupby("nom_agents")
            .agg({"code": lambda x: list(x)})
            .reset_index()
        )
        agent_data.rename(columns={"nom_agents": "nom", "code": "departments"}, inplace=True)
        agent_data = agent_data.to_dict(orient="records")

        # Vérification des données
        if not department_data:
            raise ValueError("Les données des départements sont vides ou mal formatées.")
        if not agent_data:
            raise ValueError("Les données des agents sont vides ou mal formatées.")

        # Passer les données au template
        return render_template(
            "carte_ventes_agents.html",
            department_data=json.dumps(department_data),  # Sérialisation en JSON
            agent_data=json.dumps(agent_data),            # Sérialisation en JSON
        )

    except Exception as e:
        print(f"Erreur lors de la génération des données : {e}")
        return f"Erreur lors de la génération de la carte : {e}", 500


from datetime import datetime, timedelta

@app.route('/backorders')
def backorders():
    engine = create_engine(DATABASE_URL)
    try:
        # Calcul des bornes de date
        three_months_ago = datetime.today() - timedelta(days=90)  # Limite max : 3 mois
        three_days_ago = datetime.today() - timedelta(days=3)      # Limite min : 3 jours

        query = text("""
            SELECT 
                p.code_article, 
                p.nom_produit, 
                v.num_piece AS bon_de_commande, 
                c.nom_client AS pharmacie, 
                v.quantite_vendue AS quantite_commande, 
                v.date_vente AS date_commande
            FROM "Ventes" v
            JOIN produits p ON v.code_article = p.code_article
            JOIN client c ON v.code_client = c.code_client
            WHERE v.num_piece LIKE 'CO%' -- Ne garder que les bons de commande
            AND v.date_vente BETWEEN :date_limite_min AND :date_limite_max -- Filtrer entre 3 jours et 3 mois
            ORDER BY p.code_article, v.date_vente DESC
        """)

        with engine.connect() as connection:
            result = connection.execute(query, {
                "date_limite_min": three_months_ago,
                "date_limite_max": three_days_ago
            })
            backorders_data = result.fetchall()
        
        # Transformer les résultats en dictionnaire regroupé par code_article
        backorders_dict = {}
        for row in backorders_data:
            code_article = row[0]
            if code_article not in backorders_dict:
                backorders_dict[code_article] = {
                    "nom_produit": row[1],
                    "quantite_totale": 0,  # Initialisation de la quantité totale
                    "commandes": []
                }
            backorders_dict[code_article]["quantite_totale"] += int(row[4])  # Conversion en entier

            # Ajouter les commandes filtrées à la liste
            backorders_dict[code_article]["commandes"].append({
                "bon_de_commande": row[2],
                "pharmacie": row[3],
                "quantite_commande": int(row[4]),  # Conversion en entier
                "date_commande": row[5]
            })

        return render_template("backorders.html", backorders=backorders_dict)

    except Exception as e:
        print(f"Erreur lors de la récupération des backorders : {e}")
        return f"Erreur lors de la récupération des backorders : {e}", 500



#affichage du palmares des pharmacies
from datetime import datetime, timedelta

@app.route("/pharmacies")
def pharmacies():
    engine = create_engine(DATABASE_URL)
    
    try:
        query = text('''
        SELECT 
            c.code_client, 
            c.nom_client AS pharmacie, 
            c.representant AS agent_commercial,
            MAX(v.date_vente) AS derniere_commande,
            COUNT(v.num_piece) AS nombre_commandes,
            SUM(SUM(v.quantite_vendue * v.prix_achat)) OVER(PARTITION BY c.code_client) AS ca_total
        FROM 
            "Ventes" v
        JOIN 
            client c ON v.code_client = c.code_client
        WHERE 
            v.num_piece LIKE 'FA%'  -- Uniquement les factures
        GROUP BY 
            c.code_client, c.nom_client, c.representant
        ORDER BY 
            ca_total DESC;
        ''')

        # Exécuter la requête avec pandas
        df = pd.read_sql_query(query, engine)

        if df.empty:
            return "<h1>Aucune donnée disponible pour les pharmacies.</h1>"

        # Convertir les dates et les valeurs numériques
        df["derniere_commande"] = pd.to_datetime(df["derniere_commande"])
        df["ca_total"] = df["ca_total"].fillna(0).astype(int)

        # Structurer les données pour affichage
        pharmacies_data = df.to_dict(orient="records")

        # Passer `timedelta` et `datetime` au template
        return render_template("pharmacies.html", pharmacies=pharmacies_data, now=datetime.utcnow(), timedelta=timedelta)

    except Exception as e:
        print(f"Erreur lors de l'exécution de la requête : {e}")
        return f"Erreur lors de l'exécution de la requête : {e}", 500

    finally:
        engine.dispose()



from datetime import datetime, timedelta

@app.route("/pharmacy_sales/<code_client>")
def pharmacy_sales(code_client):
    engine = create_engine(DATABASE_URL)
    
    try:
        query = text('''
        SELECT 
            TO_CHAR(v.date_vente, 'YYYY-MM') AS mois_annee,
            SUM(v.quantite_vendue * v.prix_achat) AS ca_mensuel
        FROM 
            "Ventes" v
        WHERE 
            v.code_client = :code_client
            AND v.num_piece LIKE 'FA%'  -- Uniquement les factures
            AND v.date_vente >= CURRENT_DATE - INTERVAL '24 months'
        GROUP BY 
            TO_CHAR(v.date_vente, 'YYYY-MM')
        ORDER BY 
            TO_CHAR(v.date_vente, 'YYYY-MM') ASC;
        ''')

        # Exécuter la requête
        result = pd.read_sql_query(query, engine, params={"code_client": code_client})

        # Générer une liste des 24 derniers mois
        today = datetime.today()
        months = [(today - timedelta(days=30 * i)).strftime("%Y-%m") for i in range(23, -1, -1)]

        # Créer un dictionnaire pour les données
        sales_data = {row["mois_annee"]: int(row["ca_mensuel"]) for _, row in result.iterrows()}

        # Compléter les mois manquants avec 0
        labels = []
        data = []
        for month in months:
            labels.append(datetime.strptime(month, "%Y-%m").strftime("%b %Y"))  # Format Mois Année (ex: Jan 2023)
            data.append(sales_data.get(month, 0))  # Valeur ou 0 si le mois est absent

        return {"labels": labels, "data": data}

    except Exception as e:
        print(f"Erreur lors de l'exécution de la requête : {e}")
        return {"error": str(e)}, 500

    finally:
        engine.dispose()

     


@app.route("/import_clients")
def import_clients():
    import_client_data()
    return "Importation des données clients terminée."

@app.route("/import_stocks")
def import_stocks():
    import_stock_data()
    return "Importation des données stocks terminée."

@app.route("/import_products")
def import_products():
    import_product_data()
    return "Importation des données produits terminée."

@app.route("/import_sales")
def import_sales():
    import_sales_data()
    return "Importation des données ventes terminée."

@app.route("/import_purchases")
def import_purchases():
    import_purchase_data()
    return "Importation des données achats terminée."

    
# Route principale pour afficher le palmarès
@app.route('/')
def palmares():
    order_by = request.args.get('order_by', 'vente_2024 DESC')
    palmares_data = get_palmares(order_by)
    return render_template('palmares.html', tables=palmares_data.to_dict(orient='records'), order_by=order_by)    

    
@app.route('/test/<name>')
def test_dynamic_route(name):
    return f"Bonjour, {name} !"  
    
    

if __name__ == '__main__':
    create_tables()
    create_product_table()
    app.run(debug=True)
    app.config['DEBUG'] = True


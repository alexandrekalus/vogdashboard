# Vérifiez si la colonne existe avant de tenter de la supprimer
def manage_logistique_produits_table():
    conn = get_db_connection()
    if conn:
        try:
            # Vérifiez si la colonne 'stock_securite' existe dans la table LogistiqueProduits
            query_check_column = """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'logistiqueproduits' AND column_name = 'stock_securite';
            """
            with conn.cursor() as cursor:
                cursor.execute(query_check_column)
                result = cursor.fetchone()

                if result:
                    # Si la colonne existe, recréer la table sans cette colonne
                    query_create_new_table = """
                        CREATE TABLE logistiqueproduits_new AS
                        SELECT code_article, poids, nb_par_carton, largeur_carton, longueur_carton,
                               hauteur_carton, poids_carton, delai_reapprovisionnement
                        FROM logistiqueproduits;
                    """
                    query_drop_old_table = "DROP TABLE logistiqueproduits;"
                    query_rename_new_table = "ALTER TABLE logistiqueproduits_new RENAME TO logistiqueproduits;"

                    cursor.execute(query_create_new_table)
                    cursor.execute(query_drop_old_table)
                    cursor.execute(query_rename_new_table)
                    print("Colonne 'stock_securite' supprimée avec succès.")
                else:
                    print("La colonne 'stock_securite' n'existe pas.")
            
            conn.commit()
        except Exception as e:
            print(f"Erreur lors de la gestion de la table LogistiqueProduits : {e}")
        finally:
            conn.close()
    else:
        print("Impossible de se connecter à la base de données PostgreSQL.")

def create_tables():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Créer les tables nécessaires
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Produits (
                code_article TEXT PRIMARY KEY,
                nom_produit TEXT,
                poids REAL DEFAULT 0,
                nb_par_carton INTEGER DEFAULT 0,
                largeur_carton REAL DEFAULT 0,
                longueur_carton REAL DEFAULT 0,
                hauteur_carton REAL DEFAULT 0,
                poids_carton REAL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS Stocks (
                code_article TEXT,
                quantite_stock INTEGER,
                FOREIGN KEY (code_article) REFERENCES Produits (code_article)
            );

            CREATE TABLE IF NOT EXISTS Ventes (
                id_vente SERIAL PRIMARY KEY,
                code_article TEXT,
                date_vente DATE,
                quantite_vendue INTEGER,
                prix_achat REAL,
                nom_representant TEXT,
                code_client TEXT
            );

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

            CREATE TABLE IF NOT EXISTS Client (
                code_client TEXT PRIMARY KEY,
                nom_client TEXT,
                representant TEXT,
                tel TEXT,
                email TEXT,
                date_creation DATE,
                adresse TEXT,
                cp TEXT,
                ville TEXT,
                pays TEXT
            );
            """)
            conn.commit()
            print("Tables créées avec succès.")
        except Exception as e:
            print(f"Erreur lors de la création des tables : {e}")
        finally:
            conn.close()


def recreate_database():
    conn = get_db_connection()
    if not conn:
        print("Impossible de se connecter à la base de données PostgreSQL.")
        return
    
    try:
        cursor = conn.cursor()

        # Création de la table LogistiqueProduits (si elle n'existe pas déjà)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS LogistiqueProduits (
            code_article TEXT PRIMARY KEY,
            poids REAL,
            nb_par_carton INTEGER,
            largeur_carton REAL,
            longueur_carton REAL,
            hauteur_carton REAL,
            poids_carton REAL,
            delai_reapprovisionnement INTEGER,
            FOREIGN KEY (code_article) REFERENCES Produits (code_article)
        );
        """)

        # Recréation des tables (supprimer et recréer)
        cursor.execute("DROP TABLE IF EXISTS Produits CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS Stocks CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS Ventes CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS Achats CASCADE;")

        # Création des tables avec la structure mise à jour
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
            FOREIGN KEY (code_article) REFERENCES Produits (code_article) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE Ventes (
            id_vente SERIAL PRIMARY KEY,
            code_article TEXT,
            date_vente DATE,
            quantite_vendue INTEGER,
            prix_achat NUMERIC,
            nom_representant TEXT,
            pharmacie TEXT,
            FOREIGN KEY (code_article) REFERENCES Produits (code_article) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE Achats (
            id_achat SERIAL PRIMARY KEY,
            code_document INTEGER,
            numero_document TEXT,
            date_document DATE,
            fournisseur TEXT,
            quantite INTEGER,
            code_article TEXT,
            FOREIGN KEY (code_article) REFERENCES Produits (code_article) ON DELETE CASCADE
        );
        """)

        conn.commit()
        print("Base de données recréée avec succès.")
    except Exception as e:
        print(f"Erreur lors de la recréation de la base de données : {e}")
    finally:
        conn.close()

# Test de connexion et affichage des données
conn = get_db_connection()
if conn:
    try:
        query = "SELECT * FROM Achats LIMIT 5;"
        df = pd.read_sql_query(query, conn)
        print(df)
    except Exception as e:
        print(f"Erreur lors de l'exécution de la requête : {e}")
    finally:
        conn.close()
else:
    print("Impossible de se connecter à la base de données.")

    
    
    
def update_database_schema():
    conn = get_db_connection()
    if not conn:
        print("Impossible de se connecter à la base PostgreSQL.")
        return

    try:
        cursor = conn.cursor()
        
        # Ajouter la colonne delai_reapprovisionnement si elle n'existe pas
        try:
            cursor.execute("""
                ALTER TABLE LogistiqueProduits ADD COLUMN delai_reapprovisionnement INTEGER;
            """)
            print("Colonne 'delai_reapprovisionnement' ajoutée avec succès.")
        except psycopg2.errors.DuplicateColumn as e:
            print(f"Colonne 'delai_reapprovisionnement' déjà existante : {e}")

        # Ajouter la colonne stock_securite si elle n'existe pas
        try:
            cursor.execute("""
                ALTER TABLE LogistiqueProduits ADD COLUMN stock_securite INTEGER;
            """)
            print("Colonne 'stock_securite' ajoutée avec succès.")
        except psycopg2.errors.DuplicateColumn as e:
            print(f"Colonne 'stock_securite' déjà existante : {e}")

        conn.commit()
    except Exception as e:
        print(f"Erreur lors de la mise à jour du schéma de la base de données : {e}")
    finally:
        conn.close()

def create_client_table():
    conn = get_db_connection()
    if not conn:
        print("Impossible de se connecter à la base PostgreSQL.")
        return

    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Client (
                code_client TEXT PRIMARY KEY,
                nom_client TEXT NOT NULL,
                representant TEXT,
                tel TEXT,
                email TEXT,
                date_creation DATE,
                adresse TEXT,
                cp TEXT,
                ville TEXT,
                pays TEXT
            );
        """)
        conn.commit()
        print("Table Client créée avec succès ou existante.")
    except Exception as e:
        print(f"Erreur lors de la création de la table Client : {e}")
    finally:
        conn.close()
        
        
def import_client_data():
    file_clients = './data/client.xlsx'
    if not os.path.exists(file_clients):
        print("Fichier client.xlsx introuvable dans le dossier ./data. Vérifiez le chemin et réessayez.")
        return

    try:
        # Charger les données du fichier Excel
        data_clients = pd.read_excel(file_clients)
        print("Colonnes disponibles dans le fichier clients :")
        print(data_clients.columns)

        # Renommer les colonnes pour correspondre à la base de données
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

        # Conserver uniquement les colonnes nécessaires
        data_clients = data_clients[['code_client', 'nom_client', 'representant', 'tel',
                                     'email', 'date_creation', 'adresse', 'cp', 'ville', 'pays']]

        # Connexion à PostgreSQL
        conn = get_db_connection()
        if not conn:
            print("Impossible de se connecter à la base PostgreSQL.")
            return

        cursor = conn.cursor()

        # Insérer les données dans la table Client
        for _, row in data_clients.iterrows():
            cursor.execute("""
                INSERT INTO Client (code_client, nom_client, representant, tel, email, date_creation, adresse, cp, ville, pays)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (code_client) DO NOTHING;
            """, (row['code_client'], row['nom_client'], row['representant'], row['tel'],
                  row['email'], row['date_creation'], row['adresse'], row['cp'], row['ville'], row['pays']))

        conn.commit()
        print("Données insérées avec succès dans la table Client.")
    except Exception as e:
        print(f"Erreur lors de l'importation des données clients : {e}")
    finally:
        conn.close()


    
def check_client_table():
    conn = get_db_connection()
    query = "SELECT * FROM Client LIMIT 5;"
    try:
        df = pd.read_sql_query(query, conn)
        print("Exemple de données dans la table Client :")
        print(df)
    except Exception as e:
        print(f"Erreur lors de la vérification de la table Client : {e}")
    finally:
        conn.close()

def check_client_table_structure():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'client';
        """
        cursor.execute(query)
        columns = cursor.fetchall()
        print("Structure de la table Client :")
        for column in columns:
            print(column)
    except Exception as e:
        print(f"Erreur lors de la vérification de la structure de la table Client : {e}")
    finally:
        conn.close()

def import_produits():
    file_produits = './data/produits.xlsx'
    if not os.path.exists(file_produits):
        print("Fichier produits.xlsx introuvable dans le dossier ./data. Vérifiez le chemin et réessayez.")
        return

    try:
        data_produits = pd.read_excel(file_produits)
        print("Colonnes disponibles dans le fichier produits :")
        print(data_produits.columns)

        # Renommer les colonnes pour correspondre à la base de données
        data_produits.rename(columns={
            'Code Article': 'code_article',
            'Nom produit': 'nom_produit'
        }, inplace=True)

        print("Colonnes après renommage :")
        print(data_produits.columns)

        # Ajouter des colonnes par défaut si nécessaire
        for col in ['poids', 'nb_par_carton', 'largeur_carton', 'longueur_carton', 'hauteur_carton', 'poids_carton']:
            if col not in data_produits.columns:
                data_produits[col] = 0

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insérer ou remplacer les données
        for _, row in data_produits.iterrows():
            cursor.execute("""
                INSERT INTO Produits (code_article, nom_produit, poids, nb_par_carton, largeur_carton, longueur_carton, hauteur_carton, poids_carton)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (code_article) DO UPDATE SET
                nom_produit = EXCLUDED.nom_produit,
                poids = EXCLUDED.poids,
                nb_par_carton = EXCLUDED.nb_par_carton,
                largeur_carton = EXCLUDED.largeur_carton,
                longueur_carton = EXCLUDED.longueur_carton,
                hauteur_carton = EXCLUDED.hauteur_carton,
                poids_carton = EXCLUDED.poids_carton;
            """, (row['code_article'], row['nom_produit'], row['poids'], row['nb_par_carton'], 
                  row['largeur_carton'], row['longueur_carton'], row['hauteur_carton'], row['poids_carton']))

        conn.commit()
        print("Données insérées avec succès dans la table Produits.")
    except Exception as e:
        print(f"Erreur lors de l'importation des produits : {e}")
    finally:
        conn.close()


        


def check_database_tables():
    conn = get_db_connection()
    tables = ['Produits', 'Stocks', 'Ventes']
    for table in tables:
        print(f"\nDonnées dans la table {table}:")
        try:
            query = f"SELECT * FROM {table} LIMIT 5;"
            df = pd.read_sql_query(query, conn)
            print(df)
        except Exception as e:
            print(f"Erreur lors de l'accès à la table {table} : {e}")
    conn.close()

@app.route('/add_product_form')
def add_product_form():
    code_article = request.args.get('code_article', '')
    existing_data = None

    if code_article:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT code_article, poids, nb_par_carton, largeur_carton, longueur_carton, hauteur_carton, 
                   poids_carton, delai_reapprovisionnement
            FROM LogistiqueProduits WHERE code_article = %s;
        """, (code_article,))
        existing_entry = cursor.fetchone()
        conn.close()

        if existing_entry:
            existing_data = existing_entry

    return render_template('add_product_form.html', code_article=code_article, existing_data=existing_data)


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

    conn = get_db_connection()
    cursor = conn.cursor()

    # Vérifier si des données logistiques existent déjà pour ce produit
    cursor.execute("SELECT 1 FROM LogistiqueProduits WHERE code_article = %s;", (code_article,))
    existing_entry = cursor.fetchone()

    if existing_entry:
        # Si les données existent, les mettre à jour
        cursor.execute("""
            UPDATE LogistiqueProduits
            SET poids = %s, nb_par_carton = %s, largeur_carton = %s, longueur_carton = %s, hauteur_carton = %s, 
                poids_carton = %s, delai_reapprovisionnement = %s
            WHERE code_article = %s;
        """, (poids, nb_par_carton, largeur_carton, longueur_carton, hauteur_carton, poids_carton, delai_reapprovisionnement, code_article))
        message = f"Les détails du produit {code_article} ont été mis à jour avec succès."
    else:
        # Sinon, insérer une nouvelle entrée
        cursor.execute("""
            INSERT INTO LogistiqueProduits (code_article, poids, nb_par_carton, largeur_carton, longueur_carton, hauteur_carton, 
                                            poids_carton, delai_reapprovisionnement)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """, (code_article, poids, nb_par_carton, largeur_carton, longueur_carton, hauteur_carton, poids_carton, delai_reapprovisionnement))
        message = f"Les détails du produit {code_article} ont été ajoutés avec succès."

    conn.commit()
    conn.close()
    return message



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

        # Renommage des colonnes
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

        # Insertion dans PostgreSQL
        conn = get_db_connection()
        cursor = conn.cursor()
        for _, row in data_ventes.iterrows():
            cursor.execute("""
                INSERT INTO Ventes (code_client, code_article, date_vente, quantite_vendue, prix_achat, nom_representant, nom_client)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (row['code_client'], row['code_article'], row['date_vente'], row['quantite_vendue'], row['prix_achat'], row['nom_representant'], row['nom_client']))
        conn.commit()
        conn.close()
        print("Données insérées avec succès dans la table Ventes.")
    except Exception as e:
        print(f"Erreur lors de l'importation des ventes : {e}")


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

        # Insertion dans PostgreSQL
        conn = get_db_connection()
        cursor = conn.cursor()
        for _, row in data_stocks.iterrows():
            cursor.execute("""
                INSERT INTO Stocks (code_article, quantite_stock)
                VALUES (%s, %s)
                ON CONFLICT (code_article) DO UPDATE SET quantite_stock = EXCLUDED.quantite_stock;
            """, (row['code_article'], row['quantite_stock']))
        conn.commit()
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
        data_achats = pd.read_excel(file_achats)
        print("Colonnes disponibles dans le fichier achats :")
        print(data_achats.columns)

        data_achats.rename(columns={
            'code_document': 'code_document',
            'numero_document': 'numero_document',
            'date_document': 'date_document',
            'fournisseur': 'fournisseur',
            'quantite': 'quantite',
            'code_article': 'code_article'
        }, inplace=True)

        # Correction des dates
        data_achats['date_document'] = pd.to_datetime(data_achats['date_document'], errors='coerce')
        data_achats = data_achats.dropna(subset=['date_document'])

        conn = get_db_connection()
        cursor = conn.cursor()
        for _, row in data_achats.iterrows():
            cursor.execute("""
                INSERT INTO Achats (code_document, numero_document, date_document, fournisseur, quantite, code_article)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (row['code_document'], row['numero_document'], row['date_document'], row['fournisseur'], row['quantite'], row['code_article']))
        conn.commit()
        conn.close()
        print("Données insérées avec succès dans la table Achats.")
    except Exception as e:
        print(f"Erreur lors de l'importation des achats : {e}")


def reset_ventes_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("TRUNCATE TABLE Ventes RESTART IDENTITY;")
        conn.commit()
        print("Table Ventes réinitialisée.")
    except Exception as e:
        print(f"Erreur lors de la réinitialisation de la table Ventes : {e}")
    finally:
        conn.close()
        




def get_palmares(order_by='vente_2024 DESC'):
    conn = get_db_connection()

    query = f'''
    SELECT 
        p.code_article AS code_article,
        p.nom_produit,
        COALESCE(s.quantite_stock, 0) AS quantite_stock,
        COALESCE(lp.delai_reapprovisionnement, 0) AS delai_reapprovisionnement,
        ROUND(
            (
                AVG(
                    CASE WHEN v.date_vente >= NOW() - INTERVAL '12 months' THEN v.quantite_vendue ELSE 0 END
                ) / 30
            ) * lp.delai_reapprovisionnement + 
            AVG(CASE WHEN v.date_vente >= NOW() - INTERVAL '12 months' THEN v.quantite_vendue ELSE 0 END), 2
        ) AS stock_securite,
        SUM(CASE WHEN EXTRACT(YEAR FROM v.date_vente) = 2023 THEN v.quantite_vendue ELSE 0 END) AS vente_2023,
        SUM(CASE WHEN EXTRACT(YEAR FROM v.date_vente) = 2024 THEN v.quantite_vendue ELSE 0 END) AS vente_2024,
        SUM(CASE WHEN EXTRACT(YEAR FROM v.date_vente) = 2025 THEN v.quantite_vendue ELSE 0 END) AS vente_2025
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

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_sales_by_representative(code_article):
    conn = get_db_connection()
    query = '''
    SELECT
        COALESCE(c.representant, 'Inconnu') AS nom_representant,
        p.nom_produit,
        SUM(CASE WHEN EXTRACT(YEAR FROM v.date_vente) = 2023 THEN v.quantite_vendue ELSE 0 END) AS vente_2023,
        SUM(CASE WHEN EXTRACT(YEAR FROM v.date_vente) = 2024 THEN v.quantite_vendue ELSE 0 END) AS vente_2024,
        SUM(CASE WHEN EXTRACT(YEAR FROM v.date_vente) = 2025 THEN v.quantite_vendue ELSE 0 END) AS vente_2025
    FROM
        Ventes v
    LEFT JOIN
        Produits p ON v.code_article = p.code_article
    LEFT JOIN
        Client c ON v.code_client = c.code_client
    WHERE
        v.code_article = %s
    GROUP BY
        c.representant, p.nom_produit
    ORDER BY
        vente_2024 DESC, vente_2023 DESC, vente_2025 DESC;
    '''
    result = pd.read_sql_query(query, conn, params=[code_article])
    conn.close()
    return result

def get_monthly_sales_and_average():
    conn = get_db_connection()
    query = '''
    SELECT
        c.representant AS nom_representant,
        TO_CHAR(v.date_vente, 'YYYY-MM') AS mois,
        SUM(v.quantite_vendue * v.prix_achat) AS chiffre_affaire
    FROM
        Ventes v
    JOIN
        Client c ON v.code_client = c.code_client
    GROUP BY
        c.representant, TO_CHAR(v.date_vente, 'YYYY-MM')
    ORDER BY
        c.representant, mois;
    '''
    
    sales_data = pd.read_sql_query(query, conn)

    sales_pivot = sales_data.pivot_table(
        index='nom_representant',
        columns='mois',
        values='chiffre_affaire',
        fill_value=0
    ).reset_index()

    monthly_totals = sales_pivot.drop(columns='nom_representant').sum(axis=0)
    num_representants = sales_pivot.shape[0]
    average_sales = monthly_totals / num_representants

    conn.close()
    return sales_pivot, average_sales


def get_monthly_sales_by_product(code_article):
    conn = get_db_connection()
    query = '''
    SELECT 
        TO_CHAR(date_vente, 'YYYY-MM') AS mois,
        v.code_article,
        p.nom_produit,
        SUM(v.quantite_vendue) AS quantite_vendue
    FROM 
        Ventes v
    JOIN 
        Produits p ON v.code_article = p.code_article
    WHERE 
        v.code_article = %s
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
    conn = get_db_connection()

    # Requête pour les ventes
    sales_query = '''
    SELECT
        TO_CHAR(date_vente, 'YYYY-MM') AS mois,
        SUM(quantite_vendue) AS quantite_vendue
    FROM
        Ventes
    WHERE
        code_article = %s
    GROUP BY
        mois
    ORDER BY
        mois;
    '''
    sales_data = pd.read_sql_query(sales_query, conn, params=[code_article])

    # Requête pour les produits reçus
    received_query = '''
    SELECT
        TO_CHAR(date_document, 'YYYY-MM') AS mois,
        SUM(quantite) AS quantite_achetee
    FROM
        Achats
    WHERE
        code_article = %s AND code_document = 16
    GROUP BY
        mois
    ORDER BY
        mois;
    '''
    received_data = pd.read_sql_query(received_query, conn, params=[code_article])

    # Requête pour les produits commandés
    ordered_query = '''
    SELECT
        TO_CHAR(date_document, 'YYYY-MM') AS mois,
        SUM(quantite) AS quantite_commandee
    FROM
        Achats
    WHERE
        code_article = %s AND code_document = 12
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
    conn = get_db_connection()
    query = '''
    SELECT
        c.representant AS nom_representant,
        TO_CHAR(v.date_vente, 'YYYY-MM') AS mois,
        SUM(v.quantite_vendue * v.prix_achat) AS chiffre_affaire
    FROM
        Ventes v
    JOIN
        Client c ON v.code_client = c.code_client
    GROUP BY
        c.representant, TO_CHAR(v.date_vente, 'YYYY-MM')
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
    conn = get_db_connection()

    # Étape 1 : Requête SQL pour obtenir les ventes mensuelles par représentant
    query = '''
    SELECT
        c.representant AS nom_representant,
        TO_CHAR(v.date_vente, 'YYYY-MM') AS mois,
        SUM(v.quantite_vendue * v.prix_achat) AS chiffre_affaire
    FROM
        Ventes v
    JOIN
        Client c ON v.code_client = c.code_client
    GROUP BY
        c.representant, TO_CHAR(v.date_vente, 'YYYY-MM')
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
    conn = get_db_connection()
    query = '''
    SELECT
        c.code_client AS code_client,
        c.nom_client AS nom_pharmacie,
        c.representant AS nom_representant,
        TO_CHAR(v.date_vente, 'YYYY-MM') AS mois,
        SUM(v.quantite_vendue * v.prix_achat) AS chiffre_affaire
    FROM
        Ventes v
    JOIN
        Client c ON v.code_client = c.code_client
    WHERE
        v.code_article = %s
    GROUP BY
        c.code_client, c.nom_client, c.representant, TO_CHAR(v.date_vente, 'YYYY-MM')
    ORDER BY
        c.nom_client, mois;
    '''
    try:
        sales_data = pd.read_sql_query(query, conn, params=[code_article])

        # Transformation en table pivot
        sales_pivot = sales_data.pivot_table(
            index=['code_client', 'nom_pharmacie', 'nom_representant'],
            columns='mois',
            values='chiffre_affaire',
            fill_value=0
        ).reset_index()

        print(f"Ventes mensuelles par pharmacie pour le produit {code_article} :")
        print(sales_pivot)
        return sales_pivot
    except Exception as e:
        print(f"Erreur lors de la récupération des ventes mensuelles par pharmacie : {e}")
        return None
    finally:
        conn.close()

    

# Route pour afficher les ventes, produits reçus et produits commandés mensuels par produit
@app.route('/product/<code_article>/monthly_sales_product')
def monthly_sales_product(code_article):
    monthly_data = get_monthly_sales_and_purchases(code_article)
    return render_template('monthly_sales_product.html', tables=monthly_data.to_dict(orient='records'), code_article=code_article)

# Route pour gérer le moteur de recherche
@app.route('/search')
def search():
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



def show_logistic_data():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM LogistiqueProduits;")
            rows = cursor.fetchall()
            conn.close()
            print("Données dans LogistiqueProduits :")
            for row in rows:
                print(row)
        except Exception as e:
            print(f"Erreur lors de la récupération des données logistiques : {e}")
    else:
        print("Impossible de se connecter à la base de données.")

# Appeler cette fonction après insertion pour vérifier
show_logistic_data()

# Route pour afficher les données dans la table Achats
@app.route('/view_achats')
def view_achats():
    conn = get_db_connection()
    if conn:
        try:
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
        except Exception as e:
            return f"Erreur lors de la récupération des données : {e}"
    else:
        return "Impossible de se connecter à la base de données."



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
    create_tables()
    recreate_database()
    manage_logistique_produits_table()
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
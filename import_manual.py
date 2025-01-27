import psycopg2
from psycopg2 import sql

# Configuration de la base de données
DB_CONFIG = {
    "dbname": "vogdashboard",
    "user": "vogdashboard_user",
    "password": "gXuIhJVeM7XqfsHe77LO0kMbInSLTOIi",
    "host": "dpg-cu9lbptsvqrc73dh3l1g-a.oregon-postgres.render.com",
    "port": "5432"
}

def check_and_insert_product(code_article):
    """Vérifie si un produit existe dans Produits et l'ajoute s'il est absent."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Vérifier si le produit existe
        query_check = sql.SQL("SELECT * FROM Produits WHERE code_article = %s;")
        cursor.execute(query_check, (code_article,))
        result = cursor.fetchone()

        if not result:
            # Insérer un produit par défaut si absent
            query_insert = sql.SQL("""
                INSERT INTO Produits (code_article, nom_produit, poids, nb_par_carton, largeur_carton, longueur_carton, hauteur_carton, poids_carton)
                VALUES (%s, %s, 0, 0, 0, 0, 0, 0);
            """)
            cursor.execute(query_insert, (code_article, 'Produit par défaut'))
            conn.commit()
            print(f"Produit {code_article} ajouté dans la table Produits.")
        else:
            print(f"Produit {code_article} existe déjà dans la table Produits.")

    except Exception as e:
        print(f"Erreur lors de la vérification ou de l'insertion du produit : {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

def insert_vente(code_article, date_vente, quantite_vendue, prix_achat):
    """Insère une vente après avoir vérifié l'existence du produit."""
    try:
        # Vérifier ou insérer le produit
        check_and_insert_product(code_article)

        # Connexion pour l'insertion de la vente
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Insérer la vente
        query_insert = sql.SQL("""
            INSERT INTO Ventes (code_article, date_vente, quantite_vendue, prix_achat)
            VALUES (%s, %s, %s, %s);
        """)
        cursor.execute(query_insert, (code_article, date_vente, quantite_vendue, prix_achat))
        conn.commit()

        print("Ligne insérée avec succès dans la table Ventes.")

        # Vérifier les données insérées
        cursor.execute("SELECT * FROM Ventes ORDER BY id_vente DESC LIMIT 5;")
        rows = cursor.fetchall()
        print("Dernières lignes dans la table Ventes :")
        for row in rows:
            print(row)

    except Exception as e:
        print(f"Erreur : {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

# Exemple d'utilisation
if __name__ == "__main__":
    insert_vente("AUTOTESTSEJOY2026", "2024-08-20", 100, 0.79)

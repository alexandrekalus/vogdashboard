import sqlite3
import pandas as pd

db_name = 'gestion_ventes_stocks.db'

conn = sqlite3.connect(db_name)

# Vérifiez les données dans chaque table
tables = ['Produits', 'Stocks', 'Clients', 'Ventes']

for table in tables:
    print(f"\nDonnées dans la table {table} :")
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    print(df)

conn.close()
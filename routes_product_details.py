from flask import Flask, render_template
from sqlalchemy import create_engine, text

# Configuration de la connexion à la base de données
DATABASE_URL = "postgresql://vogdashboard_user:gXuIhJVeM7XqfsHe77LO0kMbInSLTOIi@dpg-cu9lbptsvqrc73dh3l1g-a.oregon-postgres.render.com/vogdashboard"
engine = create_engine(DATABASE_URL)



def product_details(app):
    @app.route('/essailienpourvoir/<code_article>')
    def product_details_route(code_article):
        print(f"Route appelée avec code_article: {code_article}")
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

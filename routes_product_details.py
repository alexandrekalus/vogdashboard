from flask import Flask, render_template
from sqlalchemy import create_engine, text

# Configuration de la connexion à la base de données
DATABASE_URL = "postgresql://vogdashboard_user:gXuIhJVeM7XqfsHe77LO0kMbInSLTOIi@dpg-cu9lbptsvqrc73dh3l1g-a.oregon-postgres.render.com/vogdashboard"
engine = create_engine(DATABASE_URL)



def product_details(app):

    @app.route('/essailienpourvoir/<code_article>')
    def product_details_route(code_article):
        return f"Page pour le produit : {code_article}"
      

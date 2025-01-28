import pandas as pd

# Création des données des départements français avec codes et noms
departments_data = {
    "code": [
        "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
        "11", "12", "13", "14", "15", "16", "17", "18", "19", "21",
        "22", "23", "24", "25", "26", "27", "28", "29", "30", "31",
        "32", "33", "34", "35", "36", "37", "38", "39", "40", "41",
        "42", "43", "44", "45", "46", "47", "48", "49", "50", "51",
        "52", "53", "54", "55", "56", "57", "58", "59", "60", "61",
        "62", "63", "64", "65", "66", "67", "68", "69", "70", "71",
        "72", "73", "74", "75", "76", "77", "78", "79", "80", "81",
        "82", "83", "84", "85", "86", "87", "88", "89", "90", "91",
        "92", "93", "94", "95", "971", "972", "973", "974", "976"
    ],
    "nom": [
        "Ain", "Aisne", "Allier", "Alpes-de-Haute-Provence", "Hautes-Alpes",
        "Alpes-Maritimes", "Ardèche", "Ardennes", "Ariège", "Aube",
        "Aude", "Aveyron", "Bouches-du-Rhône", "Calvados", "Cantal",
        "Charente", "Charente-Maritime", "Cher", "Corrèze", "Côte-d'Or",
        "Côtes-d'Armor", "Creuse", "Dordogne", "Doubs", "Drôme",
        "Eure", "Eure-et-Loir", "Finistère", "Gard", "Haute-Garonne",
        "Gers", "Gironde", "Hérault", "Ille-et-Vilaine", "Indre",
        "Indre-et-Loire", "Isère", "Jura", "Landes", "Loir-et-Cher",
        "Loire", "Haute-Loire", "Loire-Atlantique", "Loiret", "Lot",
        "Lot-et-Garonne", "Lozère", "Maine-et-Loire", "Manche", "Marne",
        "Haute-Marne", "Mayenne", "Meurthe-et-Moselle", "Meuse", "Morbihan",
        "Moselle", "Nièvre", "Nord", "Oise", "Orne",
        "Pas-de-Calais", "Puy-de-Dôme", "Pyrénées-Atlantiques", "Hautes-Pyrénées",
        "Pyrénées-Orientales", "Bas-Rhin", "Haut-Rhin", "Rhône", "Haute-Saône",
        "Saône-et-Loire", "Sarthe", "Savoie", "Haute-Savoie", "Paris",
        "Seine-Maritime", "Seine-et-Marne", "Yvelines", "Deux-Sèvres", "Somme",
        "Tarn", "Tarn-et-Garonne", "Var", "Vaucluse", "Vendée", "Vienne",
        "Haute-Vienne", "Vosges", "Yonne", "Territoire de Belfort",
        "Essonne", "Hauts-de-Seine", "Seine-Saint-Denis", "Val-de-Marne", "Val-d'Oise",
        "Guadeloupe", "Martinique", "Guyane", "La Réunion", "Mayotte"
    ]
}

# Convertir en DataFrame
departments_df = pd.DataFrame(departments_data)

# Sauvegarder dans un fichier CSV
departments_df.to_csv("departements.csv", index=False)
print("Fichier departements.csv généré avec succès.")
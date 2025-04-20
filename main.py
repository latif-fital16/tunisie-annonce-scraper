# main.py
from fastapi import FastAPI, HTTPException
from scraping import scrape_tayara
import pandas as pd
import os

app = FastAPI()

def load_data():
    """Charge les données depuis le fichier CSV ou lance un scraping si le fichier n'existe pas."""
    if not os.path.exists('annonces_tayara_jan_fev_2025.csv'):
        print("Le fichier CSV n'existe pas. Lancement du scraping initial...")
        return scrape_tayara()
    try:
        df = pd.read_csv('annonces_tayara_jan_fev_2025.csv')
        return df.to_dict(orient='records') if not df.empty else []
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier CSV : {e}")
        return []

# Charger les données au démarrage
annonces = load_data()

@app.get("/")
def root():
    """Endpoint racine pour vérifier que l'API est opérationnelle."""
    return {"message": "API de scraping Tayara opérationnelle"}

@app.get("/annonces")
def get_annonces():
    """Retourne toutes les annonces de janvier/février 2025."""
    if not annonces:
        raise HTTPException(status_code=404, detail="Aucune annonce trouvée")
    return annonces

@app.post("/scrape")
def scrape_annonces():
    """Relance le scraping et met à jour les données."""
    global annonces
    annonces = scrape_tayara()
    if not annonces:
        raise HTTPException(status_code=500, detail="Échec du scraping ou aucune annonce trouvée")
    return {"message": f"{len(annonces)} annonces récupérées avec succès"}
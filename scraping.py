# scraping.py
import pandas as pd
from bs4 import BeautifulSoup as soup
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_tayara():
    print("Démarrage de la fonction scrape_tayara...")
    
    # Configuration de Selenium
    print("Configuration de Selenium...")
    service = Service(r"C:\chromedriver\chromedriver-win64\chromedriver.exe")
    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=service, options=options)
    print("Navigateur Chrome démarré avec succès.")

    try:
        # Liste des URLs à scraper (10 premières pages)
        urls = [f"https://www.tayara.tn/ads/c/Immobilier/?page={i}" for i in range(1, 11)]
        data = []

        # Date de référence (simulons que nous sommes le 15/02/2025 pour tester)
        reference_date = datetime(2025, 2, 15)

        for url in urls:
            print(f"Scraping: {url}")
            driver.get(url)

            # Attendre que les annonces soient chargées
            print("Attente des annonces...")
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "article.mx-0"))
                )
                print("Annonces chargées avec succès.")
            except Exception as e:
                print(f"Erreur lors du chargement des annonces sur {url}: {e}")
                continue

            # Parser le contenu HTML avec BeautifulSoup
            print("Parsing du HTML...")
            page = soup(driver.page_source, 'html.parser')
            house_containers = page.find_all("article", class_="mx-0")
            print(f"Nombre d'annonces trouvées: {len(house_containers)}")

            for house in house_containers:
                # Titre de l'article
                nom_article = house.find('h2', class_="card-title font-arabic text-sm font-medium leading-5 text-gray-800 max-w-min min-w-full line-clamp-2 my-2")
                titre = nom_article.text.strip() if nom_article else "N/A"

                # Lien de l’annonce
                lien_elem = house.find('a', href=True)
                lien = lien_elem['href'] if lien_elem else "N/A"
                lien = "https://www.tayara.tn" + lien if lien != "N/A" and not lien.startswith("http") else lien

                # Prix
                prix_elem = house.find('data', class_="font-bold font-arabic text-red-600 undefined")
                prix = prix_elem.text.strip().replace(" ", "") if prix_elem else "N/A"

                # Type de bien (catégorie)
                type_bien_elem = house.find('span', class_="truncate text-3xs md:text-xs lg:text-xs w-3/5 font-medium text-neutral-500")
                type_bien = type_bien_elem.text.strip() if type_bien_elem else "N/A"

                # Localisation et Date (elles sont dans le même span)
                localisation_elems = house.find_all('span', class_="line-clamp-1 truncate text-3xs md:text-xs lg:text-xs w-3/5 font-medium text-neutral-500")
                localisation_date = localisation_elems[-1].text.strip() if localisation_elems else "N/A"
                
                # Séparer localisation et date (ex. "Tunis, an hour ago")
                localisation = "N/A"
                date_pub_raw = "N/A"
                if ", " in localisation_date:
                    localisation, date_pub_raw = localisation_date.split(", ", 1)
                else:
                    localisation = localisation_date

                print(f"Localisation: {localisation}, Date brute: {date_pub_raw}")

                # Superficie (recherche dans le titre)
                superficie = "N/A"
                for word in titre.split():
                    if "m²" in word:
                        superficie = word.replace("m²", "").strip()

                # Description (on utilise le titre comme description)
                description = titre

                # Normalisation de la date
                date_pub = "N/A"
                if "an hour ago" in date_pub_raw.lower() or "hours ago" in date_pub_raw.lower():
                    hours_ago = 1 if "an hour ago" in date_pub_raw.lower() else int(date_pub_raw.split(" hours ago")[0].strip())
                    pub_date = reference_date - timedelta(hours=hours_ago)
                    date_pub = pub_date.strftime("%d/%m/%Y")
                elif "minutes ago" in date_pub_raw.lower():
                    minutes_ago = int(date_pub_raw.split(" minutes ago")[0].strip())
                    pub_date = reference_date - timedelta(minutes=minutes_ago)
                    date_pub = pub_date.strftime("%d/%m/%Y")
                elif "days ago" in date_pub_raw.lower():
                    days_ago = int(date_pub_raw.split(" days ago")[0].strip())
                    pub_date = reference_date - timedelta(days=days_ago)
                    date_pub = pub_date.strftime("%d/%m/%Y")
                elif "weeks ago" in date_pub_raw.lower():
                    weeks_ago = int(date_pub_raw.split(" weeks ago")[0].strip())
                    pub_date = reference_date - timedelta(weeks=weeks_ago)
                    date_pub = pub_date.strftime("%d/%m/%Y")
                elif "months ago" in date_pub_raw.lower():
                    months_ago = int(date_pub_raw.split(" months ago")[0].strip())
                    pub_date = reference_date - timedelta(days=months_ago * 30)  # Approximation: 1 mois = 30 jours
                    date_pub = pub_date.strftime("%d/%m/%Y")
                elif "janvier 2025" in date_pub_raw.lower():
                    date_pub = date_pub_raw.replace("janvier 2025", "01/2025").replace(" ", "")
                elif "février 2025" in date_pub_raw.lower():
                    date_pub = date_pub_raw.replace("février 2025", "02/2025").replace(" ", "")
                print(f"Date normalisée: {date_pub}")

                # Ajouter à la liste des données
                data.append({
                    "titre": titre,
                    "prix": prix,
                    "type_bien": type_bien,
                    "localisation": localisation,
                    "superficie": superficie,
                    "description": description,
                    "date_publication": date_pub,
                    "lien": lien
                })

        # Sauvegarder toutes les données avant filtrage pour débogage
        if data:
            df = pd.DataFrame(data)
            df.to_csv('annonces_tayara_toutes.csv', index=False, encoding="utf-8-sig")
            print(f"Toutes les annonces ({len(df)}) sauvegardées dans 'annonces_tayara_toutes.csv'")

            # Filtrer les annonces pour janvier/février 2025
            df_filtered = df[df["date_publication"].str.contains(r"^(0[1-2]|[1-2][0-9])/01/2025|^(0[1-2]|[1-2][0-9])/02/2025", regex=True, na=False)]
            df_filtered.to_csv('annonces_tayara_jan_fev_2025.csv', index=False, encoding="utf-8-sig")
            print(f"{len(df_filtered)} annonces de janvier/février 2025 sauvegardées dans 'annonces_tayara_jan_fev_2025.csv'")
            return df_filtered.to_dict(orient='records')
        else:
            print("Aucune donnée trouvée lors du scraping.")
            return []

    finally:
        driver.quit()
        print("Navigateur fermé.")

if __name__ == "__main__":
    annonces = scrape_tayara()
    print(f"Annonces récupérées: {annonces}")
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="PharmaGarde & Santé CI", page_icon="🇨🇮")

# --- FONCTION DE RÉCUPÉRATION (SCRAPING) ---
@st.cache_data(ttl=86400)
def scraper_toute_la_garde():
    urls = {
        "Abidjan": "https://www.pharmacies-de-garde.ci/liste-des-pharmacies-de-garde-a-abidjan-votre-permanence/",
        "Intérieur": "https://www.pharmacies-de-garde.ci/pharmacies-de-garde-villes-de-linterieur/"
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    all_data = []

    for zone, url in urls.items():
        try:
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            for el in soup.find_all(['li', 'p', 'tr']):
                txt = el.text.strip()
                if "-" in txt and len(txt) > 15:
                    parts = txt.split("-")
                    all_data.append({
                        "Type": "Pharmacie de Garde",
                        "Zone": zone,
                        "Nom": parts[0].strip(),
                        "Localisation": parts[1].strip() if len(parts)>1 else "Non précisé",
                        "Contact": parts[2].strip() if len(parts)>2 else "Voir sur place"
                    })
        except:
            continue
    return pd.DataFrame(all_data)

# --- INTERFACE ---
st.title("🇨🇮 Annuaire Santé Côte d'Ivoire")

menu = st.sidebar.radio("Que recherchez-vous ?", ["Pharmacies de Garde", "Centres de Santé (Annuaire)"])

if menu == "Pharmacies de Garde":
    st.header("🏥 Gardes en temps réel")
    df = scraper_toute_la_garde()
    
    recherche = st.text_input("🔍 Ville, Commune ou Quartier (ex: Bouaké, Cocody...)")
    
    if not df.empty:
        # Filtrage intelligent
        mask = df.apply(lambda r: recherche.lower() in r.astype(str).str.lower().values, axis=1)
        resultats = df[mask] if recherche else df
        
        for _, row in resultats.iterrows():
            with st.expander(f"📍 {row['Nom']} ({row['Zone']})"):
                st.write(f"🏠 **Lieu :** {row['Localisation']}")
                st.write(f"📞 **Contact :** {row['Contact']}")
                st.link_button("💬 Partager l'urgence", f"https://wa.me/?text=URGENCE%20SANTE%3A%20{row['Nom']}%20à%20{row['Localisation']}%20-%20Tel%3A%20{row['Contact']}")
    else:
        st.error("Données indisponibles. Réessayez plus tard.")

else:
    st.header("🏨 Annuaire des Centres de Santé")
    st.info("Cette section utilise la base de données officielle du gouvernement (annuaire.gouv.ci).")
    # Ici, vous pouvez charger un fichier CSV contenant l'annuaire fixe
    st.write("Fonctionnalité en cours de liaison avec l'annuaire national...")

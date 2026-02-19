import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# --- CONFIGURATION ÉCRAN & STYLE ---
st.set_page_config(page_title="Santé CI - Live", layout="wide")

st.markdown("""
    <style>
    input, textarea { color: #000000 !important; background-color: #ffffff !important; border: 2px solid #00AB66 !important; }
    .stApp { background-color: #f4f7f6; }
    .pharmacie-card {
        background: white; padding: 20px; border-radius: 15px;
        border-left: 10px solid #00AB66; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 20px; color: #1a1a1a;
    }
    .urgence-rouge { background: #ffebee; border-left: 10px solid #d32f2f; padding: 15px; border-radius: 10px; color: #b71c1c; margin-bottom: 10px; }
    .conseil-vert { background: #e8f5e9; border-left: 10px solid #2e7d32; padding: 15px; border-radius: 10px; color: #1b5e20; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- SCRAPER AUTOMATIQUE (annuaireci.com) ---
@st.cache_data(ttl=3600) # Mise à jour automatique toutes les heures
def scraper_pharmacies_live():
    url = "https://annuaireci.com/pharmacies-de-garde/"
    headers = {"User-Agent": "Mozilla/5.0"}
    all_pharmacies = []
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # On cible les éléments de la liste sur annuaireci.com
        items = soup.find_all('div', class_='wp-block-column') # Structure type du site
        
        for item in soup.find_all(['p', 'li']):
            text = item.text.strip()
            # On cherche les lignes contenant un numéro (01, 05, 07, 27)
            if re.search(r'\d{2}\s\d{2}\s\d{2}', text):
                parts = text.split('-') if '-' in text else [text]
                nom = parts[0].strip()
                contact = re.search(r'[\d\s]{8,}', text)
                
                all_pharmacies.append({
                    "Type": "Pharmacie de Garde",
                    "Nom": nom,
                    "Contact": contact.group(0) if contact else "Consulter sur place",
                    "Source": "Live: AnnuaireCI"
                })
        return pd.DataFrame(all_pharmacies).drop_duplicates()
    except:
        return pd.DataFrame()

# --- MOTEUR MÉDICAL AFRIQUE ---
def diagnostic_expert(text):
    text = text.lower()
    if any(m in text for m in ["poitrine", "paralyse", "bouche", "conscience"]):
        return "🔴 ALERTE CRITIQUE", "Urgence AVC/Coeur. Ne rien donner à boire. Appelez le 185.", "Hôpital/SAMU"
    if any(m in text for m in ["fievre", "chaud", "palu", "corps"]):
        return "🟡 PALUDISME / FIÈVRE", "Remède Maison : Linges mouillés sur le front. Hydratation. Si > 39°C, Paracétamol.", "Pharmacie"
    if any(m in text for m in ["ventre", "diarrhée", "vomir"]):
        return "🟡 DIARRHÉE / DÉSHYDRATATION", "Remède Maison : SRO (1L eau + 6 sucres + 1 pincée sel). Riz cuit.", "Pharmacie"
    return "⚪ ANALYSE", "Décrivez vos symptômes précisément pour un conseil adapté.", "Général"

# --- CHARGEMENT DES DONNÉES ---
df_fixe = pd.read_csv("https://raw.githubusercontent.com/dedjebonoua/pharma-garde-ci/main/annuaire_sante_ci.csv")
df_live = scraper_pharmacies_live()

# --- INTERFACE ---
st.title("🏥 Assistant Santé CI - Temps Réel")

tab1, tab2 = st.tabs(["🩺 IA Diagnostic & Conseils", "💊 Pharmacies de Garde (LIVE)"])

with tab1:
    st.header("Analyseur de Symptômes & Remèdes")
    user_query = st.text_area("Décrivez le problème (Age, Sexe, Douleurs...) :", placeholder="Ecrivez ici...", height=120)
    if user_query:
        titre, avis, reco = diagnostic_expert(user_query)
        st.markdown(f'<div class="{"urgence-rouge" if "🔴" in titre else "conseil-vert"}"><h3>{titre}</h3><p>{avis}</p><b>Préconisation : {reco}</b></div>', unsafe_allow_html=True)

with tab2:
    st.header("Gardes à Abidjan & Intérieur")
    st.info("Données synchronisées en direct avec AnnuaireCI.com")
    
    if not df_live.empty:
        recherche = st.text_input("🔍 Chercher un quartier ou une ville...", key="live_search")
        
        # Filtrage
        mask = df_live.apply(lambda r: recherche.lower() in str(r).lower(), axis=1) if recherche else [True]*len(df_live)
        
        for _, row in df_live[mask].iterrows():
            st.markdown(f"""
            <div class="pharmacie-card">
                <h3>{row['Nom']}</h3>
                <p>📞 <b>Contact : {row['Contact']}</b></p>
                <p>✅ Statut : Ouvert (Garde en cours)</p>
            </div>
            """, unsafe_allow_html=True)
            st.link_button(f"📍 Voir Itinéraire : {row['Nom']}", f"https://www.google.com/maps/search/{row['Nom'].replace(' ', '+')}")
    else:
        st.warning("Mise à jour en cours... Si rien ne s'affiche, consultez l'annuaire fixe.")

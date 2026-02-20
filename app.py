import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import unicodedata

# --- CONFIGURATION & STYLE ---
st.set_page_config(page_title="SanteCI Expert", layout="wide")

def local_css():
    st.markdown("""
        <style>
        .stApp { background-color: #FFFFFF !important; }
        h1, h2, h3, p, label, span { color: #1A1A1A !important; }
        .stButton>button { width: 100%; border-radius: 25px; height: 50px; background-color: #00AB66; color: white; font-weight: bold; border: none; }
        .stButton>button:hover { background-color: #008f55; color: white; }
        input, textarea { background-color: #F8F9FA !important; color: black !important; border: 2px solid #00AB66 !important; }
        .resultat { padding: 20px; border-radius: 15px; margin-top: 10px; color: black; border-left: 10px solid; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        </style>
    """, unsafe_allow_html=True)

local_css()

# --- OUTILS DE NETTOYAGE (Pour les accents et majuscules) ---
def normaliser(texte):
    if not texte: return ""
    # Enlève les accents et met en minuscule
    texte = "".join(c for c in unicodedata.normalize('NFD', texte) if unicodedata.category(c) != 'Mn')
    return texte.lower().strip()

# --- BASE DE DONNÉES VIDAL (Mise à jour) ---
VIDAL_DATA = {
    "paracetamol": {
        "nom": "Paracétamol (Doliprane, Efferalgan, Panado)",
        "info": "Pour la fièvre et les douleurs (tête, dents, courbatures).",
        "dose": "Adulte: 1 comprimé de 1g max 4 fois par jour. Enfant: Selon le poids (60mg/kg/jour).",
        "alerte": "⚠️ Attention au foie : ne jamais dépasser 4g par jour. Ne pas boire d'alcool."
    },
    "artemether": {
        "nom": "Artéméther / Luméfantrine (Coartem, Lumartem)",
        "info": "Traitement de référence contre le Paludisme simple.",
        "dose": "Suivre strictement la cure de 3 jours (matin et soir).",
        "alerte": "⚠️ À prendre impérativement avec un repas gras (lait ou plat avec huile) pour agir."
    },
    "amoxicilline": {
        "nom": "Amoxicilline (Clamoxyl)",
        "info": "Antibiotique pour infections (poumons, gorge, dents).",
        "dose": "Généralement 1g matin et soir pendant 5 à 7 jours.",
        "alerte": "⚠️ Finissez TOUTE la boîte même si vous allez mieux pour éviter la résistance."
    }
}

# --- FONCTION GARDE LIVE ---
@st.cache_data(ttl=3600)
def scraper_gardes():
    try:
        url = "https://annuaireci.com/pharmacies-de-garde/"
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        return [i.text.strip() for i in soup.find_all(['p', 'li']) if re.search(r'\d{2}', i.text)]
    except: return []

# --- INTERFACE ---
st.title("🏥 SanteCI Assistant v3.5")
tab1, tab2, tab3 = st.tabs(["💊 Pharmacies", "🩺 IA Diagnostic", "📚 Guide Vidal"])

with tab1:
    st.subheader("📍 Pharmacies de garde")
    zone = st.text_input("Tapez votre commune (ex: Cocody, Plateau, San Pedro...)", key="z")
    if st.button("RECHERCHER MAINTENANT"):
        liste = scraper_gardes()
        filtre = [p for p in liste if normaliser(zone) in normaliser(p)]
        if filtre:
            for p in filtre:
                st.markdown(f'<div style="background:#f0f2f6; padding:15px; border-radius:10px; border-left:5px solid #00AB66; margin-bottom:10px; color:black;">{p}</div>', unsafe_allow_html=True)
        else:
            st.warning("Aucune pharmacie trouvée. Essayez un nom plus court (ex: 'Yop' au lieu de 'Yopougon').")

with tab2:
    st.subheader("Analyseur Ada (Symptômes)")
    txt = st.text_area("Décrivez votre mal...", placeholder="Ex: J'ai de la fièvre et mal au ventre")
    if st.button("ANALYSER MON ÉTAT"):
        t = normaliser(txt)
        if any(x in t for x in ["poitrine", "bras", "paralyse", "visage"]):
            color, border, title = "#FFEBEE", "#D32F2F", "🚨 URGENCE CARDIAQUE / AVC"
            msg = "Allongez le patient. Ne donnez rien à boire. Appelez le 185 (SAMU) ou 180 (Pompiers) IMMÉDIATEMENT."
        elif "fievre" in t or "chaud" in t:
            color, border, title = "#E8F5E9", "#2E7D32", "🦟 SUSPICION PALUDISME"
            msg = "Hydratez-vous. Douche tiède. Faites un test TDR en pharmacie. Si la fièvre dépasse 40°C, allez aux urgences."
        elif "ventre" in t or "diarrhee" in t:
            color, border, title = "#FFF3E0", "#EF6C00", "🤢 TROUBLE DIGESTIF"
            msg = "Risque de déshydratation. **Recette SRO :** 1L eau bouillie + 6 morceaux sucre + 1 pincée sel. Boire souvent."
        else:
            color, border, title = "#F5F5F5", "#9E9E9E", "ℹ️ CONSEIL GÉNÉRAL"
            msg = "Symptômes légers détectés. Reposez-vous et surveillez la température toutes les 4 heures."
        
        st.markdown(f'<div class="resultat" style="background:{color}; border-left-color:{border};"><h3>{title}</h3><p>{msg}</p></div>', unsafe_allow_html=True)

with tab3:
    st.subheader("Guide Vidal Côte d'Ivoire")
    m = st.text_input("Nom du médicament (ex: Panado, Coartem...)", key="m")
    if st.button("VOIR LA NOTICE"):
        search = normaliser(m)
        found = False
        for key, data in VIDAL_DATA.items():
            if search in key or key in search:
                st.markdown(f"""<div class="resultat" style="background:#E3F2FD; border-left-color:#1976D2;">
                    <h3>{data['nom']}</h3>
                    <p><b>Usage :</b> {data['info']}</p>
                    <p><b>Dosage :</b> {data['dose']}</p>
                    <p style="color:#C62828;"><b>{data['alerte']}</b></p>
                </div>""", unsafe_allow_html=True)
                found = True
        if not found: st.error("Médicament non trouvé dans la base locale. Consultez un pharmacien.")

import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# --- CONFIGURATION ÉCRAN ---
st.set_page_config(page_title="SanteCI Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, label, span { color: #1A1A1A !important; }
    /* Style des boutons de validation */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        border: none;
        color: white;
        background-color: #00AB66;
        padding: 10px;
        font-weight: bold;
    }
    .stButton>button:hover { background-color: #008f55; border: none; color: white; }
    /* Zones de texte */
    textarea, input { 
        background-color: #F8F9FA !important; 
        color: #000000 !important; 
        border: 2px solid #00AB66 !important; 
    }
    .result-box { padding: 20px; border-radius: 15px; margin-top: 15px; border-left: 10px solid; }
    </style>
""", unsafe_allow_html=True)

# --- BASE DE DONNÉES VIDAL ÉLARGIE ---
VIDAL_DB = {
    "paracetamol": {
        "nom": "Paracétamol (Doliprane, Efferalgan)",
        "usage": "Fièvre et douleurs légères à modérées.",
        "dosage": "Adulte : 1g max par prise, toutes les 6h. Max 4g/jour.",
        "danger": "Attention au foie. Ne jamais associer avec de l'alcool."
    },
    "amoxicilline": {
        "nom": "Amoxicilline (Antibiotique)",
        "usage": "Infections bactériennes (angine, otite).",
        "dosage": "Selon prescription. Généralement 1g matin et soir.",
        "danger": "Allergie possible. Finir impérativement le traitement."
    },
    "artemether": {
        "nom": "Artéméther / Luméfantrine (Coartem)",
        "usage": "Traitement curatif du Paludisme.",
        "dosage": "Cure de 3 jours selon le poids. Respectez les heures.",
        "danger": "Prendre avec un repas riche en graisses (lait, huile)."
    },
    "betadine": {
        "nom": "Bétadine (Dermique)",
        "usage": "Antiseptique pour nettoyer les plaies.",
        "dosage": "Usage externe uniquement.",
        "danger": "Vérifier l'allergie à l'iode."
    }
}

# --- FONCTIONS ---
@st.cache_data(ttl=3600)
def charger_gardes():
    try:
        url = "https://annuaireci.com/pharmacies-de-garde/"
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, 'html.parser')
        return [i.text.strip() for i in soup.find_all(['p', 'li']) if re.search(r'\d{2}\s\d{2}', i.text)]
    except: return []

def analyse_ada(texte):
    t = texte.lower()
    if any(x in t for x in ["poitrine", "bras", "bouche tordue", "parle mal"]):
        return ("#FFEBEE", "#D32F2F", "🔴 URGENCE VITALE (AVC/COEUR)", 
                "**Action immédiate :** Allongez la personne. Ne donnez ni eau ni médicament. Appelez le SAMU (185) ou les Pompiers (180).")
    if any(x in t for x in ["fievre", "chaud", "palu"]):
        return ("#E8F5E9", "#2E7D32", "🟡 SUSPICION PALUDISME", 
                "**Action :** Prenez la température. Douche tiède. Si > 39°C ou frissons, test TDR en pharmacie. **Remède maison :** Hydratation intense.")
    if any(x in t for x in ["diarrhee", "vomit", "ventre"]):
        return ("#FFF3E0", "#EF6C00", "🟡 TROUBLE DIGESTIF", 
                "**Action :** Risque de déshydratation. **Remède maison (SRO) :** 1L eau bouillie + 6 morceaux de sucre + 1 pincée de sel. Boire par petites gorgées.")
    return ("#F5F5F5", "#616161", "⚪ CONSEIL GÉNÉRAL", "Symptômes non critiques. Reposez-vous et surveillez l'évolution sur 12h.")

# --- INTERFACE ---
st.title("🛡️ SanteCI : Assistant Pro v3.0")
tabs = st.tabs(["💊 Pharmacies de Garde", "🩺 Diagnostic Intelligent", "📚 Guide Vidal"])

# ONGLET 1 : GARDES
with tabs[0]:
    st.subheader("📍 Trouver une pharmacie ouverte")
    recherche = st.text_input("Tapez votre commune (ex: Yopougon, Cocody...)")
    btn_garde = st.button("VALIDER LA RECHERCHE")
    if btn_garde or recherche:
        liste = charger_gardes()
        trouve = False
        for item in liste:
            if recherche.lower() in item.lower():
                st.markdown(f'<div style="background:#f9f9f9; padding:15px; border-radius:10px; border-left:5px solid #00AB66; margin-bottom:10px; color:black;">{item}</div>', unsafe_allow_html=True)
                trouve = True
        if not trouve and recherche: st.warning("Aucune pharmacie trouvée pour cette zone.")

# ONGLET 2 : DIAGNOSTIC
with tabs[1]:
    st.subheader("🤔 Analyseur de Symptômes")
    symptome = st.text_area("Décrivez votre problème (âge, douleurs, durée...)", height=150)
    btn_diag = st.button("VALIDER ET ANALYSER MON ÉTAT")
    if btn_diag:
        if len(symptome) > 3:
            bg, border, titre, conseil = analyse_ada(symptome)
            st.markdown(f'<div style="background:{bg}; border-left:10px solid {border}; padding:20px; border-radius:15px; color:black;"><h3>{titre}</h3><p style="font-size:18px;">{conseil}</p></div>', unsafe_allow_html=True)
        else:
            st.error("Veuillez décrire vos symptômes plus précisément.")

# ONGLET 3 : VIDAL
with tabs[2]:
    st.subheader("📚 Référentiel Médicaments")
    nom_med = st.text_input("Entrez le nom du médicament (ex: Paracétamol, Coartem...)")
    btn_med = st.button("VALIDER ET VOIR LA NOTICE")
    if btn_med:
        search_key = nom_med.lower().strip()
        # Recherche intelligente dans la base
        found = False
        for key in VIDAL_DB:
            if key in search_key:
                info = VIDAL_DB[key]
                st.markdown(f"""<div style="background:#E3F2FD; border-left:10px solid #1976D2; padding:20px; border-radius:15px; color:black;">
                    <h3>{info['nom']}</h3>
                    <p><b>Usage :</b> {info['usage']}</p>
                    <p><b>Dosage :</b> {info['dosage']}</p>
                    <p style="color:#C62828;"><b>⚠️ Attention :</b> {info['danger']}</p>
                </div>""", unsafe_allow_html=True)
                found = True
        if not found:
            st.error("Ce médicament n'est pas encore dans notre base locale. Veuillez consulter votre pharmacien.")

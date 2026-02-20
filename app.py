import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# --- CONFIGURATION ÉCRAN & VISIBILITÉ ---
st.set_page_config(page_title="Mon Assistant Santé CI", layout="wide")

# CSS pour forcer le texte noir sur fond clair (Anti-bug écran blanc)
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, label, span { color: #1A1A1A !important; }
    textarea, input { 
        background-color: #F0F2F6 !important; 
        color: #000000 !important; 
        border: 2px solid #00AB66 !important; 
    }
    .card { background: white; padding: 15px; border-radius: 10px; border-left: 8px solid #00AB66; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 15px; color: black; }
    .ada-box { background: #F3E5F5; padding: 20px; border-radius: 10px; border-left: 10px solid #7B1FA2; color: #4A148C; }
    .vidal-box { background: #E3F2FD; padding: 20px; border-radius: 10px; border-left: 10px solid #1976D2; color: #0D47A1; }
    </style>
""", unsafe_allow_html=True)

# --- 1. FONCTION GARDE (LIVE SCRAPING) ---
@st.cache_data(ttl=3600)
def charger_gardes():
    try:
        url = "https://annuaireci.com/pharmacies-de-garde/"
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, 'html.parser')
        return [i.text.strip() for i in soup.find_all(['p', 'li']) if re.search(r'\d{2}\s\d{2}', i.text)]
    except: return []

# --- 2. MOTEUR DIAGNOSTIC (ADA STYLE) ---
def moteur_ada(texte):
    t = texte.lower()
    if any(x in t for x in ["poitrine", "bras", "paralyse", "bouche"]):
        return "🔴 ALERTE URGENCE", "Signes possibles d'AVC ou infarctus. Appelez le 185 (SAMU) immédiatement.", "Hôpital / CHU"
    if any(x in t for x in ["fievre", "chaud", "palu", "corps"]):
        return "🟡 SUSPICION PALUDISME", "Remède : Douche tiède, hydratation intense. Si la fièvre dure > 48h, faites un test TDR.", "Pharmacie / Clinique"
    if any(x in t for x in ["ventre", "diarrhee", "vomit"]):
        return "🟡 TROUBLE DIGESTIF", "Remède : Solution SRO (1L eau + 6 sucres + 1 pincée sel). Évitez les graisses.", "Pharmacie"
    return "⚪ ANALYSE FINIE", "Symptômes non critiques. Reposez-vous et surveillez l'évolution.", "Général"

# --- 3. INFOS MÉDICAMENTS (VIDAL STYLE) ---
def moteur_vidal(nom):
    db = {
        "paracetamol": "Indication : Fièvre et Douleur. Dose : 1g max par prise. Max 4g/jour pour un adulte.",
        "artemether": "Indication : Paludisme. À prendre absolument avec un repas gras pour l'efficacité.",
        "amoxicilline": "Indication : Antibiotique. Finissez toute la boîte même si vous vous sentez mieux.",
        "metronidazole": "Indication : Infection intestinale. Interdiction stricte de boire de l'alcool.",
        "efferalgan": "Indication : Douleurs et Fièvre (Paracétamol). Respectez 6h entre chaque prise."
    }
    return db.get(nom.lower().strip(), "Médicament non listé. Consultez la notice ou demandez au pharmacien.")

# --- NAVIGATION ---
st.title("🛡️ Mon Assistant Santé CI")
tabs = st.tabs(["💊 Gardes Live", "🩺 Diagnostic Ada", "📚 Infos Vidal"])

with tabs[0]:
    st.subheader("Pharmacies de garde en Côte d'Ivoire")
    ville = st.text_input("Chercher par ville ou quartier (ex: Cocody, Bouaké...)", key="search_live")
    liste_gardes = charger_gardes()
    if liste_gardes:
        for item in liste_gardes:
            if ville.lower() in item.lower():
                st.markdown(f'<div class="card">{item}</div>', unsafe_allow_html=True)
                nom_p = item.split('-')[0].strip()
                st.link_button(f"🗺️ Itinéraire {nom_p}", f"https://www.google.com/maps/search/{nom_p.replace(' ', '+')}")

with tabs[1]:
    st.subheader("Analyseur de Symptômes Intelligent")
    query = st.text_area("Que ressentez-vous ? (Symptômes, durée, âge...)", height=150, placeholder="Ex: Mon enfant a de la fièvre depuis hier...")
    if st.button("Lancer l'Analyse"):
        titre, avis, orientation = moteur_ada(query)
        st.markdown(f'<div class="ada-box"><h3>{titre}</h3><p>{avis}</p><b>📍 Direction : {orientation}</b></div>', unsafe_allow_html=True)

with tabs[2]:
    st.subheader("Informations Médicaments")
    med_q = st.text_input("Entrez le nom d'un médicament...")
    if med_q:
        info = moteur_vidal(med_q)
        st.markdown(f'<div class="vidal-box"><b>Info {med_q} :</b><br>{info}</div>', unsafe_allow_html=True)

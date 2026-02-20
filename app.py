import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# CONFIGURATION VISUELLE (Pour bien voir sur téléphone)
st.set_page_config(page_title="SanteCI 3-en-1", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, label, span { color: #1A1A1A !important; }
    textarea, input { 
        background-color: #F8F9FA !important; 
        color: #000000 !important; 
        border: 2px solid #00AB66 !important; 
    }
    .box-garde { background: white; padding: 15px; border-radius: 10px; border-left: 8px solid #00AB66; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 10px; color: black; }
    .box-ada { background: #F3E5F5; padding: 15px; border-radius: 10px; border-left: 8px solid #7B1FA2; color: #4A148C; margin-bottom: 10px; }
    .box-vidal { background: #E3F2FD; padding: 15px; border-radius: 10px; border-left: 8px solid #1976D2; color: #0D47A1; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- FONCTION 1 : PHARMACIES DE GARDE (Vidal/Meditec style) ---
@st.cache_data(ttl=3600)
def charger_gardes():
    try:
        url = "https://annuaireci.com/pharmacies-de-garde/"
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, 'html.parser')
        # On récupère les lignes qui ressemblent à une pharmacie avec un numéro
        lignes = [i.text.strip() for i in soup.find_all(['p', 'li']) if re.search(r'\d{2}\s\d{2}', i.text)]
        return lignes
    except: return []

# --- FONCTION 2 : ANALYSE DES SYMPTÔMES (Ada style) ---
def moteur_ada(texte):
    t = texte.lower()
    if any(x in t for x in ["poitrine", "bras", "paralyse", "bouche"]):
        return "🔴 URGENCE CRITIQUE", "Signes d'AVC ou Coeur. Appelez le 185 immédiatement. Ne donnez rien à boire.", "CHU / SAMU"
    if any(x in t for x in ["fievre", "chaud", "palu"]):
        return "🟡 SUSPICION PALUDISME", "Reposez-vous et hydratez-vous. Si la fièvre dure plus de 2 jours, faites un test TDR.", "Pharmacie"
    if any(x in t for x in ["ventre", "diarrhee"]):
        return "🟡 PROBLÈME DIGESTIF", "Prenez du SRO (Eau + Sucre + Sel). Surveillez l'hydratation.", "Pharmacie"
    return "⚪ ANALYSE", "Symptômes légers. Reposez-vous et surveillez.", "Général"

# --- FONCTION 3 : INFOS MÉDICAMENTS (Vidal style) ---
def dictionnaire_vidal(nom):
    db = {
        "paracetamol": "Contre la fièvre et douleur. Max 3g à 4g par jour. Intervalle de 6h entre prises.",
        "artemether": "Traitement du Paludisme. À prendre avec un repas un peu gras.",
        "amoxicilline": "Antibiotique. Ne jamais arrêter avant la fin, même si vous allez mieux.",
        "efferalgan": "C'est du Paracétamol. Utile pour la fièvre. Max 4g par jour.",
    }
    return db.get(nom.lower().strip(), "Médicament non trouvé. Demandez à votre pharmacien.")

# --- L'INTERFACE UTILISATEUR ---
st.title("🛡️ Mon Assistant Santé CI")
onglets = st.tabs(["💊 Gardes", "🩺 Diagnostic", "📚 Médicaments"])

with onglets[0]:
    st.subheader("Pharmacies de garde en direct")
    ville = st.text_input("Chercher votre ville ou quartier...")
    liste = charger_gardes()
    for item in liste:
        if ville.lower() in item.lower():
            st.markdown(f'<div class="box-garde">{item}</div>', unsafe_allow_html=True)

with onglets[1]:
    st.subheader("Analyseur Intelligent (Ada)")
    symptome = st.text_area("Que ressentez-vous ?", placeholder="Ex: J'ai mal à la tête depuis ce matin...")
    if st.button("Analyser"):
        titre, conseil, direction = moteur_ada(symptome)
        st.markdown(f'<div class="box-ada"><h3>{titre}</h3><p>{conseil}</p><b>📍 Direction : {direction}</b></div>', unsafe_allow_html=True)

with onglets[2]:
    st.subheader("Infos Médicaments (Vidal)")
    med = st.text_input("Nom du médicament (ex: Paracétamol)")
    if med:
        info = dictionnaire_vidal(med)
        st.markdown(f'<div class="box-vidal"><b>{med} :</b><br>{info}</div>', unsafe_allow_html=True)

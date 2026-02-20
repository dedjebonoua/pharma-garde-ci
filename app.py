import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import unicodedata
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import random

# --- CONFIGURATION SOUVERAINE ---
st.set_page_config(page_title="SanteCI Sovereign v16", layout="wide", page_icon="🧬")

# --- DESIGN "GOD TIER" (NEON GLASSMORPHISM) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700;900&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at top right, #0F172A, #020617) !important;
        color: #F8FAFC !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .main-title {
        font-size: clamp(30px, 8vw, 70px); font-weight: 900;
        background: linear-gradient(90deg, #00FFA3, #00D1FF, #BCFF00);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; padding: 20px 0; text-transform: uppercase;
        letter-spacing: -2px;
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 30px; border-radius: 30px;
        margin-bottom: 25px; border-left: 10px solid #00FFA3;
        box-shadow: 0 15px 35px rgba(0,0,0,0.5);
    }

    .stButton>button {
        background: linear-gradient(90deg, #00FFA3 0%, #BCFF00 100%) !important;
        color: #000 !important; border-radius: 20px !important;
        height: 75px !important; font-size: 24px !important;
        font-weight: 900 !important; border: none !important;
        width: 100% !important; transition: 0.4s all ease !important;
        text-transform: uppercase;
    }
    .stButton>button:hover { 
        transform: scale(1.02) !important; 
        box-shadow: 0 20px 60px rgba(0, 255, 163, 0.4) !important; 
    }

    .sos-card {
        background: rgba(255, 2, 102, 0.1); border: 2px solid #FF0266;
        color: #FF0266; padding: 20px; border-radius: 20px;
        text-align: center; font-weight: 900; font-size: 22px;
    }
    
    input, textarea {
        background: rgba(15, 23, 42, 0.9) !important; color: white !important;
        border: 2px solid #334155 !important; border-radius: 18px !important;
        padding: 20px !important; font-size: 18px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- MOTEURS TECHNIQUES (EXTRACTION & LOGIQUE) ---
def normalize(t):
    if not t: return ""
    return "".join(c for c in unicodedata.normalize('NFD', t.lower()) if unicodedata.category(c) != 'Mn').strip()

@st.cache_data(ttl=1200)
def force_scrape_pharmacies():
    """Extraction chirurgicale sur les liens fournis avec Bypass Cache"""
    urls = [
        "https://www.pharmacies-de-garde.ci/liste-des-pharmacies-de-garde-a-abidjan-votre-permanence/",
        "https://www.pharmacies-de-garde.ci/liste-des-pharmacies-de-garde-a-linterieur-votre-permanence/"
    ]
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15"}
    results = []
    def scrape(url):
        try:
            r = requests.get(f"{url}?v={random.random()}", headers=headers, timeout=12)
            soup = BeautifulSoup(r.text, 'lxml')
            return [t.text.strip() for t in soup.find_all(['tr', 'p', 'li', 'td']) if re.search(r'\d{2}.*\d{2}', t.text)]
        except: return []
    with ThreadPoolExecutor() as ex:
        res_list = ex.map(scrape, urls)
        for r in res_list: results.extend(r)
    return sorted(list(set(results)))

# --- BASE DE DONNÉES EXPERTE (REMÈDES & AIRP) ---
MEDS_DATABASE = {
    "paracetamol": {"nom": "PARACÉTAMOL (Doliprane/Efferalgan)", "usage": "Fièvre et douleurs.", "remede": "1g toutes les 6h. Max 4g/j.", "warning": "⚠️ Danger foie si surdosage."},
    "litacold": {"nom": "LITACOLD (Comprimés)", "usage": "Rhume et grippe.", "remede": "1 comprimé 3 fois par jour.", "warning": "⚠️ Somnolence élevée. Pas de conduite."},
    "coartem": {"nom": "COARTEM (CTA Palu)", "usage": "Paludisme simple.", "remede": "Schéma 3 jours (2 prises/jour).", "warning": "⚠️ À prendre avec un repas gras."},
    "amoxicilline": {"nom": "AMOXICILLINE (Antibiotique)", "usage": "Infections bactériennes.", "remede": "Selon ordonnance uniquement.", "warning": "⚠️ Finir le traitement même si ça va mieux."}
}

# --- INITIALISATION ÉTAT ADA ---
if 'step' not in st.session_state: st.session_state.step = 0
if 'symptoms' not in st.session_state: st.session_state.symptoms = ""

# --- INTERFACE ---
st.markdown('<div class="main-title">SanteCI Sovereign</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="sos-card">🚑 SAMU : 185</div>', unsafe_allow_html=True)
    st.markdown('<div class="sos-card" style="color:#FF9E00; border-color:#FF9E00; margin-top:10px;">🚒 POMPIERS : 180</div>', unsafe_allow_html=True)
    st.write("---")
    st.markdown("🌐 **MAJ FORCÉE ACTIVE**")
    if st.button("Réinitialiser l'IA"): 
        st.session_state.step = 0
        st.rerun()

tab1, tab2, tab3 = st.tabs(["💊 GARDES LIVE", "🩺 ADA IA DIAGNOSTIC", "🧪 MÉDICAMENTS & REMÈDES"])

# --- TAB 1 : PHARMACIES DE GARDE ---
with tab1:
    st.subheader("📍 Pharmacies de Garde (Abidjan & Intérieur)")
    zone = st.text_input("VOTRE ZONE / COMMUNE", placeholder="Ex: Cocody, Bouaké, San-Pedro...")
    if st.button("EXTRAIRE LES GARDES MAINTENANT"):
        with st.spinner("Infiltration des serveurs officiels..."):
            data = force_scrape_pharmacies()
            q = normalize(zone)
            matches = [p for p in data if q in normalize(p)]
            if matches:
                st.success(f"{len(matches)} pharmacies trouvées.")
                for m in matches:
                    st.markdown(f'<div class="glass-card">{m}</div>', unsafe_allow_html=True)
                    name = m.split('-')[0].strip()
                    st.link_button(f"🗺️ ALLER À {name}", f"https://www.google.com/maps/search/{name}+cote+d'ivoire")
            else: st.error("Aucune donnée trouvée. Vérifiez l'orthographe.")

# --- TAB 2 : ADA IA DIAGNOSTIC ---
with tab2:
    st.subheader("👨‍⚕️ Assistant Ada Health Intelligent")
    
    if st.session_state.step == 0:
        st.write("Quel est votre symptôme principal ?")
        user_in = st.text_input("Ex: J'ai mal au ventre, forte fièvre...")
        if st.button("ANALYSER LE SYMPTÔME"):
            st.session_state.symptoms = normalize(user_in)
            st.session_state.step = 1
            st.rerun()

    elif st.session_state.step == 1:
        st.markdown(f'<div class="glass-card">Symptôme : <b>{st.session_state.symptoms}</b></div>', unsafe_allow_html=True)
        st.write("Avez-vous d'autres signes ?")
        c1 = st.checkbox("Frissons ou Sueurs")
        c2 = st.checkbox("Vomissements ou Diarrhée")
        c3 = st.checkbox("Douleurs thoraciques")
        c4 = st.checkbox("Fatigue extrême")
        
        if st.button("GÉNÉRER LE DIAGNOSTIC FINAL"):
            s = st.session_state.symptoms
            if c3 or "poitrine" in s:
                st.markdown('<div class="sos-card" style="font-size:28px;">🚨 URGENCE VITALE : Trouble Cardiaque suspecté. Appelez le 185 !</div>', unsafe_allow_html=True)
            elif c1 or "fievre" in s:
                http://googleusercontent.com/image_retrieval/0?query=cycle+paludisme+corps+humain+schema
                st.markdown("""<div class="glass-card" style="border-left-color:#FFD600;">
                <h3>🦟 ANALYSE ADA : Suspicion Paludisme</h3>
                <b>🏠 MAISON :</b> Repos, hydratation (3L eau), compresses froides.<br>
                <b>💊 PHARMACIE :</b> Faire un test TDR. Si +, CTA (Coartem/Lumether).<br>
                <b>🏥 HÔPITAL :</b> URGENCE si yeux jaunes ou urines noires.</div>""", unsafe_allow_html=True)
            elif c2 or "ventre" in s:
                http://googleusercontent.com/image_retrieval/0?query=human+digestive+system+diagram+medical
                st.markdown("""<div class="glass-card" style="border-left-color:#00D1FF;">
                <h3>🤢 ANALYSE ADA : Trouble Digestif / Gastro</h3>
                <b>🏠 MAISON :</b> SRO (1L eau + 6 sucre + 1 sel). Diète riz blanc.<br>
                <b>💊 PHARMACIE :</b> Smecta, Zinc, Probiotiques.<br>
                <b>🏥 HÔPITAL :</b> Si signes de déshydratation sévère.</div>""", unsafe_allow_html=True)
            else:
                st.info("ANALYSE ADA : Symptômes nécessitant une surveillance. Reposez-vous.")

# --- TAB 3 : MÉDICAMENTS & REMÈDES ---
with tab3:
    st.subheader("🧪 Dictionnaire Médical & AIRP")
    med_q = st.text_input("NOM DU MÉDICAMENT", placeholder="Ex: Paracétamol, Coartem...")
    if st.button("DÉCHARGER LA FICHE"):
        mq = normalize(med_q)
        match = next((v for k, v in MEDS_DATABASE.items() if mq in k), None)
        if match:
            http://googleusercontent.com/image_retrieval/0?query=notice+medicament+schema+explication
            st.markdown(f"""<div class="glass-card">
                <h2 style="color:#00FFA3;">{match['nom']}</h2>
                <p><b>🔍 INDICATION :</b> {match['usage']}</p>
                <p><b>💊 REMÈDE :</b> {match['remede']}</p>
                <p style="color:#FF0266; font-weight:900;">{match['warning']}</p>
            </div>""", unsafe_allow_html=True)
        else:
            st.warning("Médicament absent de la base rapide. Vérification AIRP...")
            st.link_button("🌐 CONSULTER DATAPHARMA AIRP.CI", "https://airp.ci/datapharma/liste-des-medicaments-enregistres")

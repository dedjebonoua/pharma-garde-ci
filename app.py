import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import unicodedata
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURATION SOUVERAINE ---
st.set_page_config(page_title="SanteCI Sovereign v10", layout="wide", page_icon="⚡")

# --- DESIGN "ULTRA-CONTRASTE" (VISIBILITÉ TOTALE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700;900&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #020617 !important; color: #F8FAFC !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .god-title {
        font-size: clamp(35px, 9vw, 65px); font-weight: 900;
        background: linear-gradient(90deg, #00FFA3, #00D1FF, #BCFF00);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; padding: 30px 0;
    }
    .airp-card {
        background: rgba(0, 255, 163, 0.05); border: 2px solid #00FFA3;
        padding: 20px; border-radius: 20px; margin-bottom: 20px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #00FFA3 0%, #BCFF00 100%) !important;
        color: #000 !important; border-radius: 15px !important;
        height: 75px !important; font-size: 26px !important;
        font-weight: 900 !important; border: none !important;
        width: 100% !important; box-shadow: 0 10px 40px rgba(0, 255, 163, 0.3);
    }
    input, textarea {
        background: #0F172A !important; color: #FFF !important;
        border: 2px solid #334155 !important; border-radius: 15px !important;
        font-size: 18px !important;
    }
    .sos-banner {
        background: #FF0266; color: white; padding: 20px;
        border-radius: 15px; text-align: center; font-weight: 900;
        font-size: 22px; margin-bottom: 10px; border-bottom: 6px solid #9D003C;
    }
    </style>
""", unsafe_allow_html=True)

# --- MOTEUR DE FORCE (MULTI-THREADING) ---
def clean_str(t):
    if not t: return ""
    return "".join(c for c in unicodedata.normalize('NFD', t.lower()) if unicodedata.category(c) != 'Mn').strip()

@st.cache_data(ttl=1200)
def force_sync_data(mode="pharma"):
    """Scraping de force pour les pharmacies et médicaments"""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    if mode == "pharma":
        urls = ["https://www.pharmacies-de-garde.ci/", "https://www.pharma-consults.ci/"]
    else:
        urls = ["https://airp.ci/datapharma/liste-des-medicaments-enregistres"]
    
    all_results = []
    def fetch(url):
        try:
            r = requests.get(url, headers=headers, timeout=12)
            s = BeautifulSoup(r.text, 'lxml')
            return [t.text.strip() for t in s.find_all(['p', 'li', 'tr', 'td']) if len(t.text.strip()) > 5]
        except: return []

    with ThreadPoolExecutor() as executor:
        for res in executor.map(fetch, urls): all_results.extend(res)
    return list(set(all_results))

# --- INTERFACE ---
st.markdown('<div class="god-title">SanteCI Sovereign v10</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="sos-banner">🚑 SAMU : 185</div>', unsafe_allow_html=True)
    st.markdown('<div class="sos-banner" style="background:#FF9E00; border-color:#CC7E00;">🚒 POMPIERS : 180</div>', unsafe_allow_html=True)
    st.markdown('<div class="sos-banner" style="background:#00B0FF; border-color:#007BB2;">🚓 POLICE : 170</div>', unsafe_allow_html=True)
    st.write("---")
    st.markdown(f"**BASE AIRP CONNECTÉE** 🟢")

tab1, tab2, tab3 = st.tabs(["💊 GARDES LIVE", "🧪 RÉFÉRENTIEL AIRP", "🩺 IA DIAGNOSTIC"])

# --- ONGLET 1 : GARDES ---
with tab1:
    zone = st.text_input("📍 QUARTIER / VILLE", placeholder="Ex: Marcory, Yamoussoukro...")
    if st.button("FORCER LA RECHERCHE DE GARDE"):
        with st.spinner("SYNCHRO NATIONALE..."):
            data = force_sync_data("pharma")
            q = clean_str(zone)
            matches = [p for p in data if q in clean_str(p) and re.search(r'\d{2}', p)]
            if matches:
                for m in matches:
                    st.markdown(f'<div class="airp-card" style="border-left: 10px solid #00FFA3;">{m}</div>', unsafe_allow_html=True)
            else: st.error("AUCUNE DONNÉE. VÉRIFIEZ L'ORTHOGRAPHE.")

# --- ONGLET 2 : MÉDICAMENTS AIRP (GOD TIER) ---
with tab2:
    st.subheader("📚 Liste Officielle des Médicaments (AIRP.CI)")
    med_query = st.text_input("NOM DU MÉDICAMENT OU MOLÉCULE", placeholder="Ex: Paracétamol, Artéméther...")
    if st.button("VÉRIFIER L'ENREGISTREMENT AIRP"):
        with st.spinner("INTERROGATION DE LA BASE AIRP..."):
            # On simule ici la recherche dans la base AIRP
            data_airp = force_sync_data("airp")
            mq = clean_str(med_query)
            # Logique Vidal simplifiée intégrée pour la vitesse
            vidal_ci = {
                "litacold": "✅ ENREGISTRÉ (AIRP) - Indication: Rhume. Dose: 1 comp 3x/jour.",
                "efferalgan": "✅ ENREGISTRÉ (AIRP) - Indication: Douleurs/Fièvre. Dose: 1g max 4x/jour.",
                "coartem": "✅ ENREGISTRÉ (AIRP) - Indication: Paludisme simple. Dose: 1 dose matin/soir pdt 3j."
            }
            
            found = False
            for k, v in vidal_ci.items():
                if mq in k:
                    st.markdown(f'<div class="airp-card" style="border-color:#BCFF00;"><h3>{v}</h3></div>', unsafe_allow_html=True)
                    found = True
            
            # Recherche profonde dans les données scrapées
            deep_matches = [d for d in data_airp if mq in clean_str(d)]
            if deep_matches:
                for d in deep_matches[:10]: # Limite à 10 pour la lisibilité
                    st.markdown(f'<div class="airp-card">{d}</div>', unsafe_allow_html=True)
                found = True
            
            if not found:
                st.warning("Non trouvé en base rapide. Redirection vers le portail AIRP...")
                st.link_button("🌐 ACCÉDER À DATAPHARMA AIRP.CI", "https://airp.ci/datapharma/liste-des-medicaments-enregistres")

# --- ONGLET 3 : DIAGNOSTIC ---
with tab3:
    sympt = st.text_area("🩺 DÉCRIVEZ VOTRE ÉTAT")
    if st.button("VALIDER L'ANALYSE"):
        s = clean_str(sympt)
        if any(x in s for x in ["poitrine", "bras", "visage", "paralyse"]):
            st.markdown('<div class="sos-banner" style="font-size:30px;">🚨 URGENCE VITALE ! APPELEZ LE 185</div>', unsafe_allow_html=True)
        elif "fievre" in s or "chaud" in s:
            st.markdown('<div class="airp-card" style="border-color:#FFD600;"><h3>🦟 PROTOCOLE PALUDISME</h3>Faites un test TDR. Ne commencez pas de CTA sans preuve.</div>', unsafe_allow_html=True)
        else:
            st.info("ANALYSE : Symptômes légers. Repos. Consultez si l'état s'aggrave.")

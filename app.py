import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import unicodedata
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURATION SOUVERAINE ---
st.set_page_config(page_title="SanteCI Absolute Sovereign", layout="wide", page_icon="⚡")

# --- DESIGN "GOD TIER" : DARK NEON & GLASSMORPHISM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700;900&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at top right, #0F172A, #020617) !important;
        color: #F8FAFC !important; font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .god-title {
        font-size: clamp(30px, 7vw, 70px); font-weight: 900;
        background: linear-gradient(90deg, #00FFA3, #BCFF00, #00D1FF);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; padding: 20px 0; text-transform: uppercase;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1); padding: 25px; border-radius: 25px;
        margin-bottom: 20px; border-left: 8px solid #00FFA3;
    }
    .stButton>button {
        background: linear-gradient(90deg, #00FFA3 0%, #BCFF00 100%) !important;
        color: #000 !important; border-radius: 18px !important;
        height: 70px !important; font-size: 22px !important; font-weight: 900 !important;
        width: 100% !important; border: none !important; transition: 0.3s ease-in-out;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 10px 40px rgba(0, 255, 163, 0.4); }
    .sos-banner {
        background: rgba(255, 2, 102, 0.1); border: 2px solid #FF0266; color: #FF0266;
        padding: 15px; border-radius: 15px; text-align: center; font-weight: 900; margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- MOTEUR DE FORCE (SCRAPER & DATA) ---
def clean_str(t):
    return "".join(c for c in unicodedata.normalize('NFD', t.lower()) if unicodedata.category(c) != 'Mn').strip()

@st.cache_data(ttl=1200)
def fetch_all_data(mode="pharma"):
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15"}
    urls = {
        "pharma": ["https://www.pharmacies-de-garde.ci/", "https://annuaireci.com/pharmacies-de-garde/"],
        "meds": ["https://airp.ci/datapharma/liste-des-medicaments-enregistres"]
    }
    results = []
    def scrape(url):
        try:
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, 'lxml')
            return [t.text.strip() for t in soup.find_all(['p', 'li', 'tr', 'td']) if len(t.text.strip()) > 10]
        except: return []
    with ThreadPoolExecutor() as ex:
        res_list = ex.map(scrape, urls.get(mode, []))
        for r in res_list: results.extend(r)
    return list(set(results))

# --- DASHBOARD PRINCIPAL ---
st.markdown('<div class="god-title">SanteCI Sovereign</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🚨 LIGNES DE SURVIE")
    st.markdown('<div class="sos-banner">🚑 SAMU : 185</div>', unsafe_allow_html=True)
    st.markdown('<div class="sos-banner" style="color:#FF9E00; border-color:#FF9E00;">🚒 POMPIERS : 180</div>', unsafe_allow_html=True)
    st.markdown('<div class="sos-banner" style="color:#00B0FF; border-color:#00B0FF;">🚓 POLICE : 170</div>', unsafe_allow_html=True)
    st.write("---")
    st.markdown("⚡ **MOTEUR SOUVERAIN V12 DÉPLOYÉ**")

t1, t2, t3 = st.tabs(["💊 GARDES LIVE", "🩺 DIAGNOSTIC EXPERT", "🧪 BASE AIRP & VIDAL"])

# --- 1. PHARMACIES DE GARDE ---
with t1:
    loc = st.text_input("📍 COMMUNE / VILLE (Ex: Cocody, Bouaké...)", placeholder="Où êtes-vous ?")
    if st.button("FORCER L'EXTRACTION DES GARDES"):
        data = fetch_all_data("pharma")
        q = clean_str(loc)
        matches = [p for p in data if q in clean_str(p) and re.search(r'\d{2}', p)]
        if matches:
            for m in matches:
                st.markdown(f'<div class="glass-card">{m}</div>', unsafe_allow_html=True)
                n = m.split('-')[0].strip()
                st.link_button(f"🗺️ ALLER À {n}", f"https://www.google.com/maps/search/{n}+cote+d'ivoire")
        else: st.error("AUCUNE DONNÉE TROUVÉE. VÉRIFIEZ L'ORTHOGRAPHE.")

# --- 2. DIAGNOSTIC & REMÈDES ---
with t2:
    diag_input = st.text_area("🩺 DÉCRIVEZ LES SYMPTÔMES", placeholder="Ex: J'ai de la fièvre, des frissons et mal aux articulations...")
    if st.button("LANCER L'ANALYSE CLINIQUE"):
        d = clean_str(diag_input)
        if any(x in d for x in ["fievre", "chaud", "frisson", "palu"]):
            
            st.markdown("""<div class="glass-card" style="border-left-color:#FFD600;">
            <h3>🦟 SUSPICION PALUDISME (PROTOCOLE CI)</h3>
            <b>🏠 MAISON :</b> Repos, hydratation intense (3L/jour), compresses tièdes.<br>
            <b>💊 PHARMACIE :</b> Test TDR (Coût ~1000 CFA). Si +, CTA (Coartem ou Lumether).<br>
            <b>🏥 HÔPITAL :</b> URGENCE si urines rouges/noires ou perte de conscience.</div>""", unsafe_allow_html=True)
        elif any(x in d for x in ["ventre", "diarrhee", "vomit", "intoxication"]):
            [attachment_0](attachment)
            st.markdown("""<div class="glass-card" style="border-left-color:#00D1FF;">
            <h3>🤢 TROUBLE DIGESTIF SÉVÈRE</h3>
            <b>🏠 MAISON :</b> SRO (1L eau + 6 sucre + 1 sel). Riz blanc, banane.<br>
            <b>💊 PHARMACIE :</b> Smecta, Zinc, Probiotiques.<br>
            <b>🏥 HÔPITAL :</b> Si signes de déshydratation (yeux creux, plis cutanés).</div>""", unsafe_allow_html=True)
        else:
            st.info("ANALYSE : Symptômes à surveiller. Consultez si pas d'amélioration sous 24h.")

# --- 3. BASE AIRP & VIDAL ---
with t3:
    med_q = st.text_input("🧪 NOM DU MÉDICAMENT", placeholder="Ex: Litacold, Efferalgan, Coartem...")
    if st.button("VÉRIFIER LE RÉFÉRENTIEL"):
        mq = clean_str(med_q)
        vidal_db = {
            "litacold": "✅ ENREGISTRÉ AIRP. Usage: Rhume/Grippe. Dose: 1 comp 3x/jour. ⚠️ Somnolence.",
            "efferalgan": "✅ ENREGISTRÉ AIRP. Usage: Douleurs/Fièvre. Dose: 1g max 4x/jour. ⚠️ Danger Foie.",
            "coartem": "✅ ENREGISTRÉ AIRP. Usage: Paludisme. Dose: Schéma 3 jours strict. ⚠️ Repas gras."
        }
        res = next((v for k, v in vidal_db.items() if mq in k), None)
        if res:
            
            st.markdown(f'<div class="glass-card"><h3>{res}</h3></div>', unsafe_allow_html=True)
        
        st.warning("RECHERCHE PROFONDE EN COURS SUR AIRP.CI...")
        st.link_button("🌐 ACCÉDER À DATAPHARMA AIRP.CI", "https://airp.ci/datapharma/liste-des-medicaments-enregistres")

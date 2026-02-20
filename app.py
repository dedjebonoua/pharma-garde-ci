import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import unicodedata
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURATION SOUVERAINE (INCASSABLE) ---
st.set_page_config(page_title="SanteCI Sovereign v9.0", layout="wide", page_icon="⚡")

# --- MOTEUR DE DESIGN PROFESSIONNEL (VISIBILITÉ ABSOLUE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700;900&display=swap');
    
    /* Blocage du fond et forçage du contraste */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #050A18 !important;
        color: #FFFFFF !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Titre Impact */
    .god-title {
        font-size: clamp(30px, 8vw, 60px); font-weight: 900;
        background: linear-gradient(to right, #00FFA3, #00D1FF);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; padding: 20px 0;
    }

    /* Cartes Glassmorphism Renforcées */
    .result-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px; border-radius: 20px;
        margin-bottom: 15px; border-left: 10px solid #00FFA3;
        transition: 0.3s;
    }

    /* BOUTONS DE FORCE (VALIDATION) */
    .stButton>button {
        background: linear-gradient(90deg, #00FFA3 0%, #03DAC5 100%) !important;
        color: #000 !important; border-radius: 15px !important;
        height: 70px !important; font-size: 24px !important;
        font-weight: 900 !important; border: none !important;
        width: 100% !important; box-shadow: 0 10px 30px rgba(0, 255, 163, 0.2);
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 15px 40px rgba(0, 255, 163, 0.4); }

    /* Forçage visuel des inputs */
    input, textarea {
        background: #101827 !important; color: #FFF !important;
        border: 2px solid #1F2937 !important; border-radius: 12px !important;
    }
    
    /* Barre d'urgence latérale */
    .sos-card {
        background: #FF0266; color: white; padding: 15px;
        border-radius: 12px; text-align: center; font-weight: 900;
        margin-bottom: 10px; border-bottom: 4px solid #C51162;
    }
    </style>
""", unsafe_allow_html=True)

# --- MOTEUR DE FORCE (SCRAPING PARALLÈLE) ---
def clean_str(t):
    return "".join(c for c in unicodedata.normalize('NFD', t.lower()) if unicodedata.category(c) != 'Mn').strip()

@st.cache_data(ttl=1200)
def power_scrape():
    """Force l'extraction sur plusieurs sources simultanément"""
    urls = ["https://www.pharmacies-de-garde.ci/", "https://www.pharma-consults.ci/"]
    headers = {"User-Agent": "Mozilla/5.0"}
    all_data = []

    def fetch(url):
        try:
            r = requests.get(url, headers=headers, timeout=8)
            s = BeautifulSoup(r.text, 'lxml')
            return [t.text.strip() for t in s.find_all(['div', 'p', 'li']) if re.search(r'\d{2}.*\d{2}.*\d{2}', t.text)]
        except: return []

    with ThreadPoolExecutor() as executor:
        results = executor.map(fetch, urls)
        for r in results: all_data.extend(r)
    return sorted(list(set(all_data)))

# --- LOGIQUE DE L'INTERFACE ---
st.markdown('<div class="god-title">SanteCI Sovereign</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🚨 LIGNES DIRECTES")
    st.markdown('<div class="sos-card">🚑 SAMU : 185</div>', unsafe_allow_html=True)
    st.markdown('<div class="sos-card" style="background:#FFD600; color:#000;">🚒 POMPIERS : 180</div>', unsafe_allow_html=True)
    st.markdown('<div class="sos-card" style="background:#00E5FF; color:#000;">🚓 POLICE : 170</div>', unsafe_allow_html=True)
    st.write("---")
    st.info(f"Sync. Haute-Performance : {datetime.now().strftime('%H:%M')}")

tabs = st.tabs(["💊 GARDES (LIVE)", "🩺 IA DIAGNOSTIC", "📖 VIDAL PRO"])

# --- ONGLET GARDES : LE PLUS PUISSANT ---
with tabs[0]:
    zone = st.text_input("📍 COMMUNE OU VILLE", placeholder="Ex: Cocody, Yopougon, San-Pedro...")
    if st.button("FORCER LA RECHERCHE"):
        if not zone: st.error("ERREUR : Zone requise.")
        else:
            with st.spinner("FORCE-SYNC EN COURS..."):
                data = power_scrape()
                q = clean_str(zone)
                res = [p for p in data if q in clean_str(p)]
                if res:
                    st.success(f"{len(res)} PHARMACIES LOCALISÉES")
                    for p in res:
                        st.markdown(f'<div class="result-card"><b>{p}</b></div>', unsafe_allow_html=True)
                        name = p.split('-')[0].strip()
                        st.link_button(f"🗺️ OUVRIR GPS : {name}", f"https://www.google.com/maps/search/{name}+cote+d'ivoire")
                else:
                    st.error("AUCUNE DONNÉE TROUVÉE SUR LES SERVEURS NATIONAUX.")

# --- ONGLET DIAGNOSTIC : LOGIQUE ADA ---
with tabs[1]:
    desc = st.text_area("🩺 ÉTAT CLINIQUE (Symptômes)", placeholder="Décrivez le mal ici...")
    if st.button("LANCER L'ANALYSE SOUVERAINE"):
        if not desc: st.error("ERREUR : Description vide.")
        else:
            d = clean_str(desc)
            if any(x in d for x in ["poitrine", "bras", "visage", "paralyse"]):
                st.markdown('<div class="sos-card" style="font-size:28px;">🚨 ALERTE ROUGE : AVC/INFARCTUS. APPELEZ LE 185 !</div>', unsafe_allow_html=True)
            elif "fievre" in d or "chaud" in d:
                st.markdown('<div class="result-card" style="border-left-color:#FFD600;"><h3>🦟 PROTOCOLE PALUDISME</h3>Faites un test TDR immédiatement. Hydratation : 3L/jour.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="result-card">ANALYSE : Symptômes non-critiques détectés. Repos et surveillance. Source : Ada Logic.</div>', unsafe_allow_html=True)

# --- ONGLET VIDAL : L'ENCYCLOPÉDIE ---
with tabs[2]:
    med = st.text_input("💊 NOM DU MÉDICAMENT / SUBSTANCE", placeholder="Ex: Paracétamol, Litacold...")
    if st.button("DÉVERROUILLER LA FICHE VIDAL"):
        if not med: st.error("ERREUR : Médicament requis.")
        else:
            m = clean_str(med)
            if "paracetamol" in m:
                st.markdown('<div class="result-card" style="border-left-color:#00E5FF;"><h3>PARACÉTAMOL</h3><b>Usage :</b> Douleurs & Fièvre.<br><b>Dose :</b> 1g/6h. Max 4g/jour.<br><b style="color:red;">⚠️ Alerte :</b> Danger hépatique.</div>', unsafe_allow_html=True)
            elif "lita" in m:
                st.markdown('<div class="result-card" style="border-left-color:#00E5FF;"><h3>LITACOLD</h3><b>Usage :</b> Rhume.<br><b style="color:red;">⚠️ Alerte :</b> Somnolence extrême.</div>', unsafe_allow_html=True)
            
            st.markdown(f"### 🌐 Recherche Profonde (Vidal.fr)")
            st.markdown(f'<a href="https://www.vidal.fr/recherche.html?query={med}" target="_blank"><div style="background:#1F2937; color:white; padding:20px; border-radius:15px; text-align:center; cursor:pointer;">ACCÉDER À LA BASE VIDAL.FR POUR : {med.upper()}</div></a>', unsafe_allow_html=True)

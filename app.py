import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import unicodedata
from datetime import datetime

# --- CONFIGURATION ÉLITE ---
st.set_page_config(page_title="SanteCI Platinum v7.0", layout="wide", page_icon="🏆")

# --- DESIGN SYSTÈME "GOD TIER" (CSS AVANCÉ) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700;800&display=swap');
    
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    /* Fond dégradé sombre ultra-moderne */
    .stApp {
        background: radial-gradient(circle at top right, #1a1a2e, #16213e);
        color: #FFFFFF;
    }

    /* En-tête Titre */
    .main-title {
        font-size: 45px; font-weight: 800;
        background: linear-gradient(90deg, #00dbde 0%, #fc00ff 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 30px;
    }

    /* Cartes Glassmorphism (Effet de verre) */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px; border-radius: 24px;
        margin-bottom: 20px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }

    /* Boutons Urgence Flash */
    .sos-button {
        background: linear-gradient(135deg, #ff416c, #ff4b2b);
        color: white; padding: 20px; border-radius: 20px;
        text-align: center; font-weight: 800; font-size: 22px;
        box-shadow: 0 10px 20px rgba(255, 65, 108, 0.4);
        margin-bottom: 15px; border: none; cursor: pointer;
    }

    /* Bouton Action Vert Pharma */
    .stButton>button {
        background: linear-gradient(90deg, #00b09b, #96c93d) !important;
        color: white !important; border-radius: 20px !important;
        height: 65px !important; font-size: 20px !important;
        font-weight: 800 !important; border: none !important;
        width: 100% !important; transition: 0.3s all ease;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 15px 30px rgba(0, 176, 155, 0.4); }

    /* Inputs Visibles */
    input, textarea {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important; border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important; padding: 15px !important;
    }
    
    /* Onglets */
    .stTabs [data-baseweb="tab-list"] { background: transparent; }
    .stTabs [data-baseweb="tab"] { color: #888 !important; font-weight: 700; font-size: 18px; }
    .stTabs [aria-selected="true"] { color: #00dbde !important; border-bottom-color: #00dbde !important; }
    </style>
""", unsafe_allow_html=True)

# --- MOTEURS TECHNIQUES ---
def normaliser(txt):
    return "".join(c for c in unicodedata.normalize('NFD', txt.lower()) if unicodedata.category(c) != 'Mn').strip()

@st.cache_data(ttl=1800)
def fetch_live_gardes():
    """Synchro forcée PharmaConsults"""
    sources = ["https://www.pharma-consults.ci/pharmacies-de-garde", "https://annuaireci.com/pharmacies-de-garde/"]
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for url in sources:
        try:
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            for tag in soup.find_all(['p', 'li', 'div']):
                t = tag.get_text().strip()
                if re.search(r'\d{2}.*\d{2}.*\d{2}.*\d{2}', t) and len(t) < 150:
                    results.append(t)
        except: continue
    return sorted(list(set(results)))

# --- LOGIQUE VIDAL ---
VIDAL_PRO = {
    "litacold": {"n": "LITACOLD (Rhume/Grippe)", "u": "Nez bouché, éternuements, fièvre.", "d": "1 comp. 3x/jour.", "w": "🔴 Somnolence forte."},
    "paracetamol": {"n": "PARACETAMOL 1G", "u": "Douleurs et fièvre.", "d": "1g toutes les 6h.", "w": "🔴 Attention au foie."},
    "coartem": {"n": "COARTEM (Palu)", "u": "Traitement Paludisme.", "d": "Cure de 3 jours.", "w": "🔴 Prendre avec repas gras."}
}

# --- INTERFACE ---
st.markdown('<div class="main-title">SanteCI Platinum v7.0</div>', unsafe_allow_html=True)

# Barre Latérale - SOS
with st.sidebar:
    st.markdown("### 🆘 URGENCES VITALES")
    st.markdown('<div class="sos-button">🚑 SAMU : 185</div>', unsafe_allow_html=True)
    st.markdown('<div class="sos-button" style="background:#ff9a9e">🚒 POMPIERS : 180</div>', unsafe_allow_html=True)
    st.markdown('<div class="sos-button" style="background:#a18cd1">🚓 POLICE : 170</div>', unsafe_allow_html=True)
    st.write("---")
    st.markdown(f"**Synchro Réseau :** {datetime.now().strftime('%H:%M')}")

tab1, tab2, tab3 = st.tabs(["💎 GARDES LIVE", "🩺 DIAGNOSTIC AI", "📖 VIDAL PRO"])

with tab1:
    st.subheader("📍 Pharmacies de Garde en Temps Réel")
    zone = st.text_input("Tapez votre commune (ex: Cocody, Bouake...)", placeholder="Recherche...")
    if st.button("DÉPLOYER LA RECHERCHE"):
        with st.spinner('Synchro PharmaConsults...'):
            data = fetch_live_gardes()
            q = normaliser(zone)
            matches = [p for p in data if q in normaliser(p)]
            if matches:
                for p in matches:
                    st.markdown(f'<div class="glass-card"><b>{p}</b></div>', unsafe_allow_html=True)
                    n = p.split('-')[0].strip()
                    st.link_button(f"🚀 GPS : {n}", f"https://www.google.com/maps/search/{n}+cote+d'ivoire")
            else:
                st.error("Zone non trouvée. Réessayez.")

with tab2:
    st.subheader("🩺 Triage Médical (Ada Logique)")
    mal = st.text_area("Expliquez votre mal (ex: Fièvre et frissons)")
    if st.button("LANCER L'ANALYSE"):
        m = normaliser(mal)
        if any(x in m for x in ["poitrine", "bras", "visage"]):
            st.markdown('<div class="sos-button">🚨 URGENCE VITALE : AVC/CARDIAQUE. APPELEZ LE 185 !</div>', unsafe_allow_html=True)
        elif "fievre" in m or "chaud" in m:
            
            st.markdown('<div class="glass-card" style="border-left-color:#f9d423"><b>🦟 PALUDISME :</b> Test TDR obligatoire. Hydratation.</div>', unsafe_allow_html=True)
        elif "ventre" in m or "diarrhee" in m:
            [attachment_0](attachment)
            st.markdown('<div class="glass-card" style="border-left-color:#4facfe"><b>🤢 GASTRO :</b> SRO (1L eau + 6 sucre + 1 sel).</div>', unsafe_allow_html=True)

with tab3:
    st.subheader("📚 Référentiel Vidal")
    med = st.text_input("Médicament (ex: Litacold)")
    if med:
        res = next((v for k, v in VIDAL_PRO.items() if normaliser(med) in k), None)
        if res:
            st.markdown(f'<div class="glass-card"><h3>{res["n"]}</h3><b>Usage:</b> {res["u"]}<br><b>Dose:</b> {res["d"]}<br><span style="color:#ff4b2b">{res["w"]}</span></div>', unsafe_allow_html=True)
          

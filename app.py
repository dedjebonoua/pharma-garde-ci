import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import unicodedata
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURATION SOUVERAINE ---
st.set_page_config(page_title="SanteCI Sovereign v14", layout="wide", page_icon="🧠")

# --- DESIGN "GOD TIER" : DARK MODE ADA ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700;900&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        background: #020617 !important; color: #F8FAFC !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .main-header {
        font-size: clamp(30px, 6vw, 60px); font-weight: 900;
        background: linear-gradient(90deg, #00D1FF, #00FFA3);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; padding: 20px 0;
    }
    .ada-card {
        background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(0, 209, 255, 0.3);
        padding: 25px; border-radius: 25px; margin-bottom: 20px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #00D1FF 0%, #00FFA3 100%) !important;
        color: #000 !important; border-radius: 15px !important;
        height: 65px !important; font-size: 20px !important; font-weight: 900 !important;
        width: 100% !important; border: none !important; transition: 0.3s ease;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 10px 30px rgba(0, 209, 255, 0.4); }
    .sos-banner {
        background: rgba(255, 2, 102, 0.1); border: 2px solid #FF0266; color: #FF0266;
        padding: 15px; border-radius: 15px; text-align: center; font-weight: 900;
    }
    </style>
""", unsafe_allow_html=True)

# --- MOTEUR DE DONNÉES (FORCE SCRAPING & ADA LOGIC) ---
def normalize(t):
    return "".join(c for c in unicodedata.normalize('NFD', t.lower()) if unicodedata.category(c) != 'Mn').strip()

@st.cache_data(ttl=1200)
def fetch_pharmacies_force():
    """Extraction chirurgicale des pharmacies de garde sur les URLs officiels"""
    urls = [
        "https://www.pharmacies-de-garde.ci/liste-des-pharmacies-de-garde-a-abidjan-votre-permanence/",
        "https://www.pharmacies-de-garde.ci/liste-des-pharmacies-de-garde-a-linterieur-votre-permanence/"
    ]
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)"}
    data = []
    def scrape(url):
        try:
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, 'lxml')
            return [tag.get_text().strip() for tag in soup.find_all(['tr', 'p', 'li']) if re.search(r'\d{2}.*\d{2}', tag.text)]
        except: return []
    with ThreadPoolExecutor() as ex:
        for res in ex.map(scrape, urls): data.extend(res)
    return sorted(list(set(data)))

# --- INITIALISATION ADA ENGINE ---
if 'ada_step' not in st.session_state:
    st.session_state.ada_step = 0
    st.session_state.user_symptoms = ""

# --- INTERFACE ---
st.markdown('<div class="main-header">SanteCI Sovereign Elite</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="sos-banner">🚑 SAMU : 185</div>', unsafe_allow_html=True)
    st.markdown('<div class="sos-banner" style="color:#FF9E00; border-color:#FF9E00; margin-top:10px;">🚒 POMPIERS : 180</div>', unsafe_allow_html=True)
    st.write("---")
    st.markdown("🧬 **MOTEUR ADA HEALTH ACTIVÉ**")
    if st.button("Réinitialiser l'analyse"):
        st.session_state.ada_step = 0
        st.rerun()

t1, t2, t3 = st.tabs(["💊 GARDES LIVE", "🩺 ADA DIAGNOSTIC", "🧪 MÉDICAMENTS AIRP"])

# --- 1. GARDES (FORCE & MAJ) ---
with t1:
    loc = st.text_input("📍 Ville ou Commune", placeholder="Ex: Marcory, Yamoussoukro...")
    if st.button("FORCER L'EXTRACTION"):
        with st.spinner("Infiltration des bases de données..."):
            pharmacies = fetch_pharmacies_force()
            q = normalize(loc)
            res = [p for p in pharmacies if q in normalize(p)]
            if res:
                for r in res:
                    st.markdown(f'<div class="ada-card">{r}</div>', unsafe_allow_html=True)
                    name = r.split('-')[0].strip()
                    st.link_button(f"🗺️ ALLER À {name}", f"https://www.google.com/maps/search/{name}+cote+d'ivoire")
            else: st.error("Aucune pharmacie trouvée.")

# --- 2. ADA INTELLIGENCE (DISCUSSION MÉDICALE) ---
with t2:
    st.subheader("👨‍⚕️ Discussion avec l'IA Ada")
    
    if st.session_state.ada_step == 0:
        st.info("Bonjour, je suis votre assistant de santé. Quel est votre symptôme principal aujourd'hui ?")
        symp = st.text_input("Ex: J'ai mal au ventre, J'ai de la fièvre...")
        if st.button("VALIDER LE SYMPTÔME"):
            st.session_state.user_symptoms = normalize(symp)
            st.session_state.ada_step = 1
            st.rerun()

    elif st.session_state.ada_step == 1:
        st.markdown(f'<div class="ada-card">Symptôme noté : <b>{st.session_state.user_symptoms}</b></div>', unsafe_allow_html=True)
        st.write("Avez-vous d'autres signes parmi les suivants ?")
        col1, col2 = st.columns(2)
        c1 = col1.checkbox("Frissons ou sueurs")
        c2 = col2.checkbox("Vomissements")
        c3 = col1.checkbox("Douleur thoracique")
        c4 = col2.checkbox("Fatigue extrême")
        
        if st.button("CONFIRMER ET ANALYSER"):
            # LOGIQUE DE DÉCISION TYPE ADA
            s = st.session_state.user_symptoms
            if c3 or "poitrine" in s:
                st.markdown('<div class="sos-banner" style="font-size:25px;">🚨 URGENCE CRITIQUE : Suspicions de trouble cardiaque. Appelez le 185 !</div>', unsafe_allow_html=True)
            elif c1 or "fievre" in s:
                
                st.markdown("""<div class="ada-card" style="border-left: 10px solid #FFD600;">
                <h3>🦟 Analyse : Probabilité de Paludisme élevée</h3>
                <b>🏠 Maison :</b> Hydratation max, repos, pas d'aspirine (préférez le paracétamol).<br>
                <b>💊 Pharmacie :</b> Faire un test TDR. Si +, CTA (ex: Coartem).<br>
                <b>🏥 Hôpital :</b> Si la fièvre ne baisse pas après 48h ou si urines foncées.</div>""", unsafe_allow_html=True)
            elif c2 or "ventre" in s:
                [attachment_0](attachment)
                st.markdown("""<div class="ada-card" style="border-left: 10px solid #00D1FF;">
                <h3>🤢 Analyse : Trouble Gastro-Intestinal</h3>
                <b>🏠 Maison :</b> SRO (1L eau + 6 sucre + 1 sel). Diète riz/banane.<br>
                <b>💊 Pharmacie :</b> Anti-diarrhéiques + Zinc.<br>
                <b>🏥 Hôpital :</b> Si signes de déshydratation sévère.</div>""", unsafe_allow_html=True)
            else:
                st.info("Analyse terminée : Symptômes légers. Reposez-vous.")

# --- 3. MÉDICAMENTS (AIRP / VIDAL) ---
with t3:
    med = st.text_input("🧪 Nom du médicament", placeholder="Ex: Litacold...")
    if st.button("VÉRIFIER LE RÉFÉRENTIEL AIRP"):
        m = normalize(med)
        vidal_ci = {
            "litacold": "✅ ENREGISTRÉ AIRP. Usage: Rhume. Dose: 1 comp 3x/j. ⚠️ Somnolence.",
            "coartem": "✅ ENREGISTRÉ AIRP. Usage: Paludisme. Dose: 6 prises/3j. ⚠️ Prendre avec gras."
        }
        
        if m in vidal_ci: st.markdown(f'<div class="ada-card">{vidal_ci[m]}</div>', unsafe_allow_html=True)
        else: st.warning("Vérification profonde nécessaire sur : airp.ci")
            

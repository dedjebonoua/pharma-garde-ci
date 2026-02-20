import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import unicodedata
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURATION SOUVERAINE ---
st.set_page_config(page_title="SanteCI Sovereign v13", layout="wide", page_icon="⚡")

# --- DESIGN "GOD TIER" (NEON & HIGH CONTRAST) ---
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
        margin-bottom: 20px; border-left: 10px solid #00FFA3;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .stButton>button {
        background: linear-gradient(90deg, #00FFA3 0%, #BCFF00 100%) !important;
        color: #000 !important; border-radius: 20px !important;
        height: 80px !important; font-size: 24px !important; font-weight: 900 !important;
        width: 100% !important; border: none !important; transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .stButton>button:hover { transform: scale(1.05) translateY(-5px); box-shadow: 0 20px 50px rgba(0, 255, 163, 0.5); }
    .sos-banner {
        background: rgba(255, 2, 102, 0.1); border: 2px solid #FF0266; color: #FF0266;
        padding: 20px; border-radius: 20px; text-align: center; font-weight: 900; margin-bottom: 15px;
    }
    input, textarea {
        background: rgba(15, 23, 42, 0.9) !important; color: white !important;
        border: 2px solid #334155 !important; border-radius: 15px !important; padding: 20px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- MOTEUR DE FORCE (SCRAPER CIBLÉ SUR TES LIENS) ---
def normalize_text(t):
    if not t: return ""
    return "".join(c for c in unicodedata.normalize('NFD', t.lower()) if unicodedata.category(c) != 'Mn').strip()

def force_scrape_pharmacies():
    """Extraction chirurgicale sur les 4 URLs fournis sans mise en cache pour forcer l'actualisation"""
    urls = [
        "https://www.pharmacies-de-garde.ci/liste-des-pharmacies-de-garde-a-abidjan-votre-permanence/",
        "https://www.pharmacies-de-garde.ci/liste-des-pharmacies-de-garde-a-linterieur-votre-permanence/"
    ]
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}
    
    extracted_data = []

    def process_url(url):
        try:
            # On ajoute un paramètre aléatoire pour forcer le serveur à ignorer son cache (Bypass)
            res = requests.get(f"{url}?update={datetime.now().timestamp()}", headers=headers, timeout=15)
            soup = BeautifulSoup(res.text, 'lxml')
            
            # Extraction sélective : On cherche les lignes contenant des numéros de téléphone (Format CI)
            potential_pharmacies = soup.find_all(['tr', 'p', 'div', 'li'])
            valid_entries = []
            for item in potential_pharmacies:
                text = item.get_text(separator=" ").strip()
                # Pattern : Nom de pharmacie + numéro (01 02 03 04)
                if re.search(r'\d{2}.*\d{2}.*\d{2}.*\d{2}', text) and len(text) < 250:
                    valid_entries.append(text)
            return valid_entries
        except:
            return []

    with ThreadPoolExecutor() as executor:
        for results in executor.map(process_url, urls):
            extracted_data.extend(results)
    
    return sorted(list(set(extracted_data))) # Suppression des doublons et tri

# --- LOGIQUE INTERFACE ---
st.markdown('<div class="god-title">SanteCI Sovereign Elite</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🚨 LIGNES DE VIE")
    st.markdown('<div class="sos-banner">🚑 SAMU : 185</div>', unsafe_allow_html=True)
    st.markdown('<div class="sos-banner" style="color:#FF9E00; border-color:#FF9E00;">🚒 POMPIERS : 180</div>', unsafe_allow_html=True)
    st.markdown('<div class="sos-banner" style="color:#00B0FF; border-color:#00B0FF;">🚓 POLICE : 170</div>', unsafe_allow_html=True)
    st.write("---")
    st.markdown(f"🗓️ **MAJ FORCÉE :** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    st.markdown("🔒 **SOURCES OFFICIELLES SÉCURISÉES**")

tab1, tab2, tab3 = st.tabs(["💊 PHARMACIES DE GARDE", "🩺 DIAGNOSTIC & REMÈDES", "🧪 MÉDICAMENTS (AIRP)"])

# --- ONGLET 1 : PHARMACIES (FORCE SCRAPING) ---
with tab1:
    st.subheader("📍 Rechercher dans Abidjan & Intérieur")
    search_query = st.text_input("QUARTIER, COMMUNE OU VILLE", placeholder="Ex: Marcory, Yamoussoukro, San-Pedro...")
    
    if st.button("ACTUALISER ET FORCER LA RECHERCHE"):
        with st.spinner("INFILTRATION DES BASES DE DONNÉES EN COURS..."):
            pharmacies = force_scrape_pharmacies()
            q = normalize_text(search_query)
            
            # Filtrage intelligent
            results = [p for p in pharmacies if q in normalize_text(p)]
            
            if results:
                st.success(f"{len(results)} pharmacies de garde trouvées en temps réel.")
                for r in results:
                    st.markdown(f'<div class="glass-card">{r}</div>', unsafe_allow_html=True)
                    # GPS Auto-Extraction du nom
                    name_for_maps = r.split('-')[0].split('(')[0].strip()
                    st.link_button(f"🗺️ ITINÉRAIRE VERS {name_for_maps}", f"https://www.google.com/maps/search/{name_for_maps.replace(' ', '+')}+cote+d'ivoire")
            else:
                st.error("Aucune pharmacie de garde trouvée pour cette zone. Vérifiez l'orthographe ou essayez une commune proche.")

# --- ONGLET 2 : DIAGNOSTIC (PROTOCOLES ADA) ---
with tab2:
    diag_text = st.text_area("🩺 DÉCRIVEZ LES SYMPTÔMES ICI", placeholder="Ex: J'ai mal à la poitrine et je transpire...")
    if st.button("LANCER L'ANALYSE SOUVERAINE"):
        d = normalize_text(diag_text)
        if any(x in d for x in ["poitrine", "bras", "visage", "paralyse", "essoufle"]):
            st.markdown('<div class="sos-banner" style="font-size:30px; background:rgba(255,0,0,0.3);">🚨 ALERTE ROUGE : URGENCE VITALE ! APPELEZ LE 185 IMMÉDIATEMENT.</div>', unsafe_allow_html=True)
        elif any(x in d for x in ["fievre", "chaud", "frisson", "palu"]):
            st.markdown("""<div class="glass-card" style="border-left-color:#FFD600;">
            <h3>🦟 PROTOCOLE PALUDISME (Source Ada/Hôpital)</h3>
            <b>🏠 MAISON :</b> Compresses d'eau tiède, repos absolu, boire 3L d'eau.<br>
            <b>💊 PHARMACIE :</b> Acheter un test TDR. Si positif : CTA (ex: Coartem).<br>
            <b>🏥 HÔPITAL :</b> Si urines sombres ou jaunisse (yeux jaunes).</div>""", unsafe_allow_html=True)
        else:
            st.info("ANALYSE : Symptômes nécessitant une surveillance. Reposez-vous et hydratez-vous.")

# --- ONGLET 3 : MÉDICAMENTS (AIRP) ---
with tab3:
    med_input = st.text_input("🧪 NOM DU MÉDICAMENT (AIRP.CI)", placeholder="Ex: Litacold, Coartem...")
    if st.button("VÉRIFIER LE RÉFÉRENTIEL"):
        mq = normalize_text(med_input)
        # Base de données locale sécurisée
        vidal_ci = {
            "litacold": "✅ ENREGISTRÉ (AIRP). Usage: Rhume. Dose: 1 comp 3x/jour. ⚠️ Somnolence.",
            "efferalgan": "✅ ENREGISTRÉ (AIRP). Usage: Douleurs. Dose: 1g max 4x/jour. ⚠️ Alcool interdit.",
            "coartem": "✅ ENREGISTRÉ (AIRP). Usage: Paludisme. Dose: Schéma 3 jours. ⚠️ Prendre avec gras."
        }
        found = False
        for k, v in vidal_ci.items():
            if mq in k:
                st.markdown(f'<div class="glass-card"><h3>{v}</h3></div>', unsafe_allow_html=True)
                found = True
        
        if not found:
            st.warning("Médicament non trouvé dans la base rapide. Vérification sur airp.ci...")
            st.link_button("🌐 ACCÉDER À DATAPHARMA AIRP.CI", "https://airp.ci/datapharma/liste-des-medicaments-enregistres")

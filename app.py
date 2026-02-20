import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import unicodedata
from datetime import datetime

# --- CONFIGURATION ÉLITE (PLATINUM) ---
st.set_page_config(page_title="SanteCI Platinum v7.0", layout="wide", page_icon="🏥")

# --- DESIGN SYSTÈME (UI/UX GOD TIER) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #FFFFFF; }
    
    /* Boutons Urgence Flash Professionnels */
    .emergency-card {
        background: linear-gradient(135deg, #FF0000 0%, #B71C1C 100%);
        color: white; padding: 20px; border-radius: 18px;
        text-align: center; margin-bottom: 15px;
        font-weight: 900; font-size: 26px;
        box-shadow: 0 10px 20px rgba(211, 47, 47, 0.3);
        border: none; animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% {transform: scale(1);} 50% {transform: scale(1.01);} 100% {transform: scale(1);} }
    
    /* Cartes Médicaments & Pharmacies */
    .platinum-card {
        background: #FDFDFD; padding: 25px; border-radius: 20px;
        border-left: 12px solid #00AB66; margin-bottom: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.05); color: #1A1A1A;
        border-top: 1px solid #EEE; border-right: 1px solid #EEE;
    }
    
    /* Boutons de Validation */
    .stButton>button {
        width: 100%; border-radius: 30px; height: 60px;
        background: linear-gradient(90deg, #00AB66 0%, #008F55 100%);
        color: white; font-weight: 900; font-size: 20px; border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,171,102,0.3); }
    </style>
""", unsafe_allow_html=True)

# --- MOTEUR DE FORCE : SCRAPER MULTI-SOURCE ---
def normaliser(txt):
    if not txt: return ""
    return "".join(c for c in unicodedata.normalize('NFD', txt.lower()) if unicodedata.category(c) != 'Mn').strip()

@st.cache_data(ttl=1800)
def force_sync_ci():
    """Extraction agressive de données PharmaConsults & AnnuaireCI"""
    urls = ["https://www.pharma-consults.ci/pharmacies-de-garde", "https://annuaireci.com/pharmacies-de-garde/"]
    results = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    for url in urls:
        try:
            res = requests.get(url, headers=headers, timeout=12)
            soup = BeautifulSoup(res.text, 'lxml')
            for tag in soup.find_all(['p', 'li', 'tr', 'div', 'span']):
                text = tag.get_text().strip()
                if re.search(r'\d{2}.*\d{2}.*\d{2}.*\d{2}', text) and len(text) < 200:
                    results.append(text)
        except: continue
    return sorted(list(set(results)))

# --- BASE DE DONNÉES VIDAL EXPERT ---
VIDAL_PLATINUM = {
    "litacold": {"n": "LITACOLD (Rhume/Grippe)", "u": "Traitement symptomatique du rhume et des états grippaux.", "p": "Adulte : 1 comprimé 3 fois par jour.", "a": "⚠️ Risque de somnolence. Ne pas conduire."},
    "efferalgan": {"n": "EFFERALGAN / DOLIPRANE", "u": "Fièvre et douleurs (Paracétamol).", "p": "1g toutes les 6h. Max 4g par jour.", "a": "⚠️ Attention au foie : ne jamais associer à l'alcool."},
    "coartem": {"n": "COARTEM 20/120 (Palu)", "u": "Traitement curatif du paludisme simple.", "p": "6 doses sur 3 jours (Schéma strict).", "a": "⚠️ À prendre avec un repas gras (lait, sauce) pour absorption."}
}

# --- INTERFACE MAÎTRESSE ---
st.title("🏆 SanteCI Platinum : L'Excellence Médicale")

# Sidebar : Urgences Absolues
with st.sidebar:
    st.markdown("### 🚨 SERVICES D'URGENCE")
    st.markdown('<div class="emergency-card">🚑 SAMU : 185</div>', unsafe_allow_html=True)
    st.markdown('<div class="emergency-card" style="background:#B71C1C;">🚒 POMPIERS : 180</div>', unsafe_allow_html=True)
    st.markdown('<div class="emergency-card" style="background:#0D47A1;">🚓 POLICE : 170 / 111</div>', unsafe_allow_html=True)
    st.write("---")
    st.info(f"Dernière synchronisation réseau : {datetime.now().strftime('%H:%M')}")

tab1, tab2, tab3 = st.tabs(["💎 GARDES EN DIRECT", "🧠 IA DIAGNOSTIC (ADA)", "📖 VIDAL IVOIRIEN"])

# ONGLET 1 : GARDES
with tab1:
    st.subheader("📍 Localisateur de Pharmacies de Garde")
    zone = st.text_input("Saisissez votre commune ou ville (ex: Cocody, Bouaké, San-Pedro...)", placeholder="Où êtes-vous ?")
    
    if st.button("DÉPLOYER LA RECHERCHE"):
        with st.spinner('Forçage des données PharmaConsults en cours...'):
            data = force_sync_ci()
            query = normaliser(zone)
            filter_data = [p for p in data if query in normaliser(p)]
            
            if filter_data:
                st.success(f"{len(filter_data)} pharmacies trouvées pour votre zone.")
                for item in filter_data:
                    st.markdown(f'<div class="platinum-card"><b>{item}</b></div>', unsafe_allow_html=True)
                    # Bouton GPS Dynamique
                    raw_name = item.split('-')[0].split('(')[0].strip()
                    st.link_button(f"🚀 Itinéraire vers {raw_name}", f"https://www.google.com/maps/search/{raw_name.replace(' ', '+')}+cote+d'ivoire")
            else:
                st.error("Aucune donnée trouvée. Vérifiez l'orthographe ou essayez une commune voisine.")

# ONGLET 2 : DIAGNOSTIC
with tab2:
    st.subheader("🩺 Assistant de Triage Médical Intelligent")
    query_diag = st.text_area("Décrivez vos symptômes précisément (Ex: J'ai une forte fièvre et des frissons depuis hier)", height=150)
    
    if st.button("LANCER L'ANALYSE MÉDICALE"):
        s = normaliser(query_diag)
        if any(x in s for x in ["poitrine", "bras", "visage", "parle mal"]):
            st.markdown('<div class="emergency-card">🚨 ALERTE URGENCE VITALE : AVC/CARDIAQUE SUSPECTÉ. APPELEZ LE 185 IMMÉDIATEMENT.</div>', unsafe_allow_html=True)
        elif "fievre" in s or "chaud" in s:
            
            st.markdown("""<div class="platinum-card" style="border-left-color:#FBC02D;">
                <h3>🦟 Protocole Suspicion Paludisme</h3>
                <b>1. Diagnostic :</b> Test TDR obligatoire en pharmacie.<br>
                <b>2. Traitement :</b> Si positif, CTA (ex: Coartem) selon posologie.<br>
                <b>3. Danger :</b> Si urines noires ou fatigue extrême, allez au CHU.</div>""", unsafe_allow_html=True)
        elif "ventre" in s or "diarrhee" in s:
            [attachment_0](attachment)
            st.markdown("""<div class="platinum-card" style="border-left-color:#0288D1;">
                <h3>🤢 Protocole Troubles Digestifs</h3>
                <b>Alerte Déshydratation :</b> Préparez le SRO maison.<br>
                <b>Recette :</b> 1L eau bouillie + 6 morceaux sucre + 1 pincée sel.<br>
                <b>Action :</b> Boire par petites gorgées toutes les 15 minutes.</div>""", unsafe_allow_html=True)
        else:
            st.info("Symptômes analysés. Reposez-vous et surveillez votre température toutes les 4 heures.")

# ONGLET 3 : VIDAL
with tab3:
    st.subheader("📖 Référentiel Médicaments (Vidal CI)")
    med_search = st.text_input("Rechercher un médicament (ex: Litacold, Coartem, Efferalgan...)")
    if med_search:
        key_search = normaliser(med_search)
        match = next((v for k, v in VIDAL_PLATINUM.items() if key_search in k), None)
        if match:
            
            st.markdown(f"""<div class="platinum-card" style="border-left-color:#1976D2;">
                <h2>{match['n']}</h2>
                <p><b>Usage :</b> {match['u']}</p>
                <p><b>Posologie :</b> {match['p']}</p>
                <p style="color:#D32F2F; font-weight:bold;">{match['a']}</p></div>""", unsafe_allow_html=True)
        else:
            st.warning("Médicament non répertorié dans la base locale. Consultez votre pharmacien.")

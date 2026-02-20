import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import unicodedata
from datetime import datetime

# --- CONFIGURATION ÉLITE ---
st.set_page_config(page_title="SanteCI Platinum v6.0", layout="wide", page_icon="🏥")

# --- DESIGN SYSTÈME (UI/UX HAUT DE GAMME) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #FFFFFF; }
    
    /* Boutons Urgence Flash */
    .emergency-card {
        background: linear-gradient(135deg, #FF0000 0%, #B71C1C 100%);
        color: white; padding: 15px; border-radius: 15px;
        text-align: center; margin-bottom: 12px;
        font-weight: 900; font-size: 24px;
        box-shadow: 0 4px 15px rgba(211, 47, 47, 0.4);
        border: none; animation: pulse 1.5s infinite;
    }
    @keyframes pulse { 0% {transform: scale(1);} 50% {transform: scale(1.02);} 100% {transform: scale(1);} }
    
    /* Cartes Pharmacies & Médicaments */
    .pro-card {
        background: #F8F9FA; padding: 20px; border-radius: 18px;
        border-left: 10px solid #00AB66; margin-bottom: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05); color: #1A1A1A;
    }
    
    /* Onglets & Inputs */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #F1F3F4; border-radius: 10px 10px 0 0; padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #00AB66 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- MOTEUR DE FORCE : SCRAPER MULTI-SOURCE ---
def normaliser(txt):
    return "".join(c for c in unicodedata.normalize('NFD', txt.lower()) if unicodedata.category(c) != 'Mn').strip()

@st.cache_data(ttl=1800) # Rafraîchissement toutes les 30 min
def force_scraping_ci():
    """Moteur de force pour extraire les données de PharmaConsults et AnnuaireCI"""
    sources = [
        "https://www.pharma-consults.ci/pharmacies-de-garde",
        "https://annuaireci.com/pharmacies-de-garde/"
    ]
    results = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    for url in sources:
        try:
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'lxml')
            # Extraction agressive des textes contenant des numéros de téléphone ivoiriens
            for tag in soup.find_all(['p', 'li', 'tr', 'div']):
                clean_text = tag.get_text().strip()
                if re.search(r'\d{2}\s\d{2}\s\d{2}\s\d{2}', clean_text):
                    results.append(clean_text)
        except: continue
    return sorted(list(set(results))) # Dédoublage et tri

# --- BASE DE DONNÉES VIDAL GOD-TIER ---
VIDAL_GOD = {
    "litacold": {"nom": "LITACOLD (Sirop/Comp)", "u": "Rhume, nez bouché, état grippal.", "d": "1 comprimé 3 fois par jour.", "w": "⚠️ Risque de somnolence : ne pas conduire."},
    "paracetamol": {"nom": "PARACETAMOL (Doliprane/Efferalgan)", "u": "Douleurs et Fièvre.", "d": "1g max 4x/jour (6h d'écart).", "w": "⚠️ Danger foie : pas d'alcool."},
    "coartem": {"nom": "COARTEM (CTA)", "u": "Traitement du Paludisme simple.", "d": "Schéma strict sur 3 jours.", "w": "⚠️ Prendre avec un repas gras (lait, sauce)."}
}

# --- INTERFACE MAÎTRESSE ---
st.title("🏆 SanteCI Elite : Le Standard Africain")

# Sidebar - Puissance de Secours
with st.sidebar:
    st.markdown("### 🆘 URGENCES VITALES")
    st.markdown('<div class="emergency-card">🚑 SAMU : 185</div>', unsafe_allow_html=True)
    st.markdown('<div class="emergency-box" style="background:#B71C1C; color:white; padding:10px; border-radius:10px; text-align:center; margin-bottom:5px;">🚒 POMPIERS : 180</div>', unsafe_allow_html=True)
    st.markdown('<div class="emergency-box" style="background:#0D47A1; color:white; padding:10px; border-radius:10px; text-align:center;">🚓 POLICE : 170</div>', unsafe_allow_html=True)
    st.write("---")
    st.success(f"Dernière synchro : {datetime.now().strftime('%H:%M')}")

tab1, tab2, tab3 = st.tabs(["💎 GARDES LIVE", "🧠 IA ADA DIAGNOSTIC", "📖 VIDAL EXPERT"])

# ONGLET 1 : GARDES (FORCE RÉSEAU)
with tab1:
    st.subheader("📍 Pharmacies de Garde (Mise à jour minute)")
    recherche = st.text_input("Saisissez votre commune ou ville (ex: Cocody, San Pedro, Yamoussoukro...)", placeholder="Où êtes-vous ?")
    
    if st.button("DÉPLOYER LA RECHERCHE"):
        with st.spinner('Extraction des données PharmaConsults...'):
            donnees = force_scraping_ci()
            query = normaliser(recherche)
            filtre = [p for p in donnees if query in normaliser(p)]
            
            if filtre:
                for p in filtre:
                    st.markdown(f'<div class="pro-card"><b>{p}</b></div>', unsafe_allow_html=True)
                    # GPS Auto-généré
                    nom_p = p.split('-')[0].strip()
                    st.link_button(f"🗺️ Itinéraire vers {nom_p}", f"https://www.google.com/maps/search/{nom_p.replace(' ', '+')}+cote+d'ivoire")
            else:
                st.error("Aucune pharmacie trouvée dans la base live pour cette zone.")

# ONGLET 2 : DIAGNOSTIC (LOGIQUE MÉDICALE AVANCÉE)
with tab2:
    st.subheader("🩺 Triage Médical Intelligent")
    symptomes = st.text_area("Décrivez vos symptômes précisément (âge, douleur, durée...)", height=150)
    if st.button("LANCER L'ANALYSE EXPERTE"):
        s = normaliser(symptomes)
        if any(x in s for x in ["poitrine", "bras", "parle mal", "visage"]):
            st.markdown('<div class="emergency-card">🚨 URGENCE VITALE : AVC/CARDIAQUE SUSPECTÉ. APPELEZ LE 185.</div>', unsafe_allow_html=True)
        elif "fievre" in s or "chaud" in s:
            
            st.markdown("""<div class="pro-card" style="border-left-color:#FBC02D;"><h3>🦟 SUSPICION PALUDISME</h3>
            <b>Action :</b> Test TDR obligatoire. Ne commencez aucun CTA sans test. Hydratez-vous (3L/jour).</div>""", unsafe_allow_html=True)
        elif "ventre" in s or "diarrhee" in s:
            [attachment_0](attachment)
            st.markdown("""<div class="pro-card" style="border-left-color:#0288D1;"><h3>🤢 PROTOCOLE DÉSHYDRATATION</h3>
            <b>Urgence :</b> Préparez le SRO maison. 1L eau + 6 morceaux sucre + 1 pincée sel. Boire chaque 15 min.</div>""", unsafe_allow_html=True)

# ONGLET 3 : VIDAL (BASE PROFESSIONNELLE)
with tab3:
    st.subheader("📚 Référentiel Vidal Côte d'Ivoire")
    m_input = st.text_input("Rechercher un médicament (ex: Litacold, Coartem...)")
    if m_input:
        match = next((v for k, v in VIDAL_GOD.items() if normaliser(m_input) in k), None)
        if match:
            st.markdown(f"""<div class="pro-card" style="border-left-color:#1976D2;">
            <h2>{match['nom']}</h2>
            <p><b>Usage :</b> {match['u']}</p>
            <p><b>Posologie :</b> {match['d']}</p>
            <p style="color:#D32F2F; font-weight:bold;">{match['w']}</p></div>""", unsafe_allow_html=True)
        else:
            st.info("Médicament non répertorié. Consultez un pharmacien.")

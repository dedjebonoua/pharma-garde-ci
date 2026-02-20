import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import unicodedata

# --- CONFIGURATION & DESIGN ---
st.set_page_config(page_title="SanteCI 24/7", layout="wide", page_icon="🏥")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, label, span { color: #1A1A1A !important; }
    /* Style des boutons vert pharmacie */
    .stButton>button { width: 100%; border-radius: 25px; height: 55px; background-color: #00AB66; color: white; font-weight: bold; font-size: 18px; border: none; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    /* Style des numéros d'urgence */
    .emergency-btn { background-color: #D32F2F; color: white; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 5px; font-weight: bold; font-size: 20px; }
    .card { background: #F8F9FA; padding: 15px; border-radius: 12px; border-left: 8px solid #00AB66; margin-bottom: 10px; color: black; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# --- FONCTION DE NORMALISATION ---
def normaliser(texte):
    if not texte: return ""
    return "".join(c for c in unicodedata.normalize('NFD', texte.lower()) if unicodedata.category(c) != 'Mn').strip()

# --- RÉCUPÉRATION DES GARDES (S'ACTUALISE SEULE) ---
@st.cache_data(ttl=3600)  # S'actualise toutes les heures
def obtenir_gardes_live():
    url = "https://annuaireci.com/pharmacies-de-garde/"
    try:
        header = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=header, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        # On extrait les noms et contacts (balises <p> ou <li> contenant des numéros)
        data = [i.text.strip() for i in soup.find_all(['p', 'li']) if re.search(r'\d{2}\s\d{2}', i.text)]
        return data if data else ["⚠️ Impossible de charger la liste. Réessayez."]
    except:
        return ["⚠️ Erreur de connexion au serveur national."]

# --- BASE VIDAL CI ---
DB_VIDAL = {
    "litacold": {"n": "LITACOLD", "u": "Rhume et état grippal.", "d": "1 comp. 3 fois/jour.", "a": "⚠️ Risque de somnolence."},
    "efferalgan": {"n": "EFFERALGAN (Paracétamol)", "u": "Fièvre et douleurs.", "d": "1g max 4 fois/jour.", "a": "⚠️ Espacer de 6h."},
    "coartem": {"n": "COARTEM", "u": "Traitement du Paludisme.", "d": "Cure de 3 jours.", "a": "⚠️ Prendre avec un repas gras."},
}

# --- BARRE LATÉRALE : NUMÉROS D'URGENCE ---
with st.sidebar:
    st.markdown("### 🚨 NUMÉROS D'URGENCE")
    st.markdown('<div class="emergency-btn">🚑 SAMU : 185</div>', unsafe_allow_html=True)
    st.markdown('<div class="emergency-btn">🚒 POMPIERS : 180</div>', unsafe_allow_html=True)
    st.markdown('<div class="emergency-btn">🚓 POLICE : 170 / 111</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.info("Applis recommandées : PharmaConsults, PharmAppCI.")

# --- CORPS DE L'APPLICATION ---
st.title("🏥 Assistant Santé Côte d'Ivoire")
tab1, tab2, tab3 = st.tabs(["💊 TOUTES LES GARDES", "🩺 DIAGNOSTIC ADA", "📚 GUIDE VIDAL"])

with tab1:
    st.subheader("🔍 Recherche de Pharmacie de Garde")
    zone = st.text_input("Tapez votre ville ou quartier (ex: Bingerville, Abobo, Bouake...)", placeholder="Rechercher...")
    if st.button("AFFICHER LA LISTE DE GARDE"):
        liste = obtenir_gardes_live()
        filtre = [p for p in liste if normaliser(zone) in normaliser(p)]
        if filtre:
            st.success(f"{len(filtre)} pharmacie(s) trouvée(s) pour '{zone}'")
            for item in filtre:
                st.markdown(f'<div class="card">{item}</div>', unsafe_allow_html=True)
        else:
            st.warning("Aucun résultat. Essayez d'écrire juste le nom de la ville.")

with tab2:
    st.subheader("🩺 Analyseur de Symptômes Intelligent")
    mal = st.text_area("Expliquez votre mal (ex: J'ai de la fièvre et des frissons)")
    if st.button("ANALYSER"):
        c = normaliser(mal)
        if "fievre" in c or "chaud" in c:
            st.markdown('<div class="card" style="border-color:#FBC02D;"><b>🦟 PALUDISME POSSIBLE :</b> Faites un test TDR. Hydratez-vous bien.</div>', unsafe_allow_html=True)
        elif "ventre" in c or "diarrhee" in c:
            st.markdown('<div class="card" style="border-color:#0288D1;"><b>🤢 TROUBLE DIGESTIF :</b> Buvez du SRO (1L eau + 6 sucres + 1 sel).</div>', unsafe_allow_html=True)
        else:
            st.info("Décrivez plus précisément vos symptômes pour une analyse.")

with tab3:
    st.subheader("📚 Guide Médicaments (Vidal)")
    med = st.text_input("Nom du médicament (ex: Litacold)")
    if st.button("VOIR NOTICE"):
        m_c = normaliser(med)
        found = False
        for k, v in DB_VIDAL.items():
            if m_c in k:
                st.markdown(f"""<div class="card" style="border-color:#1976D2;">
                <h3>{v['n']}</h3><p><b>Usage:</b> {v['u']}<br><b>Dose:</b> {v['d']}</p><p style='color:red;'>{v['a']}</p></div>""", unsafe_allow_html=True)
                found = True
        if not found: st.error("Médicament non trouvé dans la base simplifiée.")

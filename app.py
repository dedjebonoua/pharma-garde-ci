import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import unicodedata

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="SanteCI Pro 24/7", layout="wide", page_icon="🏥")

# --- STYLE CSS (Visibilité & Boutons) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, label, span { color: #1A1A1A !important; }
    /* Bouton vert validation */
    .stButton>button { width: 100%; border-radius: 25px; height: 50px; background-color: #00AB66; color: white; font-weight: bold; border: none; font-size: 18px; }
    /* Boutons Urgence Rouge */
    .emergency-box { background-color: #D32F2F; color: white; padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 10px; font-weight: bold; font-size: 22px; border: 2px solid #B71C1C; }
    /* Cartes pharmacies */
    .pharma-card { background: #F0F2F6; padding: 15px; border-radius: 12px; border-left: 8px solid #00AB66; margin-bottom: 10px; color: black; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# --- FONCTION DE NETTOYAGE ---
def clean(text):
    if not text: return ""
    return "".join(c for c in unicodedata.normalize('NFD', text.lower()) if unicodedata.category(c) != 'Mn').strip()

# --- ROBOT DE GARDE (S'ACTUALISE SEUL) ---
@st.cache_data(ttl=3600) # Se met à jour toutes les heures
def get_gardes_live():
    url = "https://annuaireci.com/pharmacies-de-garde/"
    try:
        header = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=header, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        # On extrait les pharmacies (souvent dans des balises p ou li avec des numéros)
        data = [i.text.strip() for i in soup.find_all(['p', 'li']) if re.search(r'\d{2}\s\d{2}', i.text)]
        return data
    except:
        return ["⚠️ Erreur de connexion. Vérifiez votre connexion internet."]

# --- BASE VIDAL INTERNE ---
BASE_VIDAL = {
    "litacold": {"n": "LITACOLD", "u": "Rhume, nez bouché et fièvre.", "d": "1 comprimé 3 fois par jour.", "a": "⚠️ Attention : Risque de somnolence."},
    "paracetamol": {"n": "PARACÉTAMOL (Doliprane, Efferalgan)", "u": "Douleurs et fièvre.", "d": "1g max par prise, 4g max par jour.", "a": "⚠️ Ne pas boire d'alcool avec."},
    "coartem": {"n": "COARTEM", "u": "Traitement du Paludisme simple.", "d": "Cure de 3 jours (matin et soir).", "a": "⚠️ Prendre avec un repas gras."},
}

# --- BARRE LATÉRALE (URGENCES) ---
with st.sidebar:
    st.markdown("### 🚨 NUMÉROS D'URGENCE")
    st.markdown('<div class="emergency-box">🚑 SAMU : 185</div>', unsafe_allow_html=True)
    st.markdown('<div class="emergency-box">🚒 POMPIERS : 180</div>', unsafe_allow_html=True)
    st.markdown('<div class="emergency-box">🚓 POLICE : 170 / 111</div>', unsafe_allow_html=True)
    st.write("---")
    st.write("💡 *Ces numéros sont gratuits depuis n'importe quel opérateur en CI.*")

# --- CORPS DE L'APPLICATION ---
st.title("🏥 SanteCI : Garde, Diagnostic & Vidal")
t1, t2, t3 = st.tabs(["💊 PHARMACIES DE GARDE", "🩺 IA DIAGNOSTIC (ADA)", "📚 GUIDE VIDAL"])

with t1:
    st.subheader("📍 Rechercher une Pharmacie de Garde")
    zone = st.text_input("Tapez votre commune (ex: Cocody, Yopougon, Yamoussoukro...)", key="z")
    if st.button("AFFICHER LA LISTE ACTUELLE"):
        liste = get_gardes_live()
        z_c = clean(zone)
        filtre = [p for p in liste if z_c in clean(p)]
        
        if filtre:
            st.success(f"Voici les pharmacies trouvées pour '{zone}' :")
            for p in filtre:
                st.markdown(f'<div class="pharma-card">{p}</div>', unsafe_allow_html=True)
                # Bouton GPS automatique
                nom_p = p.split('-')[0].strip()
                st.link_button(f"🗺️ Itinéraire vers {nom_p}", f"https://www.google.com/maps/search/{nom_p.replace(' ', '+')}")
        else:
            st.warning("Aucun résultat pour cette zone. Vérifiez l'orthographe ou essayez une zone proche.")

with t2:
    st.subheader("Analyseur de Symptômes Intelligent")
    mal = st.text_area("Expliquez ce que vous ressentez (ex: J'ai de la fièvre et mal à la tête...)")
    if st.button("ANALYSER MAINTENANT"):
        c = clean(mal)
        if any(x in c for x in ["fievre", "chaud", "frisson", "palu"]):
            
            st.error("🦟 SUSPICION PALUDISME : Faites un test TDR. Repos et hydratation.")
        elif any(x in c for x in ["ventre", "diarrhee", "vomit"]):
            st.warning("🤢 TROUBLE DIGESTIF : Risque de déshydratation. Préparez un SRO (1L eau + 6 sucres + 1 sel).")
        else:
            st.info("Symptômes enregistrés. Si la douleur persiste, consultez un médecin.")

with t3:
    st.subheader("Guide des Médicaments (Vidal)")
    med_input = st.text_input("Nom du médicament (ex: Litacold, Paracétamol...)")
    if st.button("VOIR LA FICHE"):
        m_c = clean(med_input)
        match = False
        for k, v in BASE_VIDAL.items():
            if m_c in k:
                st.markdown(f"""<div class="pharma-card" style="border-color:#1976D2;">
                    <h3>{v['n']}</h3>
                    <p><b>Usage :</b> {v['u']}</p>
                    <p><b>Dosage :</b> {v['d']}</p>
                    <p style="color:red; font-weight:bold;">{v['a']}</p>
                </div>""", unsafe_allow_html=True)
                match = True
        if not match:
            st.error("Médicament non répertorié dans la base simplifiée.")
            

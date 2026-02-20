import streamlit as st
import unicodedata

# --- CONFIGURATION ---
st.set_page_config(page_title="SanteCI 24/7", layout="wide", page_icon="🏥")

# --- STYLE CSS PERSONNALISÉ ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, label, span { color: #1A1A1A !important; }
    .stButton>button { width: 100%; border-radius: 25px; height: 55px; background-color: #00AB66; color: white; font-weight: bold; font-size: 18px; border: none; }
    .emergency-card { background-color: #D32F2F; color: white; padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 10px; font-weight: bold; border: 2px solid #b71c1c; }
    .pharma-card { background: #F0F2F6; padding: 15px; border-radius: 12px; border-left: 8px solid #00AB66; margin-bottom: 10px; color: black; }
    </style>
""", unsafe_allow_html=True)

def clean(text):
    if not text: return ""
    return "".join(c for c in unicodedata.normalize('NFD', text.lower()) if unicodedata.category(c) != 'Mn').strip()

# --- BASE DE DONNÉES INTERNE (Garantit des résultats) ---
# En attendant que le scraping soit rétabli, on met les pharmacies majeures par zone
GARDES_LOCALE = {
    "yopougon": ["Pharmacie du Bel Air (Palais) - 27 23 45 11 00", "Pharmacie Saint-André (Siporex) - 27 23 46 22 11"],
    "cocody": ["Pharmacie de la Riviera (Golf) - 27 22 43 00 99", "Pharmacie Saint-Jean - 27 22 44 11 22"],
    "abobo": ["Pharmacie de la Mairie - 27 24 39 00 11", "Pharmacie du Rail - 27 24 38 22 33"],
    "bouake": ["Pharmacie de la Paix - 27 31 63 00 44", "Pharmacie du Commerce - 27 31 64 55 66"]
}

BASE_VIDAL = {
    "litacold": {"n": "LITACOLD", "u": "Rhume et état grippal.", "d": "1 comp. 3 fois/jour.", "a": "⚠️ Risque de somnolence."},
    "paracetamol": {"n": "PARACÉTAMOL (Doliprane/Efferalgan)", "u": "Douleurs et fièvre.", "d": "1g max 4 fois/jour.", "a": "⚠️ Attention au foie."},
    "coartem": {"n": "COARTEM", "u": "Traitement du Paludisme.", "d": "Cure de 3 jours.", "a": "⚠️ Prendre avec un repas gras."}
}

# --- BARRE LATÉRALE : URGENCES ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/684/684101.png", width=100)
    st.markdown("### 🚨 NUMÉROS D'URGENCE")
    st.markdown('<div class="emergency-card">🚑 SAMU : 185</div>', unsafe_allow_html=True)
    st.markdown('<div class="emergency-card">🚒 POMPIERS : 180</div>', unsafe_allow_html=True)
    st.markdown('<div class="emergency-card">🚓 POLICE : 170 / 111</div>', unsafe_allow_html=True)
    st.info("Ces numéros sont gratuits depuis un mobile en Côte d'Ivoire.")

# --- CORPS PRINCIPAL ---
st.title("🏥 SanteCI Assistant v5.0")
tab1, tab2, tab3 = st.tabs(["💊 PHARMACIES", "🩺 IA DIAGNOSTIC", "📚 GUIDE VIDAL"])

with tab1:
    st.subheader("📍 Pharmacies de garde")
    zone = st.text_input("Tapez votre commune (ex: Yopougon, Cocody...)", key="z_input")
    if st.button("RECHERCHER MAINTENANT"):
        z_c = clean(zone)
        trouve = False
        for ville, listes in GARDES_LOCALE.items():
            if z_c in ville:
                st.success(f"Pharmacies de garde à {ville.capitalize()} :")
                for p in listes:
                    st.markdown(f'<div class="pharma-card">{p}</div>', unsafe_allow_html=True)
                trouve = True
        
        if not trouve:
            st.warning("⚠️ Base locale limitée. Pour une liste complète actualisée minute par minute, nous vous conseillons l'application officielle 'PharmaConsults'.")

with tab2:
    st.subheader("Analyseur Ada")
    mal = st.text_area("Expliquez votre mal...")
    if st.button("LANCER L'ANALYSE"):
        c = clean(mal)
        if "fievre" in c or "chaud" in c:
                        st.error("🦟 SUSPICION PALUDISME : Faites un test TDR et hydratez-vous.")
        elif "ventre" in c or "diarrhee" in c:
            st.warning("🤢 TROUBLE DIGESTIF : Préparez un SRO (1L eau + 6 sucres + 1 sel).")
        else:
            st.info("Symptômes enregistrés. Reposez-vous et surveillez votre température.")

with tab3:
    st.subheader("Guide Médicaments")
    med = st.text_input("Nom du médicament (ex: Litacold, Paracétamol...)")
    if st.button("VOIR LA NOTICE"):
        m_c = clean(med)
        match = False
        for k, v in BASE_VIDAL.items():
            if m_c in k:
                st.markdown(f'<div class="pharma-card" style="border-color:#1976D2;"><h3>{v["n"]}</h3><b>Usage :</b> {v["u"]}<br><b>Dose :</b> {v["d"]}<br><span style="color:red;">{v["a"]}</span></div>', unsafe_allow_html=True)
                match = True
        if not match: st.error("Médicament non répertorié.")

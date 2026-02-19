import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Configuration optimisée pour mobile
st.set_page_config(page_title="PharmaGarde CI", layout="centered")

st.markdown("""
    <style>
    .stTextInput>div>div>input { background-color: #f0f2f6; border-radius: 10px; }
    .stTextArea>div>div>textarea { background-color: #f0f2f6; border-radius: 10px; }
    div.stButton > button:first-child { background-color: #00AB66; color:white; border-radius:10px; }
    </style>
""", unsafe_allow_html=True)

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data(ttl=3600)
def load_all_data():
    # Lien direct RAW pour éviter les erreurs de lecture
    url = "https://raw.githubusercontent.com/dedjebonoua/pharma-garde-ci/main/annuaire_sante_ci.csv"
    try:
        data = pd.read_csv(url)
        return data
    except:
        return pd.DataFrame()

df = load_all_data()

st.title("🏥 PharmaGarde 2.0")

# --- MENU NAVIGATION SIMPLE ---
option = st.selectbox("Menu", ["🏠 Accueil & Gardes", "🤖 Assistant Symptômes", "📍 Annuaire Complet"])

if option == "🏠 Accueil & Gardes":
    st.subheader("Rechercher une pharmacie")
    search = st.text_input("Tapez votre quartier...", key="main_search")
    
    if not df.empty:
        # On filtre les pharmacies
        pharmacies = df[df['Type'] == 'Pharmacie']
        if search:
            pharmacies = pharmacies[pharmacies.apply(lambda r: search.lower() in str(r).lower(), axis=1)]
        
        for i, row in pharmacies.iterrows():
            with st.expander(f"💊 {row['Nom']}"):
                st.write(f"📍 {row['Quartier']}")
                st.write(f"📞 {row['Contact']}")
                st.link_button("🗺️ Itinéraire Maps", f"https://www.google.com/maps/search/?api=1&query={row['Latitude']},{row['Longitude']}")
    else:
        st.error("Données indisponibles. Vérifiez le fichier CSV sur GitHub.")

elif option == "🤖 Assistant Symptômes":
    st.subheader("Analyse d'urgence")
    # Utilisation d'un text_area avec une clé unique pour le mobile
    user_input = st.text_area("Décrivez votre problème ici...", key="ia_input")
    
    if st.button("Analyser mon état"):
        if user_input:
            text = user_input.lower()
            if any(m in text for m in ["sang", "poitrine", "respirer", "conscience", "paralyse"]):
                st.error("🚨 URGENCE VITALE : Appelez le 185 (SAMU) immédiatement !")
                st.link_button("📞 APPELER LE 185", "tel:185")
            elif any(m in text for m in ["fievre", "chaud", "vomir", "palu"]):
                st.warning("⚠️ URGENCE MODÉRÉE : Consultez une pharmacie ou clinique rapidement.")
            else:
                st.success("✅ CONSEIL : Reposez-vous et surveillez l'évolution.")
        else:
            st.warning("Veuillez écrire quelque chose avant d'analyser.")

elif option == "📍 Annuaire Complet":
    st.subheader("Hôpitaux et Centres")
    if not df.empty:
        st.dataframe(df, use_container_width=True)

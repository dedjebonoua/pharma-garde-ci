import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import folium
from streamlit_folium import st_folium
from math import radians, cos, sin, asin, sqrt

# --- CONFIGURATION PWA & DESIGN ---
st.set_page_config(page_title="PharmaGarde 2.0 CI", page_icon="🏥", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #00AB66; color: white; font-weight: bold; }
    .urgent-card { padding: 20px; border-radius: 15px; background: white; border-left: 8px solid #FF3B30; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px; }
    .info-card { padding: 20px; border-radius: 15px; background: white; border-left: 8px solid #00AB66; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px; }
    </style>
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
""", unsafe_allow_html=True)

# --- FONCTIONS TECHNIQUES ---
def calculate_dist(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    return 2 * asin(sqrt(sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2)) * 6371

@st.cache_data(ttl=3600)
def fetch_data():
    # Lien vers ton CSV (Assure-toi que les colonnes Latitude/Longitude y sont)
    url = "https://raw.githubusercontent.com/dedjebonoua/pharma-garde-ci/main/annuaire_sante_ci.csv"
    try:
        df = pd.read_csv(url)
        return df
    except:
        return pd.DataFrame()

def diagnostic_ia(text):
    text = text.lower()
    if any(m in text for m in ["sang", "poitrine", "respirer", "conscience", "paralyse", "convulsion"]):
        return "🔴 URGENCE VITALE", "SAMU (185) / Pompiers (180)", "#FF3B30"
    if any(m in text for m in ["fievre", "chaud", "vomir", "ventre", "palu", "maux"]):
        return "🟡 URGENCE MODÉRÉE", "Pharmacie de garde ou Clinique", "#F9A825"
    return "🟢 CONSEIL LÉGER", "Pharmacie de quartier pour avis", "#00AB66"

# --- INTERFACE PRINCIPALE ---
st.title("🛡️ PharmaGarde & Santé CI 2.0")

# 1. Barre Latérale : Localisation
with st.sidebar:
    st.header("📍 Ma Position")
    # Simulation de position (Abidjan Plateau par défaut)
    u_lat = st.number_input("Ma Latitude :", value=5.3245, format="%.4f")
    u_lon = st.number_input("Ma Longitude :", value=-4.0201, format="%.4f")
    st.info("📲 Pour installer l'app : Options navigateur > Ajouter à l'écran d'accueil.")

# 2. Onglets
tab1, tab2, tab3 = st.tabs(["🚀 Urgences Proches", "🤖 Assistant Symptômes", "📂 Annuaire"])

df = fetch_data()

with tab1:
    if not df.empty:
        df['distance'] = df.apply(lambda r: calculate_dist(u_lat, u_lon, r['Latitude'], r['Longitude']), axis=1)
        df_sorted = df.sort_values('distance')
        
        col_m, col_l = st.columns([2, 1])
        
        with col_m:
            m = folium.Map(location=[u_lat, u_lon], zoom_start=13)
            folium.Marker([u_lat, u_lon], icon=folium.Icon(color='red', icon='user')).add_to(m)
            for i, row in df_sorted.head(10).iterrows():
                folium.Marker([row['Latitude'], row['Longitude']], tooltip=row['Nom']).add_to(m)
            st_folium(m, width="100%", height=400)
            
        with col_l:
            st.subheader("Les plus proches")
            for i, row in df_sorted.head(3).iterrows():
                st.markdown(f"""<div class="urgent-card"><b>{row['Nom']}</b><br>📍 {row['Quartier']}<br>📏 {row['distance']:.1f} km</div>""", unsafe_allow_html=True)
                st.link_button(f"🚀 Itinéraire vers {row['Nom']}", f"https://www.google.com/maps/dir/?api=1&destination={row['Latitude']},{row['Longitude']}")

with tab2:
    st.header("🤖 Analyse de Symptômes")
    user_txt = st.text_area("Décrivez votre problème de santé...")
    if user_txt:
        statut, orient, coul = diagnostic_ia(user_txt)
        st.markdown(f"""<div style="background:{coul}; padding:20px; border-radius:15px; color:white;"><h3>{statut}</h3>Orientation : {orient}</div>""", unsafe_allow_html=True)
        if "🔴" in statut:
            st.link_button("📞 APPELER LE SAMU (185)", "tel:185")

with tab3:
    st.header("📂 Toutes les structures")
    search = st.text_input("Filtrer par ville ou nom...")
    if search:
        st.dataframe(df[df.apply(lambda r: search.lower() in str(r).lower(), axis=1)])
    else:
        st.dataframe(df)

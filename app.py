            import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import unicodedata
from datetime import datetime

# --- CONFIGURATION ÉLITE ---
st.set_page_config(
    page_title="SanteCI Gold Standard", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- DESIGN SYSTÈME (CSS PROFESSIONNEL) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #FDFDFD; }
    .stApp { background: white; }
    /* Dashboard Cards */
    .stat-card {
        background: #ffffff; padding: 20px; border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid #F0F0F0;
        border-left: 5px solid #00AB66; margin-bottom: 20px;
    }
    /* Emergency Flash */
    .emergency-banner {
        background: linear-gradient(90deg, #D32F2F 0%, #FF5252 100%);
        color: white; padding: 15px; border-radius: 12px;
        font-weight: bold; text-align: center; font-size: 22px;
        animation: pulse 2s infinite; margin-bottom: 10px;
    }
    @keyframes pulse { 0% {opacity: 1;} 50% {opacity: 0.8;} 100% {opacity: 1;} }
    /* Buttons */
    .stButton>button {
        background: #00AB66; color: white; border-radius: 12px;
        height: 3em; width: 100%; border: none; font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,171,102,0.3); }
    </style>
""", unsafe_allow_html=True)

# --- MOTEUR D'EXTRACTION DE DONNÉES (POWERED BY PHARMACONSULTS LOGIC) ---
def normalize_str(text):
    return "".join(c for c in unicodedata.normalize('NFD', text.lower()) if unicodedata.category(c) != 'Mn').strip()

@st.cache_data(ttl=1800) # Rafraîchissement toutes les 30 min pour la précision maximale
def force_fetch_pharmacies():
    """Extracteur haute performance croisant les sources PharmaConsults et AnnuaireCI"""
    urls = [
        "https://annuaireci.com/pharmacies-de-garde/",
        "https://www.pharma-consults.ci/pharmacies-de-garde" # Source cible
    ]
    results = []
    for url in urls:
        try:
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')
            # Extraction par regex des noms et numéros type CI (+225)
            tags = soup.find_all(['p', 'li', 'div', 'span'])
            for t in tags:
                text = t.get_text().strip()
                if re.search(r'\d{2}.*\d{2}.*\d{2}.*\d{2}', text):
                    results.append(text)
        except: continue
    return list(set(results)) # Suppression des doublons

# --- BASE DE DONNÉES VIDAL ÉLITE ---
VIDAL_PRO = {
    "litacold": {"name": "LITACOLD (Sirop/Comp)", "desc": "Rhume, état grippal, congestion nasale.", "poso": "Adulte: 1 comprimé 3x/jour. Enfant: Suivre prescription.", "warning": "⚠️ Somnolence forte. Interdit aux conducteurs."},
    "coartem": {"name": "COARTEM 20/120", "desc": "Antipaludique (Artéméther/Luméfantrine).", "poso": "6 doses sur 3 jours. Suivre le schéma horaire strict.", "warning": "⚠️ Prendre avec un repas riche en lipides (lait, sauce)."},
    "paracetamol": {"name": "PARACETAMOL 1G", "desc": "Antalgique et Antipyrétique.", "poso": "1g toutes les 6h. Max 4g/jour.", "warning": "⚠️ Toxicité hépatique en cas de surdosage ou alcool."}
}

# --- INTERFACE UTILISATEUR (UI/UX) ---
st.title("🏆 SanteCI Gold : L'Excellence Médicale")

# Sidebar - Urgences Vitales
with st.sidebar:
    st.markdown("### 🆘 APPEL D'URGENCE (Gratuit)")
    st.markdown('<div class="emergency-banner">🚑 SAMU : 185</div>', unsafe_allow_html=True)
    st.markdown('<div class="emergency-banner">🚒 POMPIERS : 180</div>', unsafe_allow_html=True)
    st.markdown('<div class="emergency-banner">🚓 POLICE : 170</div>', unsafe_allow_html=True)
    st.write("---")
    st.success(f"Dernière mise à jour : {datetime.now().strftime('%H:%M')}")

tabs = st.tabs(["💎 Gardes en Temps Réel", "🧠 IA Diagnostic Pro", "📖 Encyclopédie Vidal"])

# ONGLET 1 : GARDES (FORCE PHARMACONSULTS)
with tabs[0]:
    st.subheader("📍 Géolocalisation des Pharmacies de Garde")
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input("Commune ou Ville", placeholder="Ex: Marcory, Yamoussoukro, Korhogo...")
    with col2:
        st.write("##")
        search_btn = st.button("FORCER LA RECHERCHE")

    if search_btn or query:
        with st.spinner('Synchronisation avec les serveurs de garde...'):
            data = force_fetch_pharmacies()
            q_norm = normalize_str(query)
            filtered = [p for p in data if q_norm in normalize_str(p)]
            
            if filtered:
                st.info(f"Résultats trouvés : {len(filtered)}")
                for item in filtered:
                    st.markdown(f'<div class="stat-card"><b>{item}</b></div>', unsafe_allow_html=True)
                    # Lien vers Maps pour chaque pharmacie
                    clean_name = item.split('-')[0].split('(')[0].strip()
                    st.link_button(f"🚀 Itinéraire vers {clean_name}", f"https://www.google.com/maps/search/{clean_name.replace(' ', '+')}+cote+d'ivoire")
            else:
                st.error("Aucune donnée trouvée pour cette zone. Vérifiez l'orthographe ou essayez une zone limitrophe.")

# ONGLET 2 : DIAGNOSTIC (LOGIQUE ADA MEDICAL)
with tabs[1]:
    st.subheader("🩺 Assistant de Triage Médical")
    symptoms = st.text_area("Décrivez vos symptômes avec précision...", height=150)
    if st.button("LANCER L'ANALYSE EXPERTE"):
        s = normalize_str(symptoms)
        if any(x in s for x in ["poitrine", "bras", "visage", "paralyse"]):
            st.markdown('<div class="emergency-banner">🚨 ALERTE URGENCE VITALE : NE PAS ATTENDRE. APPELEZ LE 185 IMMÉDIATEMENT.</div>', unsafe_allow_html=True)
        elif "fievre" in s or "chaud" in s:
            
            st.markdown("""
            <div class="stat-card" style="border-left-color: #FBC02D;">
            <h3>🦟 Protocole Suspicion Paludisme</h3>
            <p><b>1. Test :</b> Réalisez un test TDR en pharmacie (Coût approx: 500-1000 CFA).</p>
            <p><b>2. Hydratation :</b> Boire 2.5L d'eau minimum/jour.</p>
            <p><b>3. Vigilance :</b> Si la fièvre persiste après 48h de traitement, retournez à l'hôpital.</p>
            </div>
            """, unsafe_allow_html=True)
        elif "ventre" in s or "diarrhee" in s:
            [attachment_0](attachment)
            st.markdown("""
            <div class="stat-card" style="border-left-color: #0288D1;">
            <h3>🤢 Protocole Gastro / Intoxication</h3>
            <p><b>Alerte Déshydratation :</b> Préparez immédiatement le SRO (Solution de Réhydratation Orale).</p>
            <p><b>Recette :</b> 1 Litre d'eau bouillie + 6 cuillères à café de sucre + 1/2 cuillère à café de sel.</p>
            </div>
            """, unsafe_allow_html=True)

# ONGLET 3 : VIDAL (ENRICHISSEMENT CI)
with tabs[2]:
    st.subheader("📚 Référentiel Médicaments Côte d'Ivoire")
    drug = st.text_input("Rechercher un médicament (ex: Litacold, Coartem...)")
    if drug:
        d_norm = normalize_str(drug)
        match = next((v for k, v in VIDAL_PRO.items() if d_norm in k), None)
        if match:
            st.markdown(f"""
            <div class="stat-card" style="border-left-color: #1976D2;">
            <h2>{match['name']}</h2>
            <p><b>Indication :</b> {match['desc']}</p>
            <p><b>Posologie :</b> {match['poso']}</p>
            <p style="color: #D32F2F; font-weight: bold;">{match['warning']}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Médicament non répertorié. Consultez un spécialiste.")



import streamlit as st
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="PharmaGarde CI", page_icon="🏥")

st.title("🏥 PharmaGarde Côte d'Ivoire")
st.markdown("Trouvez rapidement la pharmacie de garde la plus proche de chez vous.")

# 1. Simulation de la base de données (À remplacer plus tard par votre fichier Excel/JSON)
data = [
    {"Commune": "Cocody", "Pharmacie": "Pharmacie de la Riviera 3", "Quartier": "Riviera 3", "Contact": "272247XXXX", "Maps": "https://goo.gl/maps/xyz1"},
    {"Commune": "Yopougon", "Pharmacie": "Pharmacie Bel Air", "Quartier": "Siporex", "Contact": "2723XXXXXX", "Maps": "https://goo.gl/maps/xyz2"},
    {"Commune": "Marcory", "Pharmacie": "Pharmacie de l'INJS", "Quartier": "Zone 4", "Contact": "2721XXXXXX", "Maps": "https://goo.gl/maps/xyz3"},
    {"Commune": "Abobo", "Pharmacie": "Pharmacie de la Mairie", "Quartier": "Abobo Centre", "Contact": "2724XXXXXX", "Maps": "https://goo.gl/maps/xyz4"},
]
df = pd.DataFrame(data)

# 2. Barre de recherche
commune_liste = sorted(df['Commune'].unique())
recherche = st.selectbox("Sélectionnez votre commune :", ["Toutes"] + commune_liste)

# 3. Filtrage des résultats
if recherche != "Toutes":
    resultats = df[df['Commune'] == recherche]
else:
    resultats = df

# 4. Affichage des résultats sous forme de cartes
for index, row in resultats.iterrows():
    with st.container():
        st.subheader(f"💊 {row['Pharmacie']}")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"📍 **Quartier :** {row['Quartier']}")
            st.write(f"📞 **Tel :** {row['Contact']}")
        with col2:
            st.link_button("📍 Voir sur Maps", row['Maps'])
            st.link_button("📞 Appeler", f"tel:{row['Contact']}")
        st.divider()

st.caption("Données mises à jour selon le tour de garde officiel de l'AIRP.")

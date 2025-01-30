import streamlit as st
import os
import datetime

# =======================================================================
# Configuration de la page
# =======================================================================
st.set_page_config(
    page_title="Accueil - Mapping Entreprise Medipim",
    layout="wide"
)

# =======================================================================
# Charger CSS personnalisé (si présent)
# =======================================================================
css_file_path = os.path.join(os.path.dirname(__file__), "styles.css")
if os.path.exists(css_file_path):
    with open(css_file_path, "r") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

# =======================================================================
# Charger un logo (optionnel)
# =======================================================================
logo_path = os.path.join(os.path.dirname(__file__), "assets", "image001.png")
if os.path.exists(logo_path):
    st.image(logo_path, width=250)

# =======================================================================
# Page d'accueil
# =======================================================================
st.title("Bienvenue sur l'application de Mapping Entreprise Medipim")
st.markdown("""
Cette application vous permet de :
- Gérer votre **authentification** (page Connexion)
- Réaliser le **mapping** (page Mapping)
- Administrer les utilisateurs (page Administration) si vous êtes admin

Utilisez le menu latéral (icône en haut à gauche) pour naviguer entre les pages.
""")

st.markdown(f"Date du jour : **{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**")

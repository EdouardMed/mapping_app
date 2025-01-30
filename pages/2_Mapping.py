import streamlit as st
import pandas as pd
import datetime
from firebase_admin import firestore
from firebase_config import init_firebase


db = init_firebase()  # Récupère un firestore.client() initialisé
# -----------------------------------------------------------------------
# Vérification de la session
# -----------------------------------------------------------------------
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("Vous devez être connecté pour accéder à cette page.")
    st.stop()

# -----------------------------------------------------------------------
# Fonctions utilitaires
# -----------------------------------------------------------------------
@st.cache_data
def load_csv(file):
    return pd.read_csv(file)

def log_action(user_email, action_description):
    """
    Exemple de fonction pour logguer une action dans Firestore.
    """
    db.collection("logs").add({
        "user_email": user_email,
        "action": action_description,
        "timestamp": datetime.datetime.now()
    })

# -----------------------------------------------------------------------
# Interface
# -----------------------------------------------------------------------
st.title("Page de Mapping")
st.write(f"Connecté en tant que : {st.session_state['username']} (rôle : {st.session_state['role']})")

st.markdown("""
**Instructions**:
1. Téléversez le fichier **LABOS.csv**.
2. Téléversez le fichier **PRODUITS.csv**.
3. Le mapping s'effectue automatiquement après l'upload des deux fichiers.
4. Téléchargez le fichier final.
""")

col1, col2 = st.columns(2)

with col1:
    labos_file = st.file_uploader("Téléversez le fichier LABOS.csv ici", type="csv")
    if labos_file is not None:
        st.write("Aperçu de LABOS.csv :")
        try:
            labos_df = load_csv(labos_file)
            st.dataframe(labos_df.head(5))
        except Exception as e:
            st.error(f"Erreur lors de la lecture de LABOS.csv : {e}")

with col2:
    produits_file = st.file_uploader("Téléversez le fichier PRODUITS.csv ici", type="csv")
    if produits_file is not None:
        st.write("Aperçu de PRODUITS.csv :")
        try:
            produits_df = load_csv(produits_file)
            st.dataframe(produits_df.head(5))
        except Exception as e:
            st.error(f"Erreur lors de la lecture de PRODUITS.csv : {e}")

# Traitement
required_labos_cols = {"ID", "Nom", "Enterprises"}
required_produits_cols = {"ID", "Labos", "Entreprises"}

if labos_file and produits_file:
    with st.spinner("Traitement en cours..."):
        try:
            labos_df = load_csv(labos_file)
            produits_df = load_csv(produits_file)

            # Nettoyage des noms de colonnes
            labos_df.columns = labos_df.columns.str.strip()
            produits_df.columns = produits_df.columns.str.strip()

            # Vérifie la présence des colonnes obligatoires
            if not required_labos_cols.issubset(labos_df.columns):
                st.error(f"Le fichier LABOS.csv doit contenir au minimum les colonnes : {required_labos_cols}")
                st.stop()

            if not required_produits_cols.issubset(produits_df.columns):
                st.error(f"Le fichier PRODUITS.csv doit contenir au minimum les colonnes : {required_produits_cols}")
                st.stop()

            # Mapping
            mapping = produits_df.merge(
                labos_df,
                left_on="Labos",
                right_on="ID",
                how="left",
                suffixes=("_produit", "_labo")
            )
            mapping = mapping.rename(columns={
                "Nom": "Nom Laboratoire",
                "Enterprises": "Entreprise ID"
            })
            mapping = mapping.fillna("Non assignée")

            st.success("Mapping réussi !")
            st.dataframe(mapping.head(10))

            # Génération du CSV final
            csv_final = mapping.to_csv(index=False).encode("utf-8")

            # Nom du fichier avec timestamp pour éviter l'écrasement
            now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"produits_completes_{now_str}.csv"

            st.download_button(
                label="Télécharger le fichier complété",
                data=csv_final,
                file_name=file_name,
                mime="text/csv"
            )

            # Logguer l'action
            log_action(st.session_state["email"], "Mapping effectué et fichier téléchargé")
        except Exception as e:
            st.error(f"Erreur lors du traitement des fichiers : {e}")
else:
    st.info("Veuillez téléverser les deux fichiers pour commencer.")

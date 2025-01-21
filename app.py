import streamlit as st
import pandas as pd
import bcrypt
import os
import datetime

# Add the company logo
st.set_page_config(layout="wide", page_title="Mapping Produits-Labo-Entreprise")
logo_path = os.path.join(os.path.dirname(__file__), "image001.png")
if os.path.exists(logo_path):
    st.image(logo_path, width=250)
else:
    st.warning("Logo introuvable. Assurez-vous que le fichier 'image001.png' est dans le même dossier que l'application.")

# Authentication
@st.cache_data
def load_users():
    users_path = os.path.join(os.path.dirname(__file__), "users.csv")
    if os.path.exists(users_path):
        return pd.read_csv(users_path)
    else:
        return pd.DataFrame(columns=["username", "password", "role"])

users = load_users()

def authenticate(username, password):
    if username in users["username"].values:
        user_data = users[users["username"] == username].iloc[0]
        if bcrypt.checkpw(password.encode(), user_data["password"].encode()):
            return True, user_data["role"]
    return False, None

st.title("Application sécurisée - Connexion")
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["role"] = None

if not st.session_state["authenticated"]:
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        authenticated, role = authenticate(username, password)
        if authenticated:
            st.session_state["authenticated"] = True
            st.session_state["role"] = role
            st.success(f"Bienvenue, {username} ! Rôle : {role}")
        else:
            st.error("Nom d'utilisateur ou mot de passe incorrect.")
else:
    role = st.session_state["role"]
    st.sidebar.button("Se déconnecter", on_click=lambda: st.session_state.update({"authenticated": False, "role": None}))

    # Check role
    if role == "admin":
        st.sidebar.write("Vous êtes connecté en tant qu'administrateur.")
    elif role == "user":
        st.sidebar.write("Vous êtes connecté en tant qu'utilisateur.")
    else:
        st.error("Rôle inconnu.")

    # Application logic for authenticated users
    st.title("Mapping produit avec entreprises manquantes.")

    # Instructions moved to a collapsible section
    with st.expander("**INSTRUCTIONS A LIRE AVANT UTILISATION**", expanded=True):
        st.markdown(
            """
            <div style="font-size:20px; line-height:2;">
            Cette application de mapping va vous permettre d'ajouter une entreprise (fournisseur) sur les fiches produits.

            Avant de procéder au mapping, assurez-vous d'avoir ces 2 fichiers en votre possession : 

            - **Un fichier produit** (sans entreprises) qui contient 3 colonnes : `ID`, `LABOS`, `ENTREPRISES` (colonne vierge).

            - **Un fichier labo** qui contient 3 colonnes : `ID`, `NOM`, `ENTREPRISES`.

            Une fois ces fichiers en votre possession, vous pouvez les téléverser dans l'interface. 
            Assurez-vous de fournir le bon fichier dans la zone de téléversement (Drag and Drop). 
            Il y a une zone pour le fichier `labos` et une zone pour le fichier `produits`.

            Une fois les fichiers ajoutés, le mapping se fait instantanément. 

            Et pour finir, vous pouvez exporter votre fichier avec les données complètes afin de procéder à une importation sur MEDIPIM.
            </div>
            """,
            unsafe_allow_html=True
        )

    # File uploader section
    st.header("Chargement des fichiers")
    col1, col2 = st.columns(2)

    with col1:
        labos_file = st.file_uploader("Glissez et déposez le fichier LABOS.csv ici", type="csv", label_visibility="visible")

    with col2:
        produits_file = st.file_uploader("Glissez et déposez le fichier PRODUITS.csv ici", type="csv", label_visibility="visible")

    # Change the language of the drag-and-drop zone to French
    st.markdown(
        """
        <style>
        div[data-testid="stFileUploadDropzone"] div div {
            font-family: Arial, sans-serif;
            font-size: 20px;
            color: #FFF;
            text-align: center;
        }
        div[data-testid="stFileUploadDropzone"] div div::before {
            content: "Déposez votre fichier ici";
        }

        footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            text-align: center;
            padding: 10px 0;
            font-size: 16px;
            background-color: #1e1e1e;
            color: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if labos_file and produits_file:
        try:
            # Load the uploaded files
            labos_df = pd.read_csv(labos_file, sep=None, engine="python")
            produits_df = pd.read_csv(produits_file, sep=None, engine="python")

            # Ensure column names are standardized
            labos_df.columns = labos_df.columns.str.strip()
            produits_df.columns = produits_df.columns.str.strip()

            # Validate required columns
            required_labos_columns = {"ID", "Nom", "Enterprises"}
            required_produits_columns = {"ID", "Labos", "Entreprises"}

            if not required_labos_columns.issubset(labos_df.columns):
                st.error(f"Le fichier LABOS.csv doit contenir les colonnes suivantes : {', '.join(required_labos_columns)}")
            elif not required_produits_columns.issubset(produits_df.columns):
                st.error(f"Le fichier PRODUITS.csv doit contenir les colonnes suivantes : {', '.join(required_produits_columns)}")
            else:
                # Display datasets side by side
                st.header("Données des fichiers")
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Laboratoires")
                    st.dataframe(labos_df, height=450)

                with col2:
                    st.subheader("Produits")
                    st.dataframe(produits_df, height=450)

                # Merge datasets to map entreprises to produits via laboratoires
                st.header("Mapping produit avec entreprises manquantes.")
                try:
                    # Check and standardize column types
                    labos_df["ID"] = labos_df["ID"].astype(str)
                    labos_df["Enterprises"] = labos_df["Enterprises"].astype(str)
                    produits_df["Labos"] = produits_df["Labos"].astype(str)

                    # Perform mapping
                    mapping = produits_df.merge(labos_df, left_on="Labos", right_on="ID", how="left")

                    # Rename columns for clarity and drop unnecessary ones
                    mapping = mapping.rename(columns={
                        "Nom": "Nom Laboratoire",
                        "Enterprises": "Entreprise ID"
                    }).drop(columns=["ID_y"], errors="ignore")

                    # Fill missing values for clarity
                    mapping["Entreprise ID"] = mapping["Entreprise ID"].replace({pd.NA: "Non assignée", None: "Non assignée", "nan": "Non assignée"})

                    st.dataframe(mapping, height=450)

                    # Export mapped data
                    st.markdown("### Exporter le fichier complété")

                    @st.cache_data
                    def convert_df(df):
                        return df.to_csv(index=False).encode('utf-8')

                    csv = convert_df(mapping)

                    st.download_button(
                        label="Télécharger le fichier CSV",
                        data=csv,
                        file_name="produits_completes.csv",
                        mime="text/csv",
                    )

                    st.markdown(
                        """
                        **Mapping terminé :**
                        - Les produits sont maintenant associés à leurs laboratoires et entreprises correspondants.
                        - Vous pouvez télécharger le fichier complété.
                        """
                    )
                except Exception as mapping_error:
                    st.error(f"Une erreur est survenue lors du mapping : {mapping_error}")

        except Exception as e:
            st.error(f"Une erreur est survenue lors du traitement des fichiers : {e}")
    else:
        st.info("Veuillez téléverser les fichiers LABOS.csv et PRODUITS.csv pour commencer.")

# Footer
st.markdown(f"""
<footer>
© {datetime.datetime.now().year} Edouard GEORG - MEDIPIM. Tous droits réservés.
</footer>
""", unsafe_allow_html=True)

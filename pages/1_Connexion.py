import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
import bcrypt
from firebase_config import init_firebase


db = init_firebase()  # Récupère un firestore.client() initialisé


# -----------------------------------------------------------------------
# Initialisation de Firebase
# -----------------------------------------------------------------------
# On utilise un pattern "if not firebase_admin._apps" pour éviter
# qu'il ne s'initialise plusieurs fois (erreur sinon).
if not firebase_admin._apps:
    try:
        firebase_info = st.secrets["firebase"]
        cred = credentials.Certificate({
            "type": firebase_info["type"],
            "project_id": firebase_info["project_id"],
            "private_key_id": firebase_info["private_key_id"],
            "private_key": firebase_info["private_key"],
            "client_email": firebase_info["client_email"],
            "client_id": firebase_info["client_id"],
            "auth_uri": firebase_info["auth_uri"],
            "token_uri": firebase_info["token_uri"],
            "auth_provider_x509_cert_url": firebase_info["auth_provider_x509_cert_url"],
            "client_x509_cert_url": firebase_info["client_x509_cert_url"],
        })
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erreur lors de l'initialisation de Firebase : {e}")
        st.stop()

db = firestore.client()

# -----------------------------------------------------------------------
# Fonctions utilitaires
# -----------------------------------------------------------------------
def authenticate_user(email, password):
    """
    Vérifie les informations d'identification de l'utilisateur via Firebase/Firestore.
    Retourne (True, role, username) si OK, sinon (False, None, None).
    """
    try:
        user_record = auth.get_user_by_email(email)
        doc = db.collection('users').document(user_record.uid).get()
        if doc.exists:
            user_data = doc.to_dict()
            if bcrypt.checkpw(password.encode(), user_data['password'].encode()):
                return True, user_data.get('role', 'user'), user_data.get('username', email)
    except Exception as e:
        st.error(f"Erreur lors de l'authentification : {e}")
    return False, None, None

def save_session(authenticated, email, role, username):
    st.session_state["authenticated"] = authenticated
    st.session_state["email"] = email
    st.session_state["role"] = role
    st.session_state["username"] = username

def load_session():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["email"] = None
        st.session_state["role"] = None
        st.session_state["username"] = None

# -----------------------------------------------------------------------
# Exécution
# -----------------------------------------------------------------------
st.title("Page de Connexion")

# Initialiser l'état de session
load_session()

# Si utilisateur déjà connecté, afficher un message
if st.session_state["authenticated"]:
    st.success(f"Vous êtes déjà connecté en tant que {st.session_state['username']} (rôle: {st.session_state['role']}).")
    st.info("Allez dans la page 'Mapping' ou 'Administration' si nécessaire.")
else:
    # Formulaire de connexion
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        authenticated, role, username = authenticate_user(email, password)
        if authenticated:
            save_session(True, email, role, username)
            st.query_params["auth"] = "true"
            st.success("Connexion réussie. Rendez-vous sur la page 'Mapping' ou 'Administration'.")
        else:
            st.error("Email ou mot de passe incorrect.")

# Bouton de déconnexion (si nécessaire)
if st.session_state["authenticated"]:
    if st.button("Se déconnecter"):
        save_session(False, None, None, None)
        st.query_params["auth"] = "false"
        st.success("Déconnexion réussie.")

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

def init_firebase():
    """
    Initialise l'application Firebase si ce n'est pas déjà fait.
    Retourne un client Firestore.
    """
    if not firebase_admin._apps:
        # Récupérer les secrets
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
    return firestore.client()

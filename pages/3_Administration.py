import streamlit as st
from firebase_admin import auth, firestore
import bcrypt

db = firestore.client()

def load_users():
    # Récupère tous les documents de la collection 'users'
    return db.collection("users").get()

def update_user_role(uid, new_role):
    db.collection("users").document(uid).update({"role": new_role})

def reset_user_password(uid, new_password):
    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    db.collection("users").document(uid).update({"password": hashed})

st.title("Administration des utilisateurs")

# Vérification de la session et rôle
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("Vous devez être connecté pour accéder à cette page.")
    st.stop()

if st.session_state["role"] != "admin":
    st.error("Accès refusé : vous n'avez pas le rôle administrateur.")
    st.stop()

# Afficher la liste des utilisateurs
st.write("Liste des utilisateurs :")
users_docs = load_users()
for doc in users_docs:
    user_data = doc.to_dict()
    user_uid = doc.id
    user_email = user_data.get("email", "")
    user_role = user_data.get("role", "user")
    username = user_data.get("username", "")

    st.write(f"**UID**: {user_uid}")
    st.write(f"**Email**: {user_email}")
    st.write(f"**Username**: {username}")
    st.write(f"**Rôle actuel**: {user_role}")

    # Formulaire pour changer le rôle
    new_role = st.selectbox("Nouveau rôle", ["user", "admin"], key=f"role_{user_uid}")
    if st.button(f"Changer le rôle de {user_email}", key=f"btn_role_{user_uid}"):
        update_user_role(user_uid, new_role)
        st.success(f"Rôle mis à jour pour {user_email} en {new_role}.")

    # Formulaire pour réinitialiser le mot de passe
    new_password = st.text_input("Nouveau mot de passe", type="password", key=f"pwd_{user_uid}")
    if st.button(f"Réinitialiser le mot de passe de {user_email}", key=f"btn_pwd_{user_uid}"):
        if new_password:
            reset_user_password(user_uid, new_password)
            st.success(f"Mot de passe réinitialisé pour {user_email}.")
        else:
            st.error("Vous devez saisir un nouveau mot de passe.")

    st.write("---")

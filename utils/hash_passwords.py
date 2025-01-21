import bcrypt

# Liste des mots de passe à hacher
passwords = ["password123", "userpassword"]

# Génération des mots de passe hachés
hashed_passwords = [bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode() for password in passwords]

# Affichage des mots de passe hachés
for password, hashed in zip(passwords, hashed_passwords):
    print(f"{password} -> {hashed}")

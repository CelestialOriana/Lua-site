# models/user.py
try:
    from flask_login import UserMixin  # type: ignore
except ImportError:
    # Fallback si flask_login n'est pas disponible pour Pylance
    class UserMixin:
        def is_authenticated(self):
            return True
        def is_active(self):
            return True
        def is_anonymous(self):
            return False
        def get_id(self):
            return str(self.id)

# Définition de la classe User
class User(UserMixin):
    def __init__(self, id, username, email, password, role='user', name=None):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.role = role  # 'user', 'admin', etc.
        self.name = name or username
        
    def is_admin(self):
        return self.role == 'admin'
    
    def get_id(self):
        return str(self.id)

# Simulation d'une base de données d'utilisateurs (à remplacer par une vraie base de données)
users_db = {
    1: User(1, 'admin', 'admin@example.com', '$2b$12$dXfAVDN3v5xSZ/gPvYP9SOPoZ9WeZ3RA49l7/rKCmYazGYmraDfEa', 'admin', 'Administrateur'),  # Mot de passe: admin123
    2: User(2, 'user1', 'user1@example.com', '$2b$12$kxHR1hMJk.MfOlI8J5hN6emNzQT.z9iCg2GJcn0YezGEzU6.fyfUe', 'user', 'Utilisateur 1'),  # Mot de passe: user123
    3: User(3, 'user2', 'user2@example.com', '$2b$12$kxHR1hMJk.MfOlI8J5hN6emNzQT.z9iCg2GJcn0YezGEzU6.fyfUe', 'user', 'Utilisateur 2'),  # Mot de passe: user123
}

# Fonctions d'accès aux utilisateurs
def get_user_by_id(user_id):
    try:
        return users_db.get(int(user_id))
    except (ValueError, TypeError):
        return None

def get_user_by_username(username):
    for user in users_db.values():
        if user.username == username:
            return user
    return None

def get_user_by_email(email):
    for user in users_db.values():
        if user.email == email:
            return user
    return None

def add_user(username, email, password, role='user', name=None):
    # Trouver le prochain ID disponible
    next_id = max(users_db.keys()) + 1 if users_db else 1
   
    # Créer le nouvel utilisateur
    new_user = User(next_id, username, email, password, role, name)
   
    # Ajouter à notre "base de données"
    users_db[next_id] = new_user
   
    return new_user

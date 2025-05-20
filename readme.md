# Système de Gestion de Matériel (SGM) - Région Réunion

Une application moderne pour gérer l'inventaire et le suivi du matériel informatique, développée avec Flask et Lua.

![Badge Version](https://img.shields.io/badge/version-1.0.0-blue)
![Badge Python](https://img.shields.io/badge/Python-3.7%2B-yellow)
![Badge Flask](https://img.shields.io/badge/Flask-3.0.0-green)
![Badge Lua](https://img.shields.io/badge/Lua-5.3-red)

## 📋 Fonctionnalités

- **Tableau de bord interactif** : Vue d'ensemble claire de votre inventaire de matériel
- **Gestion des stocks** : Suivez toutes vos ressources matérielles en temps réel
- **Filtrage par type** : Affichez uniquement les ordinateurs de bureau ou portables selon vos besoins
- **Alertes de stock bas** : Identification visuelle des matériels en quantité limitée
- **Système de rapports** : Générez des rapports détaillés sur l'utilisation et l'état du stock
- **Notifications** : Système complet pour informer les utilisateurs des événements importants
- **API REST** : Interface programmable pour intégrer avec d'autres services
- **Interface responsive** : Adapté à tous les appareils

## 🛠️ Guide d'installation

### Prérequis

- Python 3.7 ou supérieur
- Pip (gestionnaire de paquets Python)
- Navigateur web moderne

### Étape 1 : Cloner le projet

```bash
# Clonez le dépôt Git
git clone https://github.com/votre-utilisateur/systeme-gestion-materiel.git
cd systeme-gestion-materiel

# OU téléchargez et extrayez l'archive du projet
```

### Étape 2 : Installation des dépendances

```bash
# Installation en utilisant le fichier requirements.txt
pip install -r requirements.txt
```

Les modules principaux nécessaires sont :
- Flask 3.0.0 : Framework web léger
- python-dotenv 1.0.0 : Gestion des variables d'environnement
- lupa 2.0 : Intégration de Lua dans Python
- flask-login 0.6.3 : Gestion de l'authentification
- flask-bcrypt 1.0.1 : Hachage sécurisé des mots de passe

### Étape 3 : Configuration

1. Créez un fichier `.env` à la racine du projet avec le contenu suivant :

```
SECRET_KEY=votre_cle_secrete_a_changer_en_production
FLASK_ENV=development
PORT=5000
```

2. Personnalisez la configuration dans `config.py` si nécessaire

### Étape 4 : Lancement de l'application

```bash
# Lancement du serveur de développement
python app.py
```

L'application est accessible à l'adresse : [http://localhost:5000](http://localhost:5000)

## 🖥️ Guide d'utilisation

### Authentification

- **Connexion** : Utilisez les identifiants par défaut (admin/admin123 ou user1/user123)
- **Inscription** : Créez un nouveau compte utilisateur

### Tableau de bord

Le tableau de bord offre une vue d'ensemble de l'inventaire avec :
- Statistiques générales (total des matériels, disponibles, types)
- Liste des matériels avec filtrage par type (bureau/portable)
- Section spéciale pour les matériels en stock limité
- Actions rapides pour allouer du matériel

### Gestion des matériels

- **Allocation** : Attribuez du matériel à un utilisateur
- **Consultation** : Visualisez les détails et la disponibilité
- **Filtrage** : Triez par type de matériel

### Rapports

- **Utilisation du matériel** : Statistiques d'allocation et de retour
- **Inventaire** : État actuel des stocks
- **Activité utilisateur** : Suivi des actions par utilisateur

### Notifications

- **Création** : Envoyez des notifications aux utilisateurs
- **Diffusion** : Informez tous les utilisateurs d'un message important
- **Gestion** : Marquez comme lu, filtrez et supprimez les notifications

## 🔧 Dépannage

### Problèmes courants

| Problème | Solution |
|----------|----------|
| Erreur de connexion | Vérifiez les identifiants (admin/admin123 ou user1/user123) |
| Erreur "Address already in use" | Modifiez le port dans le fichier `.env` |
| Modules Python non trouvés | Vérifiez l'installation avec `pip list` |
| Problèmes d'affichage | Videz le cache du navigateur ou essayez un autre navigateur |

### Logs d'erreur

Les erreurs sont enregistrées dans la console où s'exécute l'application Flask. Consultez ces logs pour diagnostiquer les problèmes.

## 📁 Structure du projet

```
├── .env                    # Variables d'environnement
├── app.py                  # Point d'entrée de l'application Flask
├── config.py               # Configuration de l'application
├── lua_integration.py      # Intégration de Lua avec Flask
├── lua/                    # Fichiers Lua pour la logique métier
│   ├── app.lua             # Point d'entrée Lua
│   ├── inventory_manager.lua  # Gestionnaire d'inventaire
│   ├── material.lua        # Modèle de matériel
│   ├── notification_system.lua # Système de notifications
│   └── reports_generator.lua  # Générateur de rapports
├── models/                 # Modèles de données Python
│   └── user.py             # Modèle utilisateur
├── requirements.txt        # Dépendances Python
├── static/                 # Fichiers statiques
│   ├── css/                # Styles CSS
│   └── js/                 # Scripts JavaScript
└── templates/              # Templates HTML
    ├── auth/               # Pages d'authentification
    ├── dashboard.html      # Tableau de bord
    ├── reports.html        # Page des rapports
    └── layouts/            # Layouts communs
```

## 🔄 Futures améliorations

- [ ] Interface d'administration avancée
- [ ] Historique des mouvements avec statistiques
- [ ] Gestion des réservations de matériel
- [ ] Système de QR codes pour le suivi physique
- [ ] Application mobile compagnon
- [ ] Intégration avec les services d'inventaire existants

## 📝 Licence

Ce projet est sous licence [MIT](https://opensource.org/licenses/MIT).

## 🤝 Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à soumettre des issues ou des pull requests.

## 📧 Contact

Pour toute question ou suggestion, contactez-nous à l'adresse : sgm-support@exemple.fr

---

Développé avec ❤️ par [Emmanuel Ah-Hong]

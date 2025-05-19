# Système de Gestion de Matériel (SGM)

Un système moderne pour gérer l'inventaire de matériel informatique, développé avec Flask et Lua.

![Badge Version](https://img.shields.io/badge/version-1.0.0-blue)
![Badge Python](https://img.shields.io/badge/Python-3.7%2B-yellow)
![Badge Flask](https://img.shields.io/badge/Flask-3.0.0-green)
![Badge Lua](https://img.shields.io/badge/Lua-5.3-red)

## 📋 Fonctionnalités

- **Inventaire en temps réel** : Suivez tous vos équipements informatiques
- **Filtrage par type** : Affichez uniquement les ordinateurs de bureau ou portables
- **Alertes de stock** : Identification visuelle des matériels en quantité limitée
- **API REST** : Accédez aux données via une API JSON
- **Responsive** : Interface adaptée à tous les appareils
- **Mode hors ligne** : Fonctionnalités de base disponibles sans connexion

## 🛠️ Guide d'installation

### Prérequis

- Python 3.7 ou supérieur
- Pip (gestionnaire de paquets Python)
- Navigateur web moderne

### Étape 1 : Téléchargement du projet

```bash
# Clonez le dépôt Git (si disponible)
git clone https://github.com/votre-utilisateur/systeme-gestion-materiel.git
cd systeme-gestion-materiel

# OU téléchargez et extrayez l'archive du projet
# puis naviguez dans le dossier extrait
cd chemin/vers/dossier/projet
```

### Étape 2 : Installation des dépendances

Les modules suivants sont nécessaires au fonctionnement de l'application :

- **Flask** : Framework web pour Python
- **python-dotenv** : Gestion des variables d'environnement
- **lupa** : Intégration de Lua dans Python

```bash
# Installation individuelle des modules
pip install flask
pip install python-dotenv
pip install lupa

# OU installation en utilisant le fichier requirements.txt
pip install -r requirements.txt
```

### Étape 3 : Configuration

1. Créez un fichier `.env` à la racine du projet avec le contenu suivant :

```
SECRET_KEY=votre_cle_secrete_a_changer_en_production
FLASK_ENV=development
PORT=5000
```

2. Personnalisez la configuration si nécessaire dans `config.py`

### Étape 4 : Lancement de l'application

```bash
# Lancement du serveur de développement
python app.py
```

L'application est maintenant accessible à l'adresse : [http://localhost:5000](http://localhost:5000)

## 🖥️ Utilisation

1. **Page d'accueil** : Présentation du système
2. **Tableau de bord** : Vue d'ensemble et liste des matériels
   - Utilisez les boutons de filtre pour afficher uniquement les ordinateurs de bureau ou portables
   - Les matériels en stock limité (moins de 20%) sont mis en évidence en rouge
3. **Page À propos** : Informations sur l'application

## 🔧 Dépannage

### Problèmes courants

| Problème | Solution |
|----------|----------|
| `ModuleNotFoundError: No module named 'flask'` | Vérifiez que Flask est bien installé avec `pip install flask` |
| `ModuleNotFoundError: No module named 'dotenv'` | Installez python-dotenv avec `pip install python-dotenv` |
| `ModuleNotFoundError: No module named 'lupa'` | Installez lupa avec `pip install lupa` |
| Erreur lors du chargement des fichiers Lua | Vérifiez que les fichiers Lua sont correctement placés dans le dossier `/lua` |
| Erreur "Address already in use" | Un autre service utilise déjà le port 5000. Modifiez la valeur du port dans le fichier `.env` |

### Vérification de l'installation

Pour vérifier que tous les modules sont correctement installés :

```bash
pip list | findstr flask
pip list | findstr python-dotenv
pip list | findstr lupa
```

Ces commandes devraient afficher les versions installées de chaque module.

## 📁 Structure du projet

```
.
├── .env                    # Variables d'environnement
├── app.py                  # Point d'entrée de l'application Flask
├── config.py               # Configuration de l'application
├── lua                     # Fichiers Lua
│   ├── app.lua             # Point d'entrée Lua
│   ├── home_controller.lua # Contrôleur d'accueil
│   └── material.lua        # Modèle de matériel
├── requirements.txt        # Dépendances Python
├── static                  # Fichiers statiques
│   ├── css
│   │   └── style.css       # Styles CSS
│   └── js
│       ├── app.js          # JavaScript principal
│       └── sw.js           # Service Worker
└── templates               # Templates HTML
    ├── about.html          # Page À propos
    ├── dashboard.html      # Tableau de bord
    ├── error.html          # Page d'erreur
    ├── index.html          # Page d'accueil
    └── layouts
        └── main.html       # Template de base
```

## 🔄 Mises à jour futures

- [ ] Système d'authentification des utilisateurs
- [ ] Gestion des emprunts de matériel
- [ ] Tableau de bord analytique avancé
- [ ] Historique des mouvements
- [ ] Application mobile

## 📝 Licence

Ce projet est sous licence [MIT](https://opensource.org/licenses/MIT).

## 🤝 Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à soumettre des issues ou des pull requests.

---

Développé avec ❤️ par [Emmanuel ah-hong]

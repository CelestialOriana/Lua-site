from flask import Flask, render_template, jsonify, redirect, url_for, request
import os
import sys
import traceback
from dotenv import load_dotenv
import logging
import json

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

# Initialiser l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')

# Données factices directement dans le fichier Python
MATERIALS = [
    {"id": 1, "name": "ThinkCentre Gen 2", "type": "desktop", "available": 5, "total": 10, "description": "Ordinateur de bureau ThinkCentre Gen 2"},
    {"id": 2, "name": "ThinkCentre Gen 3", "type": "desktop", "available": 3, "total": 8, "description": "Ordinateur de bureau ThinkCentre Gen 3"},
    {"id": 3, "name": "ThinkCentre Gen 4", "type": "desktop", "available": 7, "total": 15, "description": "Ordinateur de bureau ThinkCentre Gen 4"},
    {"id": 4, "name": "ThinkCentre Gen 5", "type": "desktop", "available": 2, "total": 6, "description": "Ordinateur de bureau ThinkCentre Gen 5"},
    {"id": 5, "name": "ThinkPad X1", "type": "laptop", "available": 4, "total": 10, "description": "Ordinateur portable ThinkPad X1"},
    {"id": 6, "name": "ThinkPad T14", "type": "laptop", "available": 6, "total": 12, "description": "Ordinateur portable ThinkPad T14"}
]

# Calcul du total
def calculate_total_materials():
    total = 0
    for material in MATERIALS:
        total += material["total"]
    return total

@app.route("/")
def index():
    try:
        welcome_message = "Bienvenue dans le Système de Gestion de Matériel"
        return render_template('index.html', message=welcome_message)
    except Exception as e:
        logger.error(f"Erreur sur la page d'accueil: {e}")
        traceback.print_exc()
        return render_template('error.html', error="Une erreur est survenue sur la page d'accueil")

@app.route("/dashboard")
def dashboard():
    try:
        materials = MATERIALS
        total_materials = calculate_total_materials()
        return render_template('dashboard.html', 
                              materials=materials, 
                              total_materials=total_materials)
    except Exception as e:
        logger.error(f"Erreur sur le dashboard: {e}")
        traceback.print_exc()
        error_details = f"Type d'erreur: {type(e).__name__}, Message: {str(e)}"
        return render_template('error.html', error=f"Une erreur est survenue lors du chargement du tableau de bord", message=error_details)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/stage")
def stage():
    # Vérifier quel template existe réellement
    template_name = 'stage.html'
    
    # Si stage.html n'existe pas mais stage-template.html existe, utiliser ce dernier
    if not os.path.exists(os.path.join(app.template_folder, template_name)) and \
       os.path.exists(os.path.join(app.template_folder, 'stage-template.html')):
        template_name = 'stage-template.html'
    
    try:
        return render_template(template_name)
    except Exception as e:
        logger.error(f"Erreur sur la page de stage: {e}")
        return render_template('error.html', error="La page de stage n'est pas disponible pour le moment")

@app.route("/api/materials")
def api_materials():
    try:
        return jsonify(MATERIALS)
    except Exception as e:
        logger.error(f"Erreur API matériels: {e}")
        return jsonify({"error": "Une erreur est survenue"}), 500

# Route pour afficher les informations de débogage
@app.route("/debug")
def debug_info():
    if not app.debug:
        return redirect(url_for('index'))
    
    debug_data = {
        "Python Version": sys.version,
        "Flask Version": Flask.__version__,
        "Template Folder": app.template_folder,
        "Static Folder": app.static_folder,
        "Working Directory": os.getcwd(),
        "Templates Available": os.listdir(app.template_folder) if os.path.exists(app.template_folder) else [],
        "Static Files Available": os.listdir(app.static_folder) if os.path.exists(app.static_folder) else [],
        "Materials Data": MATERIALS
    }
    
    return render_template('debug.html', debug_data=debug_data)

# Gestion des erreurs
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="404", message="La page que vous cherchez semble avoir été emportée par les vagues ou n'a jamais existé."), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error="500", message="Une erreur est survenue sur le serveur. Nos équipes techniques ont été informées."), 500

# Vérifier la disponibilité des templates au démarrage
def check_templates():
    templates_to_check = ['index.html', 'dashboard.html', 'about.html', 'error.html']
    missing_templates = []
    
    for template in templates_to_check:
        if not os.path.exists(os.path.join(app.template_folder, template)):
            missing_templates.append(template)
    
    if missing_templates:
        logger.warning(f"Templates manquants: {', '.join(missing_templates)}")
    else:
        logger.info("Tous les templates essentiels sont disponibles")
    
    # Vérifier si le logo existe
    logo_path = os.path.join(app.static_folder, 'images', 'region_reunion.png')
    if os.path.exists(logo_path):
        logger.info("Logo de la Région Réunion trouvé")
    else:
        logger.warning(f"Logo de la Région Réunion non trouvé à l'emplacement: {logo_path}")

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    # Afficher des informations de démarrage
    logger.info(f"Démarrage de l'application sur le port {port}")
    logger.info(f"Mode debug: {debug}")
    logger.info(f"Dossier des templates: {app.template_folder}")
    logger.info(f"Dossier statique: {app.static_folder}")
    
    # Vérifier les templates et le logo
    check_templates()
    
    app.run(host='0.0.0.0', port=port, debug=debug)

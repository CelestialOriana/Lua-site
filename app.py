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

# Importer et initialiser l'intégration Lua après l'initialisation de l'app
from lua_integration import init_lua

# Initialisation correcte de lua_integration qui retourne une instance
# IMPORTANT: Passez skip_routes=True pour éviter les conflits de route
lua_integration = init_lua(app, skip_routes=True)

# Données factices directement dans le fichier Python (conservées pour la compatibilité)
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

# Nouvelles routes utilisant Lua

@app.route("/api/allocate", methods=["POST"])
def allocate_material():
    """Route pour allouer un matériel à un utilisateur."""
    data = request.json
    material_id = data.get('material_id')
    user_id = data.get('user_id')
    quantity = data.get('quantity', 1)
    
    # Créer le contexte pour le moteur de règles
    context = {
        'user_id': user_id,
        'user_role': 'standard',
        'user_allocation_count': 2,
        'material_id': material_id,
        'quantity': quantity
    }
    
    # Vérifier les règles
    result = lua_integration.call_lua_function('rules_engine', 'validate', 'material_allocation', context)
    success, message = result if isinstance(result, tuple) else (result, None)
    
    if not success:
        return jsonify({"success": False, "message": message}), 400
    
    # Si les règles sont validées, procéder à l'allocation
    result = lua_integration.call_lua_function('inventory_manager', 'allocate_material', material_id, user_id, quantity)
    success, transaction_id = result if isinstance(result, tuple) else (result, None)
    
    if success:
        return jsonify({"success": True, "transaction_id": transaction_id})
    else:
        return jsonify({"success": False, "message": transaction_id}), 400

@app.route("/api/reports/usage", methods=["GET"])
def material_usage_report():
    """Route pour générer un rapport d'utilisation du matériel."""
    start_date = request.args.get('start_date', '2025-01-01')
    end_date = request.args.get('end_date', '2025-05-01')
    
    try:
        report = lua_integration.call_lua_function('reports_generator', 'generate_material_usage_report', start_date, end_date)
        
        if request.args.get('format') == 'json':
            return jsonify(report)
        else:
            # Utiliser le template de rapport
            return render_template('reports/report_template.html', **report)
    except Exception as e:
        logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "Erreur lors de la génération du rapport: " + str(e)}), 500

@app.route("/api/inventory/report", methods=["GET"])
def inventory_report():
    """Route pour générer un rapport d'inventaire."""
    try:
        report = lua_integration.call_lua_function('reports_generator', 'generate_inventory_report')
        
        if request.args.get('format') == 'json':
            return jsonify(report)
        else:
            # Utiliser le template de rapport
            return render_template('reports/report_template.html', **report)
    except Exception as e:
        logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "Erreur lors de la génération du rapport: " + str(e)}), 500

@app.route("/api/notifications", methods=["GET"])
def get_notifications():
    """Route pour récupérer les notifications d'un utilisateur."""
    user_id = request.args.get('user_id')
    include_read = request.args.get('include_read', 'false').lower() == 'true'
    
    if not user_id:
        return jsonify({"error": "L'ID utilisateur est requis"}), 400
    
    try:
        notifications = lua_integration.call_lua_function('notification_system', 'get_notifications', user_id, include_read)
        return jsonify({"notifications": notifications})
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des notifications: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "Erreur lors de la récupération des notifications"}), 500

@app.route("/api/notifications/mark-read", methods=["POST"])
def mark_notification_read():
    """Route pour marquer une notification comme lue."""
    data = request.json
    notification_id = data.get('notification_id')
    
    if not notification_id:
        return jsonify({"error": "L'ID de notification est requis"}), 400
    
    try:
        success = lua_integration.call_lua_function('notification_system', 'mark_as_read', notification_id)
        return jsonify({"success": success})
    except Exception as e:
        logger.error(f"Erreur lors du marquage de la notification: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "Erreur lors du marquage de la notification"}), 500

@app.route("/api/cache/stats", methods=["GET"])
def cache_stats():
    """Route pour obtenir des statistiques sur le cache."""
    try:
        stats = lua_integration.call_lua_function('smart_cache', 'get_stats')
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des stats du cache: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "Erreur lors de la récupération des stats du cache"}), 500

@app.route("/reports")
def reports_page():
    """Page des rapports."""
    try:
        return render_template('reports.html')
    except Exception as e:
        logger.error(f"Erreur sur la page des rapports: {str(e)}")
        traceback.print_exc()
        return render_template('error.html', error="Erreur sur la page des rapports")

# Routes API pour Lua - DÉFINIES DIRECTEMENT ICI, PAS DANS L'INTÉGRATION LUA

@app.route("/api/lua/modules/list", methods=["GET"])
def list_lua_modules():
    """Liste tous les modules Lua chargés."""
    try:
        modules = list(lua_integration.modules.keys())
        return jsonify({'modules': modules})
    except Exception as e:
        logger.error(f"Erreur lors de la liste des modules Lua: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "Erreur lors de la liste des modules Lua"}), 500

@app.route("/api/lua/modules/reload", methods=["POST"])
def reload_all_lua_modules():
    """Recharge tous les modules Lua."""
    try:
        lua_integration.reload_all_modules()
        return jsonify({'success': True, 'message': 'Tous les modules Lua ont été rechargés'})
    except Exception as e:
        logger.error(f"Erreur lors du rechargement des modules Lua: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "Erreur lors du rechargement des modules Lua"}), 500

@app.route("/api/lua/module/<module_name>/reload", methods=["POST"])
def reload_lua_module(module_name):
    """Recharge un module Lua spécifique."""
    try:
        module = lua_integration.reload_module(module_name)
        if module:
            return jsonify({'success': True, 'message': f'Module {module_name} rechargé'})
        else:
            return jsonify({'success': False, 'message': f'Échec du rechargement du module {module_name}'}), 404
    except Exception as e:
        logger.error(f"Erreur lors du rechargement du module {module_name}: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Erreur lors du rechargement du module {module_name}"}), 500

# Gestion des erreurs
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="404", message="La page que vous cherchez semble avoir été emportée par les vagues ou n'a jamais existé."), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error="500", message="Une erreur est survenue sur le serveur. Nos équipes techniques ont été informées."), 500

# Si ce fichier est exécuté directement, lancer l'application
if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    # Afficher des informations de démarrage
    logger.info(f"Démarrage de l'application sur le port {port}")
    logger.info(f"Mode debug: {debug}")
    logger.info(f"Intégration Lua initialisée")
    
    # Vérifier que lua_integration est bien initialisé avant d'accéder à ses attributs
    if lua_integration and hasattr(lua_integration, 'modules'):
        logger.info(f"Modules Lua chargés: {list(lua_integration.modules.keys())}")
    else:
        logger.warning("L'intégration Lua n'est pas correctement initialisée")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
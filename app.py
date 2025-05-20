# app.py optimisé

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
# Passer skip_routes=True pour éviter les conflits de route
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

# Identifie les matériels en stock limité
def get_low_stock_items():
    low_stock = []
    for material in MATERIALS:
        if material["available"] / material["total"] < 0.2:  # Moins de 20% disponible
            low_stock.append(material)
    return low_stock

# Compte les types de matériels uniques
def count_material_types():
    types = set()
    for material in MATERIALS:
        types.add(material["type"])
    return len(types)

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
        # Données de base pour le dashboard
        materials = MATERIALS
        total_materials = calculate_total_materials()
        
        # Calcul correct du total des matériels disponibles
        available_materials = sum(material["available"] for material in materials)
        
        # Calcul du nombre de types différents
        material_types = count_material_types()
        
        # Obtenir les matériels en stock limité
        low_stock_items = get_low_stock_items()
        low_stock_count = len(low_stock_items)
        
        # Vérifier si la page des rapports est disponible
        reports_page_available = True
        
        # Utilisation optionnelle du module Lua pour des statistiques avancées
        inventory_stats = None
        if lua_integration:
            try:
                # Tenter d'obtenir des statistiques d'inventaire via Lua
                inventory_stats = lua_integration.call_lua_function('inventory_manager', 'get_inventory_stats')
            except Exception as lua_error:
                logger.warning(f"Impossible d'obtenir les statistiques via Lua: {str(lua_error)}")
        
        # Si les statistiques Lua sont disponibles, les utiliser pour enrichir les données
        if inventory_stats:
            # Ici, on pourrait enrichir les données avec des statistiques avancées
            pass
        
        return render_template('dashboard.html', 
                              materials=materials, 
                              total_materials=total_materials,
                              available_materials=available_materials,
                              material_types=material_types,
                              low_stock_items=low_stock_items,
                              low_stock_count=low_stock_count,
                              reports_page_available=reports_page_available)
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
    # Vérifier si les données sont présentes et au bon format
    if not request.is_json:
        return jsonify({"success": False, "message": "Les données doivent être au format JSON"}), 400
    
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "Données manquantes"}), 400
        
    material_id = data.get('material_id')
    user_id = data.get('user_id')
    quantity = data.get('quantity', 1)
    
    # Validation de base
    if material_id is None:
        return jsonify({"success": False, "message": "ID matériel requis"}), 400
    
    if not user_id:
        return jsonify({"success": False, "message": "ID utilisateur requis"}), 400
    
    # Validation du type
    try:
        material_id = int(material_id)
        quantity = int(quantity)
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "ID matériel et quantité doivent être des nombres"}), 400
    
    # Validation de la quantité
    if quantity <= 0:
        return jsonify({"success": False, "message": "La quantité doit être positive"}), 400
    
    try:
        # Recherche du matériel par ID
        material = None
        for m in MATERIALS:
            if m["id"] == material_id:
                material = m
                break
        
        if not material:
            return jsonify({"success": False, "message": f"Matériel avec ID {material_id} non trouvé"}), 404
        
        # Vérifier si l'intégration Lua est disponible
        if lua_integration:
            try:
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
                if isinstance(result, tuple) and len(result) >= 2:
                    success, message = result
                else:
                    success = result
                    message = None
                
                if not success:
                    return jsonify({"success": False, "message": message or "Règles d'allocation non respectées"}), 400
                
                # Si les règles sont validées, procéder à l'allocation
                result = lua_integration.call_lua_function('inventory_manager', 'allocate_material', material_id, user_id, quantity)
                if isinstance(result, tuple) and len(result) >= 2:
                    success, transaction_id = result
                else:
                    success = result
                    transaction_id = f"{material_id}-{user_id}-{os.urandom(4).hex()}"
                
                if success:
                    # Mise à jour des données locales (pour la compatibilité)
                    material["available"] = max(0, material["available"] - quantity)
                    
                    return jsonify({"success": True, "transaction_id": transaction_id})
                else:
                    return jsonify({"success": False, "message": transaction_id or "Échec de l'allocation"}), 400
            except Exception as lua_error:
                logger.error(f"Erreur avec l'intégration Lua: {str(lua_error)}")
                # Continuer avec la logique de secours
        
        # Fallback si Lua n'est pas disponible ou a échoué
        if material["available"] >= quantity:
            material["available"] -= quantity
            transaction_id = f"{material_id}-{user_id}-{os.urandom(4).hex()}"
            return jsonify({"success": True, "transaction_id": transaction_id})
        else:
            return jsonify({"success": False, "message": f"Stock insuffisant. Disponible: {material['available']}, Demandé: {quantity}"}), 400
        
    except Exception as e:
        logger.error(f"Erreur lors de l'allocation: {str(e)}")
        traceback.print_exc()
        return jsonify({"success": False, "message": f"Erreur serveur lors de l'allocation: {str(e)}"}), 500

@app.route("/api/reports/usage", methods=["GET"])
def material_usage_report():
    """Route pour générer un rapport d'utilisation du matériel."""
    start_date = request.args.get('start_date', '2025-01-01')
    end_date = request.args.get('end_date', '2025-05-01')
    material_id = request.args.get('material_id')
    
    try:
        if lua_integration:
            # Générer le rapport via Lua
            if material_id:
                report = lua_integration.call_lua_function('reports_generator', 'generate_material_usage_report', start_date, end_date, int(material_id))
            else:
                report = lua_integration.call_lua_function('reports_generator', 'generate_material_usage_report', start_date, end_date)
            
            if request.args.get('format') == 'json':
                return jsonify(report)
            else:
                # Utiliser le template de rapport
                return render_template('reports/report_template.html', **report)
        else:
            # Fallback si Lua n'est pas disponible
            return jsonify({"error": "Générateur de rapports non disponible"}), 500
    except Exception as e:
        logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "Erreur lors de la génération du rapport: " + str(e)}), 500

@app.route("/api/inventory/report", methods=["GET"])
def inventory_report():
    """Route pour générer un rapport d'inventaire."""
    try:
        if lua_integration:
            report = lua_integration.call_lua_function('reports_generator', 'generate_inventory_report')
            
            if request.args.get('format') == 'json':
                return jsonify(report)
            else:
                # Utiliser le template de rapport
                return render_template('reports/report_template.html', **report)
        else:
            # Fallback si Lua n'est pas disponible
            return jsonify({"error": "Générateur de rapports non disponible"}), 500
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
        if lua_integration:
            notifications = lua_integration.call_lua_function('notification_system', 'get_notifications', user_id, include_read)
            return jsonify({"notifications": notifications})
        else:
            # Fallback si Lua n'est pas disponible
            return jsonify({"notifications": []}), 200
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
        if lua_integration:
            success = lua_integration.call_lua_function('notification_system', 'mark_as_read', notification_id)
            return jsonify({"success": success})
        else:
            # Fallback si Lua n'est pas disponible
            return jsonify({"success": False, "message": "Système de notifications non disponible"}), 500
    except Exception as e:
        logger.error(f"Erreur lors du marquage de la notification: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "Erreur lors du marquage de la notification"}), 500

@app.route("/api/cache/stats", methods=["GET"])
def cache_stats():
    """Route pour obtenir des statistiques sur le cache."""
    try:
        if lua_integration:
            stats = lua_integration.call_lua_function('smart_cache', 'get_stats')
            return jsonify(stats)
        else:
            # Fallback si Lua n'est pas disponible
            return jsonify({"error": "Système de cache non disponible"}), 500
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
        if lua_integration and hasattr(lua_integration, 'modules'):
            modules = list(lua_integration.modules.keys())
            return jsonify({'modules': modules})
        else:
            return jsonify({"error": "Intégration Lua non initialisée"}), 500
    except Exception as e:
        logger.error(f"Erreur lors de la liste des modules Lua: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "Erreur lors de la liste des modules Lua"}), 500

@app.route("/api/lua/modules/reload", methods=["POST"])
def reload_all_lua_modules():
    """Recharge tous les modules Lua."""
    try:
        if lua_integration:
            lua_integration.reload_all_modules()
            return jsonify({'success': True, 'message': 'Tous les modules Lua ont été rechargés'})
        else:
            return jsonify({"error": "Intégration Lua non initialisée"}), 500
    except Exception as e:
        logger.error(f"Erreur lors du rechargement des modules Lua: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "Erreur lors du rechargement des modules Lua"}), 500

@app.route("/api/lua/module/<module_name>/reload", methods=["POST"])
def reload_lua_module(module_name):
    """Recharge un module Lua spécifique."""
    try:
        if lua_integration:
            module = lua_integration.reload_module(module_name)
            if module:
                return jsonify({'success': True, 'message': f'Module {module_name} rechargé'})
            else:
                return jsonify({'success': False, 'message': f'Échec du rechargement du module {module_name}'}), 404
        else:
            return jsonify({"error": "Intégration Lua non initialisée"}), 500
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

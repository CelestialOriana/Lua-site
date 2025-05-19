# Intégration des modules Lua dans app.py

from flask import Flask, render_template, jsonify, redirect, url_for, request
import os
import sys
import traceback
from dotenv import load_dotenv
import logging
import json
from lua_integration import init_lua, lua_integration

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

# Initialiser l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')

# Initialiser l'intégration Lua
lua = init_lua(app)

# Routes existantes préservées...
# [Code existant de app.py...]

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
        'user_role': 'standard',  # À récupérer d'une DB en réalité
        'user_allocation_count': lua.call_lua_function('inventory_manager', 'get_user_transactions', user_id),
        'material_id': material_id,
        'quantity': quantity
    }
    
    # Vérifier les règles
    validate_result = lua.call_lua_function('rules_engine', 'validate', 'material_allocation', context)
    success, message = validate_result if isinstance(validate_result, tuple) else (validate_result, None)
    
    if not success:
        return jsonify({"success": False, "message": message}), 400
    
    # Si les règles sont validées, procéder à l'allocation
    allocation_result = lua.call_lua_function('inventory_manager', 'allocate_material', material_id, user_id, quantity)
    alloc_success, transaction_id = allocation_result if isinstance(allocation_result, tuple) else (allocation_result, None)
    
    if alloc_success:
        return jsonify({"success": True, "transaction_id": transaction_id})
    else:
        return jsonify({"success": False, "message": transaction_id}), 400

@app.route("/api/reports/usage", methods=["GET"])
def material_usage_report():
    """Route pour générer un rapport d'utilisation du matériel."""
    start_date = request.args.get('start_date', '2025-01-01')
    end_date = request.args.get('end_date', '2025-05-01')
    
    report = lua.call_lua_function('reports_generator', 'generate_material_usage_report', start_date, end_date)
    
    if request.args.get('format') == 'json':
        return jsonify(report)
    else:
        # Utiliser le moteur de template Lua pour rendre le HTML
        template_path = os.path.join(app.template_folder, 'reports', 'report_template.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        rendered_html = lua.call_lua_function('template_engine', 'render', template_content, report)
        return rendered_html

@app.route("/api/inventory/report", methods=["GET"])
def inventory_report():
    """Route pour générer un rapport d'inventaire."""
    report = lua.call_lua_function('reports_generator', 'generate_inventory_report')
    
    if request.args.get('format') == 'json':
        return jsonify(report)
    else:
        # Utiliser le moteur de template Lua pour rendre le HTML
        template_path = os.path.join(app.template_folder, 'reports', 'report_template.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        rendered_html = lua.call_lua_function('template_engine', 'render', template_content, report)
        return rendered_html

@app.route("/api/notifications", methods=["GET"])
def get_notifications():
    """Route pour récupérer les notifications d'un utilisateur."""
    user_id = request.args.get('user_id')
    include_read = request.args.get('include_read', 'false').lower() == 'true'
    
    if not user_id:
        return jsonify({"error": "L'ID utilisateur est requis"}), 400
    
    notifications = lua.call_lua_function('notification_system', 'get_notifications', user_id, include_read)
    return jsonify({"notifications": notifications})

@app.route("/api/notifications/mark-read", methods=["POST"])
def mark_notification_read():
    """Route pour marquer une notification comme lue."""
    data = request.json
    notification_id = data.get('notification_id')
    
    if not notification_id:
        return jsonify({"error": "L'ID de notification est requis"}), 400
    
    success = lua.call_lua_function('notification_system', 'mark_as_read', notification_id)
    return jsonify({"success": success})

@app.route("/api/cache/stats", methods=["GET"])
def cache_stats():
    """Route pour obtenir des statistiques sur le cache."""
    stats = lua.call_lua_function('smart_cache', 'get_stats')
    return jsonify(stats)

@app.route("/reports")
def reports_page():
    """Page des rapports."""
    return render_template('reports.html')

# Si ce fichier est exécuté directement, lancer l'application
if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    # Afficher des informations de démarrage
    logger.info(f"Démarrage de l'application sur le port {port}")
    logger.info(f"Mode debug: {debug}")
    logger.info(f"Intégration Lua initialisée")
    logger.info(f"Modules Lua chargés: {list(lua.modules.keys())}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

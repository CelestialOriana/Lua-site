from flask import Flask, render_template, jsonify, redirect, url_for, request, flash
import os
import sys
import traceback
from dotenv import load_dotenv
import logging
import json
import time 

# Imports pour l'authentification
from flask_login import LoginManager, login_user, logout_user, login_required, current_user  # type: ignore
from flask_bcrypt import Bcrypt  # type: ignore
from models.user import User, get_user_by_id, get_user_by_username, get_user_by_email, add_user 

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

# Initialiser l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')

# Initialiser Bcrypt et LoginManager
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'

# User loader pour Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

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

# Routes d'authentification
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        # Chercher l'utilisateur par nom d'utilisateur ou email
        user = get_user_by_username(username) or get_user_by_email(username)
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=remember)
            flash('Connexion réussie !', 'success')
            
            # Rediriger vers la page demandée ou le tableau de bord
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Échec de la connexion. Vérifiez vos identifiants.', 'error')
    
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation de base
        if get_user_by_username(username):
            flash('Ce nom d\'utilisateur est déjà pris.', 'error')
            return render_template('auth/register.html')
        
        if get_user_by_email(email):
            flash('Cet email est déjà utilisé.', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Le mot de passe doit contenir au moins 6 caractères.', 'error')
            return render_template('auth/register.html')
        
        # Hachage du mot de passe et création de l'utilisateur
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = add_user(username, email, hashed_password, role='user', name=name)
        
        flash('Inscription réussie ! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('auth/login.html')

@app.route("/dashboard")
@login_required
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

# Nouvelles routes pour le système de notifications

@app.route("/notifications")
@login_required
def notifications_dashboard():
    """Page du tableau de bord des notifications."""
    try:
        return render_template('notification-dashboard.html')
    except Exception as e:
        logger.error(f"Erreur sur la page des notifications: {str(e)}")
        traceback.print_exc()
        return render_template('error.html', error="Erreur sur la page des notifications")

@app.route("/api/notifications/add", methods=["POST"])
@login_required
def add_notification():
    """Route pour ajouter une notification (version simplifiée)."""
    data = request.json
    user_id = data.get('user_id')
    notification_type = data.get('type', 'info')
    message = data.get('message')
    metadata = data.get('metadata', {})
    
    if not user_id or not message:
        return jsonify({"success": False, "message": "L'ID utilisateur et le message sont requis"}), 400
    
    try:
        logger.info(f"Tentative d'ajout de notification - User: {user_id}, Type: {notification_type}, Message: {message}")
        
        # Simuler l'ajout d'une notification sans appeler Lua pour tests
        notification_id = hash(f"{user_id}-{message}-{time.time()}")
        
        logger.info(f"Notification simulée ajoutée avec succès, ID: {notification_id}")
        return jsonify({"success": True, "notification_id": notification_id})
        
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout de la notification: {str(e)}")
        traceback.print_exc()
        return jsonify({"success": False, "message": f"Erreur lors de l'ajout de la notification: {str(e)}"}), 500

@app.route("/api/notifications/broadcast", methods=["POST"])
@login_required
def broadcast_notification():
    """Route pour diffuser une notification à tous les utilisateurs."""
    data = request.json
    message = data.get('message')
    metadata = data.get('metadata', {})
    
    if not message:
        return jsonify({"success": False, "message": "Le message est requis"}), 400
    
    try:
        # Simuler la diffusion d'une notification
        users = ["user1", "user2", "user3", "admin"]
        notification_ids = []
        
        for user in users:
            notification_id = hash(f"{user}-{message}-{time.time()}")
            notification_ids.append(notification_id)
        
        return jsonify({"success": True, "notification_ids": notification_ids})
    except Exception as e:
        logger.error(f"Erreur lors de la diffusion de la notification: {str(e)}")
        traceback.print_exc()
        return jsonify({"success": False, "message": f"Erreur lors de la diffusion de la notification: {str(e)}"}), 500

@app.route("/api/notifications/delete", methods=["POST"])
@login_required
def delete_notification():
    """Route pour supprimer une notification."""
    data = request.json
    notification_id = data.get('notification_id')
    
    if not notification_id:
        return jsonify({"success": False, "message": "L'ID de notification est requis"}), 400
    
    # Simuler la suppression
    return jsonify({"success": True})

@app.route("/api/notifications/mark-all-read", methods=["POST"])
@login_required
def mark_all_notifications_read():
    """Route pour marquer toutes les notifications d'un utilisateur comme lues."""
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"success": False, "message": "L'ID utilisateur est requis"}), 400
    
    # Simuler le marquage de notifications
    count = 5  # nombre fictif de notifications marquées
    return jsonify({"success": True, "count": count})

# Route temporaire pour recharger le module de règles (accepte GET et POST)
@app.route("/api/reload_rules", methods=["GET", "POST"])
@login_required
def reload_rules_module():
    """Route temporaire pour recharger le module de règles pendant le développement."""
    try:
        if lua_integration:
            result = lua_integration.reload_module('rules_engine')
            if result:
                return jsonify({"success": True, "message": "Module rules_engine rechargé avec succès"})
            else:
                return jsonify({"success": False, "message": "Échec du rechargement du module rules_engine"}), 500
        else:
            return jsonify({"error": "Intégration Lua non initialisée"}), 500
    except Exception as e:
        logger.error(f"Erreur lors du rechargement du module rules_engine: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Erreur lors du rechargement: {str(e)}"}), 500

# Routes utilisant Lua

@app.route("/api/allocate", methods=["POST"])
@login_required
def allocate_material():
    """Route pour allouer un matériel à un utilisateur."""
    # Vérifier si les données sont présentes et au bon format
    if not request.is_json:
        return jsonify({"success": False, "message": "Les données doivent être au format JSON"}), 400
    
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "Données manquantes"}), 400
        
    material_id = data.get('material_id')
    user_id = data.get('user_id', current_user.id)  # Utiliser l'ID de l'utilisateur connecté par défaut
    quantity = data.get('quantity', 1)
    
    # Log des données reçues pour debug
    logger.info(f"Tentative d'allocation - Material: {material_id}, User: {user_id}, Quantity: {quantity}")
    
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
        
        # Vérifier si la quantité disponible est suffisante
        if material["available"] >= quantity:
            # Mise à jour du stock
            material["available"] -= quantity
            transaction_id = f"{material_id}-{user_id}-{os.urandom(4).hex()}"
            logger.info(f"Allocation réussie. Transaction: {transaction_id}")
            
            # Simuler l'ajout d'une notification
            notification_id = hash(f"{user_id}-allocation-{transaction_id}")
            
            return jsonify({"success": True, "transaction_id": transaction_id})
        else:
            logger.error(f"Stock insuffisant. Disponible: {material['available']}, Demandé: {quantity}")
            return jsonify({"success": False, "message": f"Stock insuffisant. Disponible: {material['available']}, Demandé: {quantity}"}), 400
        
    except Exception as e:
        logger.error(f"Erreur lors de l'allocation: {str(e)}")
        traceback.print_exc()
        return jsonify({"success": False, "message": f"Erreur serveur lors de l'allocation: {str(e)}"}), 500

@app.route("/api/reports/usage", methods=["GET"])
@login_required
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
@login_required
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
@login_required
def get_notifications():
    """Route pour récupérer les notifications d'un utilisateur."""
    user_id = request.args.get('user_id', current_user.id)  # Utiliser l'ID de l'utilisateur connecté par défaut
    include_read = request.args.get('include_read', 'false').lower() == 'true'
    
    if not user_id:
        return jsonify({"error": "L'ID utilisateur est requis"}), 400
    
    try:
        # Simuler les notifications pour tests
        notifications = []
        notification_types = ["info", "warning", "error", "success", "system"]
        
        for i in range(5):
            read = i % 2 == 0  # Alterner entre lu et non lu
            if not include_read and read:
                continue
                
            notification = {
                "id": i + 1,
                "user_id": user_id,
                "type": notification_types[i % len(notification_types)],
                "message": f"Ceci est une notification de test #{i+1} pour {user_id}",
                "created_at": int(time.time()) - (i * 3600),  # Espacer d'une heure
                "read": read,
                "metadata": {"test_id": i, "source": "simulation"}
            }
            notifications.append(notification)
            
        return jsonify({"notifications": notifications})
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des notifications: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "Erreur lors de la récupération des notifications"}), 500

@app.route("/api/notifications/mark-read", methods=["POST"])
@login_required
def mark_notification_read():
    """Route pour marquer une notification comme lue."""
    data = request.json
    notification_id = data.get('notification_id')
    
    if not notification_id:
        return jsonify({"error": "L'ID de notification est requis"}), 400
    
    # Simuler le marquage comme lu
    return jsonify({"success": True})

@app.route("/api/cache/stats", methods=["GET"])
@login_required
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
@login_required
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
@login_required
def list_lua_modules():
    """Liste tous les modules Lua chargés."""
    # Vérifier si l'utilisateur est admin
    if not current_user.is_admin():
        return jsonify({"error": "Accès non autorisé"}), 403
        
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

@app.route("/api/lua/modules/reload", methods=["POST", "GET"])
@login_required
def reload_all_lua_modules():
    """Recharge tous les modules Lua."""
    # Vérifier si l'utilisateur est admin
    if not current_user.is_admin():
        return jsonify({"error": "Accès non autorisé"}), 403
        
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

@app.route("/api/lua/module/<module_name>/reload", methods=["POST", "GET"])
@login_required
def reload_lua_module(module_name):
    """Recharge un module Lua spécifique."""
    # Vérifier si l'utilisateur est admin
    if not current_user.is_admin():
        return jsonify({"error": "Accès non autorisé"}), 403
        
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

# Nouvelle page admin pour les modules Lua
@app.route("/admin/lua-modules")
@login_required
def lua_modules_admin_page():
    """Page d'administration des modules Lua."""
    # Vérifier si l'utilisateur est admin
    if not current_user.is_admin():
        flash("Vous n'avez pas l'autorisation d'accéder à cette page.", "error")
        return redirect(url_for('dashboard'))
        
    try:
        if lua_integration and hasattr(lua_integration, 'modules'):
            modules = list(lua_integration.modules.keys())
            return render_template('admin/lua_modules.html', modules=modules)
        else:
            return render_template('error.html', error="Intégration Lua non initialisée")
    except Exception as e:
        logger.error(f"Erreur sur la page d'administration Lua: {str(e)}")
        traceback.print_exc()
        return render_template('error.html', error="Erreur sur la page d'administration Lua")

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
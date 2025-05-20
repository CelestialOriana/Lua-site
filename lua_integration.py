# lua_integration.py mis à jour pour éviter les conflits de route

from flask import jsonify, request
from lupa import LuaRuntime
import os
import json
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LuaIntegration:
    def __init__(self, lua_path='lua'):
        """Initialise l'intégration Lua avec Flask."""
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua_path = lua_path
        self.modules = {}
        
        # Assurez-vous que le dossier Lua existe
        if not os.path.exists(lua_path):
            os.makedirs(lua_path)
            logger.warning(f"Dossier Lua créé: {lua_path}")
        
        # Configurer le chemin Lua pour les imports
        self._setup_lua_path()
        
        # Charger les modules essentiels
        self._load_essential_modules()
    
    def _setup_lua_path(self):
        """Configure le chemin de recherche des modules Lua."""
        setup_code = f"""
        package.path = package.path .. ";{self.lua_path}/?.lua"
        """
        self.lua.execute(setup_code)
    
    def _load_module(self, module_name):
        """Charge un module Lua dans la mémoire."""
        try:
            module_path = os.path.join(self.lua_path, f"{module_name}.lua")
            
            if not os.path.exists(module_path):
                logger.error(f"Module Lua introuvable: {module_path}")
                return None
            
            with open(module_path, 'r', encoding='utf-8') as f:
                module_code = f.read()
            
            # Exécuter le code Lua pour charger le module
            self.modules[module_name] = self.lua.execute(module_code)
            logger.info(f"Module Lua chargé: {module_name}")
            return self.modules[module_name]
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du module Lua {module_name}: {str(e)}")
            return None
    
    def _load_essential_modules(self):
        """Charge les modules Lua essentiels pour l'application."""
        essential_modules = [
            'app',                  # Module principal
            'home_controller',      # Contrôleur de page d'accueil
            'material',             # Modèle de matériel
            'inventory_manager',    # Gestionnaire d'inventaire
            'rules_engine',         # Moteur de règles
            'reports_generator',    # Générateur de rapports
            'template_engine',      # Moteur de templates
            'smart_cache',          # Système de cache
            'notification_system'   # Système de notifications
        ]
        
        for module_name in essential_modules:
            if os.path.exists(os.path.join(self.lua_path, f"{module_name}.lua")):
                self._load_module(module_name)
    
    def get_module(self, module_name):
        """Récupère un module Lua, le charge s'il n'est pas déjà chargé."""
        if module_name not in self.modules:
            return self._load_module(module_name)
        return self.modules[module_name]
    
    def reload_module(self, module_name):
        """Recharge un module Lua."""
        if module_name in self.modules:
            del self.modules[module_name]
        return self._load_module(module_name)
    
    def reload_all_modules(self):
        """Recharge tous les modules Lua."""
        module_names = list(self.modules.keys())
        for module_name in module_names:
            self.reload_module(module_name)
    
    def python_to_lua(self, data):
        """Convertit une structure de données Python en Lua."""
        if isinstance(data, dict):
            # Créer une table Lua
            lua_table = self.lua.table()
            for key, value in data.items():
                lua_table[key] = self.python_to_lua(value)
            return lua_table
        elif isinstance(data, list):
            # Créer une liste Lua (table avec des indices numériques)
            lua_list = self.lua.table()
            for i, value in enumerate(data, 1):  # Lua utilise des indices à partir de 1
                lua_list[i] = self.python_to_lua(value)
            return lua_list
        else:
            # Types primitifs (str, int, float, bool, None)
            return data
    
    def lua_to_python(self, lua_data):
        """Convertit une structure de données Lua en Python."""
        if self.lua.table_from(lua_data) is not None:
            # C'est une table Lua
            result = {}
            is_array = True
            max_index = 0
            
            # Parcourir la table
            for k, v in self.lua.pairs(lua_data):
                result[self.lua_to_python(k)] = self.lua_to_python(v)
                
                # Vérifier si c'est un tableau ou un dictionnaire
                if isinstance(k, (int, float)) and int(k) == k and k > 0:
                    max_index = max(max_index, int(k))
                else:
                    is_array = False
            
            # Si c'est un tableau, convertir en liste Python
            if is_array and max_index > 0:
                python_list = [None] * max_index
                for i in range(1, max_index + 1):
                    if i in result:
                        python_list[i-1] = result[i]
                return python_list
            
            return result
        else:
            # Types primitifs
            return lua_data
    
    def call_lua_function(self, module_name, function_name, *args, **kwargs):
        """Appelle une fonction Lua avec les arguments spécifiés."""
        module = self.get_module(module_name)
        if not module:
            logger.error(f"Module Lua non trouvé: {module_name}")
            return None
        
        # Convertir les arguments de Python à Lua
        lua_args = [self.python_to_lua(arg) for arg in args]
        
        # Convertir les arguments nommés en table Lua
        if kwargs:
            lua_kwargs = self.python_to_lua(kwargs)
            lua_args.append(lua_kwargs)
        
        try:
            # Si la fonction est une méthode d'un objet Lua
            if function_name.find(':') > 0:
                obj_name, method_name = function_name.split(':')
                lua_object = module[obj_name]
                lua_function = getattr(lua_object, method_name)
                result = lua_function(lua_object, *lua_args)
            else:
                # Sinon, c'est une fonction normale
                lua_function = module[function_name]
                result = lua_function(*lua_args)
            
            # Convertir le résultat de Lua à Python
            return self.lua_to_python(result)
        except Exception as e:
            logger.error(f"Erreur lors de l'appel de la fonction Lua {module_name}.{function_name}: {str(e)}")
            return None

# Instance globale pour l'intégration Lua
lua_integration = None

def init_lua(app, lua_path='lua', skip_routes=False):
    """Initialise l'intégration Lua et ajoute les routes nécessaires à l'application Flask.
    
    Args:
        app: L'application Flask
        lua_path: Chemin vers le répertoire des fichiers Lua
        skip_routes: Si True, ne pas ajouter les routes automatiquement (pour éviter les conflits)
    
    Returns:
        Une instance de LuaIntegration
    """
    global lua_integration
    lua_integration = LuaIntegration(lua_path)
    
    # Ajouter les routes spéciales pour l'intégration Lua, sauf si skip_routes est True
    if not skip_routes:
        add_lua_routes(app)
    
    return lua_integration

def add_lua_routes(app):
    """Ajoute des routes Flask pour interagir avec Lua."""
    
    @app.route('/api/lua/module/<module_name>/reload', methods=['POST'])
    def reload_lua_module(module_name):
        """Recharge un module Lua spécifique."""
        if not lua_integration:
            return jsonify({'error': 'Intégration Lua non initialisée'}), 500
        
        module = lua_integration.reload_module(module_name)
        if module:
            return jsonify({'success': True, 'message': f'Module {module_name} rechargé'})
        else:
            return jsonify({'success': False, 'message': f'Échec du rechargement du module {module_name}'}), 404
    
    @app.route('/api/lua/modules/reload', methods=['POST'])
    def reload_all_lua_modules():
        """Recharge tous les modules Lua."""
        if not lua_integration:
            return jsonify({'error': 'Intégration Lua non initialisée'}), 500
        
        lua_integration.reload_all_modules()
        return jsonify({'success': True, 'message': 'Tous les modules Lua ont été rechargés'})
    
    @app.route('/api/lua/modules/list', methods=['GET'])
    def list_lua_modules():
        """Liste tous les modules Lua chargés."""
        if not lua_integration:
            return jsonify({'error': 'Intégration Lua non initialisée'}), 500
        
        modules = list(lua_integration.modules.keys())
        return jsonify({'modules': modules})
    
    @app.route('/api/lua/call/<module_name>/<function_name>', methods=['POST'])
    def call_lua_function_api(module_name, function_name):
        """API pour appeler une fonction Lua depuis le frontend."""
        if not lua_integration:
            return jsonify({'error': 'Intégration Lua non initialisée'}), 500
        
        # Récupérer les arguments de la requête
        args = []
        kwargs = {}
        
        if request.is_json:
            data = request.get_json()
            if 'args' in data and isinstance(data['args'], list):
                args = data['args']
            if 'kwargs' in data and isinstance(data['kwargs'], dict):
                kwargs = data['kwargs']
        
        # Appeler la fonction Lua
        result = lua_integration.call_lua_function(module_name, function_name, *args, **kwargs)
        
        if result is None:
            return jsonify({'error': f'Erreur lors de l\'appel de {module_name}.{function_name}'}), 500
        
        return jsonify({'result': result})

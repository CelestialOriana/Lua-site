from flask import Flask, render_template, jsonify
import os
from dotenv import load_dotenv
from lupa import LuaRuntime
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

# Initialiser l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')

# Créer une instance du moteur Lua
lua = LuaRuntime(unpack_returned_tuples=True)

# Charger les fichiers Lua
try:
    lua.execute('dofile("lua/app.lua")')
    logger.info("Fichiers Lua chargés avec succès")
except Exception as e:
    logger.error(f"Erreur lors du chargement des fichiers Lua: {e}")

@app.route("/")
def index():
    try:
        welcome_message = lua.globals().get_welcome_message()
        return render_template('index.html', message=welcome_message)
    except Exception as e:
        logger.error(f"Erreur sur la page d'accueil: {e}")
        return render_template('error.html', error="Une erreur est survenue")

@app.route("/dashboard")
def dashboard():
    try:
        materials = lua.globals().get_materials()
        total_materials = lua.globals().get_total_materials()
        return render_template('dashboard.html', 
                              materials=materials, 
                              total_materials=total_materials)
    except Exception as e:
        logger.error(f"Erreur sur le dashboard: {e}")
        return render_template('error.html', error="Une erreur est survenue")

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/stage")
def stage():
    return render_template('stage.html')

@app.route("/api/materials")
def api_materials():
    try:
        materials = lua.globals().get_materials()
        return jsonify(materials)
    except Exception as e:
        logger.error(f"Erreur API matériels: {e}")
        return jsonify({"error": "Une erreur est survenue"}), 500

# Gestion des erreurs
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="Page non trouvée"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error="Erreur serveur"), 500

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

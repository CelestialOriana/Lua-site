# test_notifications.py
# Script pour tester le système de notifications Lua

from flask import Flask, jsonify
import json
import logging
import traceback
import sys

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Créer une application Flask minimale
app = Flask(__name__)

# Importer l'intégration Lua
from lua_integration import init_lua, LuaIntegration

# Initialiser l'intégration Lua
lua_integration = init_lua(app, skip_routes=True)

def test_add_notification():
    """Teste l'ajout de notifications pour plusieurs utilisateurs."""
    print("\n=== Test: Ajout de notifications ===")
    
    user_ids = ["user1", "user2", "admin"]
    notification_types = ["info", "warning", "error", "success"]
    messages = [
        "Nouvelle mise à jour disponible",
        "Stock faible pour ThinkPad X1",
        "Erreur lors de l'allocation du matériel",
        "Matériel alloué avec succès"
    ]
    
    notification_ids = []
    
    # Ajouter différentes notifications pour différents utilisateurs
    for i, user_id in enumerate(user_ids):
        notification_type = notification_types[i % len(notification_types)]
        message = messages[i % len(messages)]
        metadata = {"source": "test_script", "priority": i + 1}
        
        try:
            notification_id = lua_integration.call_lua_function(
                'notification_system', 
                'add_notification', 
                user_id, 
                notification_type, 
                message, 
                metadata
            )
            
            if notification_id:
                print(f"✅ Notification ajoutée: ID={notification_id}, User={user_id}, Type={notification_type}")
                notification_ids.append(notification_id)
            else:
                print(f"❌ Échec de l'ajout de notification pour {user_id}")
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout de notification: {str(e)}")
            traceback.print_exc()
    
    return notification_ids

def test_get_notifications(user_id="user1", include_read=False):
    """Teste la récupération des notifications pour un utilisateur."""
    print(f"\n=== Test: Récupération des notifications pour {user_id} ===")
    
    try:
        notifications = lua_integration.call_lua_function(
            'notification_system', 
            'get_notifications', 
            user_id, 
            include_read
        )
        
        if notifications:
            print(f"✅ {len(notifications)} notification(s) trouvée(s) pour {user_id}")
            for notif in notifications:
                print(f"  - ID: {notif.get('id')}, Type: {notif.get('type')}, Message: {notif.get('message')}")
                print(f"    Métadonnées: {notif.get('metadata')}")
                print(f"    Lu: {notif.get('read')}")
        else:
            print(f"ℹ️ Aucune notification trouvée pour {user_id}")
        
        return notifications
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des notifications: {str(e)}")
        traceback.print_exc()
        return None

def test_mark_as_read(notification_id):
    """Teste le marquage d'une notification comme lue."""
    print(f"\n=== Test: Marquage de la notification {notification_id} comme lue ===")
    
    try:
        success = lua_integration.call_lua_function(
            'notification_system', 
            'mark_as_read', 
            notification_id
        )
        
        if success:
            print(f"✅ Notification {notification_id} marquée comme lue")
        else:
            print(f"❌ Échec du marquage de la notification {notification_id}")
        
        return success
    except Exception as e:
        print(f"❌ Erreur lors du marquage de la notification: {str(e)}")
        traceback.print_exc()
        return False

def test_mark_all_as_read(user_id="user1"):
    """Teste le marquage de toutes les notifications d'un utilisateur comme lues."""
    print(f"\n=== Test: Marquage de toutes les notifications de {user_id} comme lues ===")
    
    try:
        success, count = lua_integration.call_lua_function(
            'notification_system', 
            'mark_all_as_read', 
            user_id
        )
        
        if success:
            print(f"✅ {count} notification(s) marquée(s) comme lue(s) pour {user_id}")
        else:
            print(f"❌ Échec du marquage des notifications pour {user_id}")
        
        return success, count
    except Exception as e:
        print(f"❌ Erreur lors du marquage des notifications: {str(e)}")
        traceback.print_exc()
        return False, 0

def test_delete_notification(notification_id):
    """Teste la suppression d'une notification."""
    print(f"\n=== Test: Suppression de la notification {notification_id} ===")
    
    try:
        success = lua_integration.call_lua_function(
            'notification_system', 
            'delete_notification', 
            notification_id
        )
        
        if success:
            print(f"✅ Notification {notification_id} supprimée")
        else:
            print(f"❌ Échec de la suppression de la notification {notification_id}")
        
        return success
    except Exception as e:
        print(f"❌ Erreur lors de la suppression de la notification: {str(e)}")
        traceback.print_exc()
        return False

def test_broadcast_notification():
    """Teste la diffusion d'une notification à tous les utilisateurs."""
    print("\n=== Test: Diffusion d'une notification système ===")
    
    try:
        message = "Maintenance système prévue demain à 18h00"
        metadata = {"maintenance_id": "MAINT-2025-05-21", "duration": "2h"}
        
        notification_ids = lua_integration.call_lua_function(
            'notification_system', 
            'broadcast', 
            message, 
            metadata
        )
        
        if notification_ids:
            print(f"✅ Notification diffusée à {len(notification_ids)} utilisateur(s)")
            print(f"  IDs: {notification_ids}")
        else:
            print("❌ Échec de la diffusion de la notification")
        
        return notification_ids
    except Exception as e:
        print(f"❌ Erreur lors de la diffusion de la notification: {str(e)}")
        traceback.print_exc()
        return []

def test_notification_types():
    """Teste la récupération des types de notifications disponibles."""
    print("\n=== Test: Types de notifications disponibles ===")
    
    try:
        types = lua_integration.call_lua_function(
            'notification_system', 
            'get_notification_types'
        )
        
        if types:
            print("✅ Types de notifications récupérés")
            for key, value in types.items():
                print(f"  - {key}: {value}")
        else:
            print("❌ Échec de la récupération des types de notifications")
        
        return types
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des types de notifications: {str(e)}")
        traceback.print_exc()
        return None

def run_all_tests():
    """Exécute tous les tests de notification."""
    print("\n🔍 DÉBUT DES TESTS DU SYSTÈME DE NOTIFICATIONS")
    
    # Test des types de notifications
    test_notification_types()
    
    # Ajouter des notifications
    notification_ids = test_add_notification()
    
    if notification_ids:
        # Récupérer les notifications pour user1
        test_get_notifications("user1")
        
        # Marquer une notification comme lue
        if len(notification_ids) > 0:
            test_mark_as_read(notification_ids[0])
        
        # Récupérer les notifications incluant les lues
        test_get_notifications("user1", True)
        
        # Marquer toutes les notifications comme lues
        test_mark_all_as_read("user2")
        
        # Supprimer une notification
        if len(notification_ids) > 1:
            test_delete_notification(notification_ids[1])
    
    # Diffuser une notification
    test_broadcast_notification()
    
    # Vérifier les notifications pour tous les utilisateurs après diffusion
    for user_id in ["user1", "user2", "admin"]:
        test_get_notifications(user_id)
    
    print("\n✅ FIN DES TESTS DU SYSTÈME DE NOTIFICATIONS")

def main():
    """Fonction principale pour exécuter les tests."""
    # Vérifier si l'intégration Lua est correctement initialisée
    if not lua_integration:
        print("❌ Échec de l'initialisation de l'intégration Lua")
        return 1
    
    # Vérifier si le module notification_system est chargé
    if 'notification_system' not in lua_integration.modules:
        print("❌ Module notification_system non chargé")
        return 1
    
    # Exécuter tous les tests
    run_all_tests()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

-- lua/notification_system.lua

local NotificationSystem = {}

-- Table pour stocker les notifications
local pending_notifications = {}

-- ID des notifications
local next_notification_id = 1

-- Types de notifications prédéfinis
local notification_types = {
    INFO = "info",
    WARNING = "warning",
    ERROR = "error",
    SUCCESS = "success",
    SYSTEM = "system"
}

-- Table pour les abonnements aux notifications
local subscribers = {}

-- Ajouter une notification
function NotificationSystem:add_notification(user_id, notification_type, message, metadata)
    if not user_id or not message then
        return nil, "L'ID utilisateur et le message sont requis"
    end
    
    -- Valider le type de notification
    local valid_type = false
    for _, type_value in pairs(notification_types) do
        if notification_type == type_value then
            valid_type = true
            break
        end
    end
    
    if not valid_type then
        notification_type = notification_types.INFO
    end
    
    -- Créer la notification
    local notification = {
        id = next_notification_id,
        user_id = user_id,
        type = notification_type,
        message = message,
        metadata = metadata or {},
        created_at = os.time(),
        read = false
    }
    
    next_notification_id = next_notification_id + 1
    
    -- Ajouter à la liste des notifications en attente
    table.insert(pending_notifications, notification)
    
    -- Notifier les abonnés
    self:_notify_subscribers(notification)
    
    return notification.id
end

-- Obtenir toutes les notifications pour un utilisateur
function NotificationSystem:get_notifications(user_id, include_read)
    include_read = include_read or false
    
    if not user_id then
        return nil, "L'ID utilisateur est requis"
    end
    
    local user_notifications = {}
    for _, notification in ipairs(pending_notifications) do
        if notification.user_id == user_id and (include_read or not notification.read) then
            table.insert(user_notifications, notification)
        end
    end
    
    -- Trier par date de création (du plus récent au plus ancien)
    table.sort(user_notifications, function(a, b) return a.created_at > b.created_at end)
    
    return user_notifications
end

-- Marquer une notification comme lue
function NotificationSystem:mark_as_read(notification_id)
    for i, notification in ipairs(pending_notifications) do
        if notification.id == notification_id then
            pending_notifications[i].read = true
            return true
        end
    end
    
    return false, "Notification non trouvée"
end

-- Marquer toutes les notifications d'un utilisateur comme lues
function NotificationSystem:mark_all_as_read(user_id)
    if not user_id then
        return false, "L'ID utilisateur est requis"
    end
    
    local count = 0
    for i, notification in ipairs(pending_notifications) do
        if notification.user_id == user_id and not notification.read then
            pending_notifications[i].read = true
            count = count + 1
        end
    end
    
    return true, count
end

-- Supprimer une notification
function NotificationSystem:delete_notification(notification_id)
    for i, notification in ipairs(pending_notifications) do
        if notification.id == notification_id then
            table.remove(pending_notifications, i)
            return true
        end
    end
    
    return false, "Notification non trouvée"
end

-- Supprimer toutes les notifications d'un utilisateur
function NotificationSystem:delete_all_notifications(user_id, include_read)
    include_read = include_read or true
    
    if not user_id then
        return false, "L'ID utilisateur est requis"
    end
    
    local count = 0
    for i = #pending_notifications, 1, -1 do
        local notification = pending_notifications[i]
        if notification.user_id == user_id and (include_read or notification.read) then
            table.remove(pending_notifications, i)
            count = count + 1
        end
    end
    
    return true, count
end

-- S'abonner aux notifications
function NotificationSystem:subscribe(callback)
    if type(callback) ~= "function" then
        return false, "Le callback doit être une fonction"
    end
    
    table.insert(subscribers, callback)
    return #subscribers
end

-- Se désabonner des notifications
function NotificationSystem:unsubscribe(subscriber_id)
    if subscribers[subscriber_id] then
        subscribers[subscriber_id] = nil
        return true
    end
    
    return false, "Abonné non trouvé"
end

-- Notifier les abonnés (fonction interne)
function NotificationSystem:_notify_subscribers(notification)
    for _, callback in pairs(subscribers) do
        local success, err = pcall(callback, notification)
        if not success then
            -- Dans une implémentation réelle, on pourrait logger l'erreur
            print("Erreur lors de la notification d'un abonné: " .. (err or "erreur inconnue"))
        end
    end
end

-- Obtenir les types de notifications disponibles
function NotificationSystem:get_notification_types()
    return notification_types
end

-- Créer une notification de système (pour tous les utilisateurs)
function NotificationSystem:broadcast(message, metadata)
    local broadcast_ids = {}
    
    -- Simuler une liste d'utilisateurs (dans une implémentation réelle, on récupérerait les utilisateurs de la base de données)
    local users = {"user1", "user2", "user3", "admin"}
    
    for _, user_id in ipairs(users) do
        local notification_id = self:add_notification(user_id, notification_types.SYSTEM, message, metadata)
        table.insert(broadcast_ids, notification_id)
    end
    
    return broadcast_ids
end

return NotificationSystem
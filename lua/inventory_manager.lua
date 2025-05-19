-- lua/inventory_manager.lua

local InventoryManager = {}

-- Données simulées pour les transactions
local transactions = {}

-- Vérifier la disponibilité d'un matériel
function InventoryManager:check_availability(material_id)
    -- Note: Dans une implémentation réelle, ceci interrogerait votre base de données
    -- Pour l'instant, utilisons des données statiques similaires à celles dans app.lua
    
    local materials = {
        [1] = {available = 5, total = 10},
        [2] = {available = 3, total = 8},
        [3] = {available = 7, total = 15},
        [4] = {available = 2, total = 6},
        [5] = {available = 4, total = 10},
        [6] = {available = 6, total = 12}
    }
    
    local material = materials[material_id]
    if material then
        return material.available
    else
        return 0
    end
end

-- Allouer un matériel à un utilisateur
function InventoryManager:allocate_material(material_id, user_id, quantity)
    -- Vérifier que les paramètres sont valides
    if not material_id or not user_id then
        return false, "Identifiants de matériel et d'utilisateur requis"
    end
    
    quantity = quantity or 1
    
    -- Vérifier que la quantité est valide
    if quantity <= 0 then
        return false, "La quantité doit être positive"
    end
    
    -- Vérifier la disponibilité
    local available = self:check_availability(material_id)
    if available < quantity then
        return false, "Stock insuffisant"
    end
    
    -- Générer un ID de transaction unique
    local transaction_id = os.time() .. "-" .. material_id .. "-" .. user_id
    
    -- Enregistrer la transaction
    self:record_transaction(transaction_id, material_id, user_id, quantity)
    
    -- Dans une implémentation réelle, mise à jour de la base de données ici
    -- Pour la simulation, nous supposons simplement que la transaction a réussi
    
    return true, transaction_id
end

-- Enregistrer une transaction
function InventoryManager:record_transaction(transaction_id, material_id, user_id, quantity)
    local transaction = {
        id = transaction_id,
        material_id = material_id,
        user_id = user_id,
        quantity = quantity,
        timestamp = os.time(),
        status = "completed"
    }
    
    table.insert(transactions, transaction)
    return transaction
end

-- Obtenir l'historique des transactions pour un utilisateur
function InventoryManager:get_user_transactions(user_id)
    local user_transactions = {}
    
    for _, transaction in ipairs(transactions) do
        if transaction.user_id == user_id then
            table.insert(user_transactions, transaction)
        end
    end
    
    return user_transactions
end

-- Obtenir l'historique des transactions pour un matériel
function InventoryManager:get_material_transactions(material_id)
    local material_transactions = {}
    
    for _, transaction in ipairs(transactions) do
        if transaction.material_id == material_id then
            table.insert(material_transactions, transaction)
        end
    end
    
    return material_transactions
end

-- Retourner un matériel
function InventoryManager:return_material(transaction_id)
    for i, transaction in ipairs(transactions) do
        if transaction.id == transaction_id and transaction.status == "completed" then
            -- Marquer la transaction comme retournée
            transactions[i].status = "returned"
            transactions[i].return_timestamp = os.time()
            
            -- Dans une implémentation réelle, mise à jour du stock disponible
            
            return true, "Matériel retourné avec succès"
        end
    end
    
    return false, "Transaction non trouvée ou déjà retournée"
end

return InventoryManager
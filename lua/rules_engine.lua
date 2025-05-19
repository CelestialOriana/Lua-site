-- lua/rules_engine.lua

local RulesEngine = {}

-- Tableau de règles pour différentes opérations
local rules = {
    -- Règles pour l'allocation de matériel
    material_allocation = {
        { 
            name = "limit_per_user",
            condition = function(ctx) 
                return ctx.user_allocation_count < 5 
            end,
            message = "Un utilisateur ne peut pas avoir plus de 5 allocations actives"
        },
        {
            name = "admin_bypass",
            condition = function(ctx)
                return ctx.user_role == "admin"
            end,
            -- Les admins peuvent bypasser toutes les règles
            bypass_all = true
        },
        {
            name = "quantity_limit",
            condition = function(ctx)
                return ctx.quantity <= 3
            end,
            message = "Les utilisateurs standard ne peuvent pas allouer plus de 3 unités à la fois"
        }
    },
    
    -- Règles pour les retours de matériel
    material_return = {
        {
            name = "return_period",
            condition = function(ctx)
                local current_time = os.time()
                local max_loan_period = 30 * 24 * 60 * 60 -- 30 jours en secondes
                return (current_time - ctx.allocation_time) <= max_loan_period
            end,
            message = "Le matériel a été prêté depuis plus de 30 jours, une validation supplémentaire est requise"
        }
    },
    
    -- Règles pour l'ajout de nouveaux matériels
    material_addition = {
        {
            name = "manager_approval",
            condition = function(ctx)
                return ctx.user_role == "manager" or ctx.user_role == "admin"
            end,
            message = "Seuls les managers et les administrateurs peuvent ajouter du matériel"
        },
        {
            name = "valid_quantity",
            condition = function(ctx)
                return ctx.quantity > 0
            end,
            message = "La quantité doit être supérieure à zéro"
        }
    }
}

-- Fonction principale pour valider les règles
function RulesEngine:validate(operation, context)
    local operation_rules = rules[operation]
    if not operation_rules then
        return true, nil -- Pas de règles pour cette opération
    end
    
    -- Chercher si un bypass existe
    for _, rule in ipairs(operation_rules) do
        if rule.bypass_all and rule.condition(context) then
            return true, nil -- Bypass toutes les règles
        end
    end
    
    -- Vérifier toutes les règles
    for _, rule in ipairs(operation_rules) do
        if not rule.bypass_all and not rule.condition(context) then
            return false, rule.message
        end
    end
    
    return true, nil
end

-- Ajouter une règle personnalisée
function RulesEngine:add_rule(operation, rule)
    if not rules[operation] then
        rules[operation] = {}
    end
    
    table.insert(rules[operation], rule)
end

-- Supprimer une règle
function RulesEngine:remove_rule(operation, rule_name)
    if not rules[operation] then
        return false
    end
    
    for i, rule in ipairs(rules[operation]) do
        if rule.name == rule_name then
            table.remove(rules[operation], i)
            return true
        end
    end
    
    return false
end

-- Liste toutes les règles pour une opération
function RulesEngine:list_rules(operation)
    if not rules[operation] then
        return {}
    end
    
    local rule_names = {}
    for _, rule in ipairs(rules[operation]) do
        table.insert(rule_names, rule.name)
    end
    
    return rule_names
end

return RulesEngine
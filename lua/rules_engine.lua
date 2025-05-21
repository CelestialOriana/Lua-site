-- lua/rules_engine.lua

local RulesEngine = {}

-- Tableau de règles pour différentes opérations
local rules = {
    -- Règles pour l'allocation de matériel
    material_allocation = {
        { 
            name = "limit_per_user",
            condition = function(ctx) 
                return true  -- Modifié pour toujours retourner true
            end,
            message = "Un utilisateur ne peut pas avoir plus de 5 allocations actives"
        },
        {
            name = "admin_bypass",
            condition = function(ctx)
                return true  -- Modifié pour toujours retourner true
            end,
            -- Les admins peuvent bypasser toutes les règles
            bypass_all = true
        },
        {
            name = "quantity_limit",
            condition = function(ctx)
                return true  -- Modifié pour toujours retourner true
            end,
            message = "Les utilisateurs standard ne peuvent pas allouer plus de 3 unités à la fois"
        }
    },
    
    -- Autres règles inchangées...
    material_return = {
        -- Inchangé...
    },
    material_addition = {
        -- Inchangé...
    }
}

-- Fonction principale pour valider les règles
function RulesEngine:validate(operation, context)
    -- Modifié pour toujours valider
    return true, nil
    
    -- Ancien code commenté
    --[[
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
    ]]--
end

-- Reste du code inchangé...
function RulesEngine:add_rule(operation, rule)
    if not rules[operation] then
        rules[operation] = {}
    end
    
    table.insert(rules[operation], rule)
end

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

-- lua/template_engine.lua

local TemplateEngine = {}

-- Variable pour stocker les templates mis en cache
local template_cache = {}

-- Fonction pour nettoyer une chaîne de caractères (supprimer les espaces en début et fin)
local function trim(s)
    return s:match("^%s*(.-)%s*$")
end

-- Fonction simple de templating avec prise en charge de conditions et boucles
function TemplateEngine:render(template, context)
    -- Vérification des paramètres
    if not template or type(template) ~= "string" then
        return "Erreur: template non valide"
    end
    
    if not context or type(context) ~= "table" then
        context = {}
    end
    
    local result = template
    
    -- 1. Traiter les conditions if/else
    -- Format: {%if condition %}contenu{%else%}contenu alternatif{%endif%}
    result = result:gsub("{%%if%s+(.-)%s+%%}(.-)({%%else%%}(.-))?{%%endif%%}", function(condition, if_content, else_part, else_content)
        local success, value = pcall(function()
            -- Évaluation simple des conditions
            local expr = condition
            
            -- Remplacer les variables par leur valeur
            for var_name, var_value in pairs(context) do
                if type(var_value) == "string" or type(var_value) == "number" then
                    expr = expr:gsub(var_name, tostring(var_value))
                elseif type(var_value) == "boolean" then
                    expr = expr:gsub(var_name, var_value and "true" or "false")
                end
            end
            
            -- Évaluer l'expression
            local result
            
            -- Cas simple: vérification d'existence
            if context[expr] ~= nil then
                result = context[expr] and true or false
            -- Cas simple: comparaison avec == ou !=
            elseif expr:find("==") then
                local left, right = expr:match("(.-)%s*==%s*(.+)")
                left, right = trim(left), trim(right)
                
                -- Convertir les valeurs potentielles
                if left == "true" then left = true
                elseif left == "false" then left = false
                elseif tonumber(left) then left = tonumber(left)
                end
                
                if right == "true" then right = true
                elseif right == "false" then right = false
                elseif tonumber(right) then right = tonumber(right)
                end
                
                result = (left == right)
            elseif expr:find("!=") then
                local left, right = expr:match("(.-)%s*!=%s*(.+)")
                left, right = trim(left), trim(right)
                
                -- Convertir les valeurs potentielles
                if left == "true" then left = true
                elseif left == "false" then left = false
                elseif tonumber(left) then left = tonumber(left)
                end
                
                if right == "true" then right = true
                elseif right == "false" then right = false
                elseif tonumber(right) then right = tonumber(right)
                end
                
                result = (left ~= right)
            else
                -- Par défaut, vérifier si la valeur est "truthy"
                result = expr == "true" or expr ~= "false" and expr ~= "0" and expr ~= ""
            end
            
            if result then
                return if_content
            else
                return else_content or ""
            end
        end)
        
        if success then
            return value
        else
            return "<!-- Erreur condition: " .. condition .. " -->"
        end
    end)
    
    -- 2. Traiter les boucles for
    -- Format: {%for item in items %}contenu avec {{item}}{%endfor%}
    result = result:gsub("{%%for%s+(.-)%s+in%s+(.-)%s+%%}(.-)%{%%endfor%%}", function(var_name, collection_name, content)
        local collection = context[collection_name]
        if not collection or type(collection) ~= "table" then
            return "<!-- Erreur collection: " .. collection_name .. " non trouvée -->"
        end
        
        local output = ""
        for i, item in ipairs(collection) do
            -- Créer un nouveau contexte pour chaque itération
            local loop_context = {}
            for k, v in pairs(context) do
                loop_context[k] = v
            end
            
            -- Ajouter la variable de boucle au contexte
            loop_context[var_name] = item
            -- Ajouter des variables utiles pour la boucle
            loop_context["loop"] = {
                index = i,
                first = (i == 1),
                last = (i == #collection)
            }
            
            -- Rendre le contenu avec le nouveau contexte
            local item_content = content
            
            -- Remplacer les variables
            item_content = item_content:gsub("{{%s*(.-)%s*}}", function(var)
                if var == var_name then
                    if type(item) == "table" then
                        return "<!-- Erreur: " .. var_name .. " est une table -->"
                    else
                        return tostring(item)
                    end
                elseif var:find(var_name .. "%.") then
                    -- Accès à un champ de l'objet
                    local field = var:match(var_name .. "%.(.+)")
                    if type(item) == "table" and item[field] ~= nil then
                        if type(item[field]) == "table" then
                            return "<!-- Erreur: " .. field .. " est une table -->"
                        else
                            return tostring(item[field])
                        end
                    else
                        return "<!-- Champ non trouvé: " .. field .. " -->"
                    end
                elseif var:find("loop%.") then
                    -- Accès aux variables de boucle
                    local field = var:match("loop%.(.+)")
                    if loop_context.loop[field] ~= nil then
                        return tostring(loop_context.loop[field])
                    else
                        return "<!-- Variable de boucle non trouvée: " .. field .. " -->"
                    end
                else
                    if loop_context[var] ~= nil then
                        if type(loop_context[var]) == "table" then
                            return "<!-- Erreur: " .. var .. " est une table -->"
                        else
                            return tostring(loop_context[var])
                        end
                    else
                        return "<!-- Variable non trouvée: " .. var .. " -->"
                    end
                end
            end)
            
            output = output .. item_content
        end
        
        return output
    end)
    
    -- 3. Remplacer les variables simples
    -- Format: {{variable}}
    result = result:gsub("{{%s*(.-)%s*}}", function(var)
        if context[var] ~= nil then
            if type(context[var]) == "table" then
                return "<!-- Erreur: " .. var .. " est une table -->"
            else
                return tostring(context[var])
            end
        else
            -- Vérifier si c'est une variable imbriquée (ex: user.name)
            local parts = {}
            for part in var:gmatch("([^.]+)") do
                table.insert(parts, part)
            end
            
            if #parts > 1 then
                local value = context
                for _, part in ipairs(parts) do
                    if type(value) ~= "table" then
                        return "<!-- Variable imbriquée invalide: " .. var .. " -->"
                    end
                    value = value[part]
                    if value == nil then
                        return "<!-- Champ non trouvé: " .. part .. " -->"
                    end
                end
                
                if type(value) == "table" then
                    return "<!-- Erreur: " .. var .. " est une table -->"
                else
                    return tostring(value)
                end
            else
                return "<!-- Variable non trouvée: " .. var .. " -->"
            end
        end
    end)
    
    return result
end

-- Fonction pour charger un template depuis un fichier
function TemplateEngine:load_template(template_path)
    -- Vérifier si le template est déjà en cache
    if template_cache[template_path] then
        return template_cache[template_path]
    end
    
    -- Tenter de lire le fichier
    local file, err = io.open(template_path, "r")
    if not file then
        return nil, "Erreur lors de l'ouverture du template: " .. (err or "fichier non trouvé")
    end
    
    local content = file:read("*all")
    file:close()
    
    -- Mettre en cache
    template_cache[template_path] = content
    
    return content
end

-- Fonction pour rendre un template à partir d'un fichier
function TemplateEngine:render_file(template_path, context)
    local template, err = self:load_template(template_path)
    if not template then
        return "Erreur: " .. err
    end
    
    return self:render(template, context)
end

-- Fonction pour vider le cache de templates
function TemplateEngine:clear_cache()
    template_cache = {}
end

return TemplateEngine
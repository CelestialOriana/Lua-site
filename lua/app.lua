-- lua/app.lua

-- Charger les modules
package.path = package.path .. ";./lua/?.lua"
local HomeController = {}
local Material = {}

-- Fonction pour s'assurer que les modules sont chargés correctement
local function loadModule(name)
    local status, module = pcall(function() return require(name) end)
    if status then
        return module
    else
        print("Erreur lors du chargement du module " .. name .. ": " .. module)
        return {}
    end
end

-- Tenter de charger les modules
local success, controller = pcall(function() return loadModule("home_controller") end)
if success then
    HomeController = controller
end

local success, materialModule = pcall(function() return loadModule("material") end)
if success then
    Material = materialModule
end

-- Simulation d'une base de données pour les matériels avec URLs d'images
local materials = {
    {id = 1, name = "ThinkCentre Gen 2", type = "desktop", available = 5, total = 10, description = "Ordinateur de bureau ThinkCentre Gen 2", image_path = "https://placehold.co/400x300?text=ThinkCentre+Gen+2"},
    {id = 2, name = "ThinkCentre Gen 3", type = "desktop", available = 3, total = 8, description = "Ordinateur de bureau ThinkCentre Gen 3", image_path = "https://placehold.co/400x300?text=ThinkCentre+Gen+3"},
    {id = 3, name = "ThinkCentre Gen 4", type = "desktop", available = 7, total = 15, description = "Ordinateur de bureau ThinkCentre Gen 4", image_path = "https://placehold.co/400x300?text=ThinkCentre+Gen+4"},
    {id = 4, name = "ThinkCentre Gen 5", type = "desktop", available = 2, total = 6, description = "Ordinateur de bureau ThinkCentre Gen 5", image_path = "https://placehold.co/400x300?text=ThinkCentre+Gen+5"},
    {id = 5, name = "ThinkPad X1", type = "laptop", available = 4, total = 10, description = "Ordinateur portable ThinkPad X1", image_path = "https://placehold.co/400x300?text=ThinkPad+X1"},
    {id = 6, name = "ThinkPad T14", type = "laptop", available = 6, total = 12, description = "Ordinateur portable ThinkPad T14", image_path = "https://placehold.co/400x300?text=ThinkPad+T14"}
}

-- Fonction qui retourne les matériels disponibles
function get_materials()
    return materials
end

-- Fonction qui retourne le nombre total de matériels
function get_total_materials()
    local total = 0
    for _, material in ipairs(materials) do
        total = total + material.total
    end
    return total
end

-- Fonction pour obtenir le message d'accueil depuis le contrôleur
function get_welcome_message()
    local msg = "Bienvenue dans le Système de Gestion de Matériel"
    if HomeController.index then
        local success, result = pcall(function() return HomeController:index() end)
        if success then
            msg = result
        end
    end
    return msg
end

-- Fonction pour obtenir un matériel par son ID
function get_material_by_id(id)
    for _, material in ipairs(materials) do
        if material.id == id then
            return material
        end
    end
    return nil
end

-- Fonction pour filtrer les matériels par type
function filter_materials_by_type(material_type)
    local filtered = {}
    for _, material in ipairs(materials) do
        if material.type == material_type then
            table.insert(filtered, material)
        end
    end
    return filtered
end

-- Exporter toutes les fonctions
return {
    get_materials = get_materials,
    get_total_materials = get_total_materials,
    get_welcome_message = get_welcome_message,
    get_material_by_id = get_material_by_id,
    filter_materials_by_type = filter_materials_by_type
}

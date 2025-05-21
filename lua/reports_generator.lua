-- lua/reports_generator.lua

local ReportsGenerator = {}

-- Simuler des données d'utilisation
local function simulate_usage_data(start_date, end_date)
    -- Dans une implémentation réelle, ces données viendraient d'une base de données
    -- Pour cette simulation, nous générons des données aléatoires
    
    -- Convertir les dates en timestamps (format simple pour la simulation)
    local function date_to_timestamp(date_str)
        local year, month, day = date_str:match("(%d+)-(%d+)-(%d+)")
        return os.time({year=year, month=month, day=day})
    end
    
    local start_ts = date_to_timestamp(start_date)
    local end_ts = date_to_timestamp(end_date)
    
    -- Générer des données d'utilisation aléatoires
    local usage_data = {
        desktops = {
            allocations = math.random(10, 50),
            returns = math.random(5, 40),
            most_used = "ThinkCentre Gen 4",
            least_used = "ThinkCentre Gen 5"
        },
        laptops = {
            allocations = math.random(20, 60),
            returns = math.random(15, 50),
            most_used = "ThinkPad X1",
            least_used = "ThinkPad T14"
        }
    }
    
    -- Calculer les totaux
    local total_allocations = usage_data.desktops.allocations + usage_data.laptops.allocations
    local total_returns = usage_data.desktops.returns + usage_data.laptops.returns
    
    return {
        period = {
            start = start_date,
            ["end"] = end_date, -- "end" est un mot-clé réservé en Lua, il doit être entre crochets
            days = math.floor((end_ts - start_ts) / (24 * 60 * 60))
        },
        totals = {
            allocations = total_allocations,
            returns = total_returns,
            active = total_allocations - total_returns
        },
        by_type = usage_data
    }
end

-- Générer un rapport d'utilisation du matériel
function ReportsGenerator:generate_material_usage_report(start_date, end_date, material_id)
    local usage_data = simulate_usage_data(start_date, end_date)
    
    -- Filtrer les données si un material_id est spécifié
    if material_id then
        print("Génération du rapport pour material_id: " .. material_id)
        -- Ajouter la logique pour filtrer les données selon material_id
    end
    
    local report = {
        title = "Rapport d'utilisation du matériel",
        period = start_date .. " au " .. end_date,
        date_generated = os.date("%Y-%m-%d %H:%M:%S"),
        summary = {
            total_days = usage_data.period.days,
            total_allocations = usage_data.totals.allocations,
            total_returns = usage_data.totals.returns,
            active_allocations = usage_data.totals.active,
            most_allocated = usage_data.by_type.laptops.allocations > usage_data.by_type.desktops.allocations 
                             and usage_data.by_type.laptops.most_used 
                             or usage_data.by_type.desktops.most_used
        },
        details = {
            {
                type = "desktop", 
                allocations = usage_data.by_type.desktops.allocations,
                returns = usage_data.by_type.desktops.returns,
                percentage = math.floor((usage_data.by_type.desktops.allocations / usage_data.totals.allocations) * 100),
                most_used = usage_data.by_type.desktops.most_used,
                least_used = usage_data.by_type.desktops.least_used
            },
            {
                type = "laptop", 
                allocations = usage_data.by_type.laptops.allocations,
                returns = usage_data.by_type.laptops.returns,
                percentage = math.floor((usage_data.by_type.laptops.allocations / usage_data.totals.allocations) * 100),
                most_used = usage_data.by_type.laptops.most_used,
                least_used = usage_data.by_type.laptops.least_used
            }
        }
    }
    
    -- Si material_id est défini, ajouter cette information au rapport
    if material_id then
        report.material_id = material_id
        report.title = "Rapport d'utilisation du matériel #" .. material_id
    end
    
    return report
end

-- Générer un rapport de stock
function ReportsGenerator:generate_inventory_report()
    -- Simulation de données d'inventaire
    local inventory_data = {
        total_materials = 61,
        available_materials = 27,
        low_stock_count = 4,
        categories = {
            {name = "desktop", count = 39, available = 17},
            {name = "laptop", count = 22, available = 10}
        },
        low_stock_items = {
            {id = 4, name = "ThinkCentre Gen 5", available = 2, total = 6},
            {id = 2, name = "ThinkCentre Gen 3", available = 3, total = 8}
        }
    }
    
    local report = {
        title = "Rapport d'inventaire",
        date_generated = os.date("%Y-%m-%d %H:%M:%S"),
        summary = {
            total_count = inventory_data.total_materials,
            available_count = inventory_data.available_materials,
            availability_percentage = math.floor((inventory_data.available_materials / inventory_data.total_materials) * 100),
            low_stock_count = inventory_data.low_stock_count
        },
        categories = inventory_data.categories,
        low_stock_items = inventory_data.low_stock_items
    }
    
    return report
end

-- Générer un rapport d'activité par utilisateur
function ReportsGenerator:generate_user_activity_report(user_id, start_date, end_date)
    -- Simulation de données d'activité utilisateur
    local user_data = {
        id = user_id,
        name = "Utilisateur " .. user_id,
        department = "Service informatique",
        activity = {
            allocations = math.random(1, 15),
            returns = math.random(1, 10),
            late_returns = math.random(0, 3),
            current_allocations = math.random(0, 5)
        },
        current_items = {
            {id = 1, name = "ThinkPad X1", allocated_date = "2025-04-15", due_date = "2025-05-15"},
            {id = 3, name = "ThinkCentre Gen 4", allocated_date = "2025-03-20", due_date = "2025-06-20"}
        }
    }
    
    local report = {
        title = "Rapport d'activité utilisateur",
        user = {
            id = user_data.id,
            name = user_data.name,
            department = user_data.department
        },
        period = start_date .. " au " .. end_date,
        date_generated = os.date("%Y-%m-%d %H:%M:%S"),
        activity_summary = user_data.activity,
        current_allocations = user_data.current_items
    }
    
    return report
end

return ReportsGenerator
-- lua/smart_cache.lua

local SmartCache = {}

-- Table pour stocker les entrées du cache
local cache = {}

-- Table pour les statistiques d'utilisation du cache
local stats = {
    hits = 0,
    misses = 0,
    evictions = 0
}

-- Configuration du cache
local config = {
    default_ttl = 3600,  -- 1 heure par défaut (en secondes)
    max_entries = 1000,  -- Nombre maximum d'entrées dans le cache
    cleanup_interval = 300  -- Intervalle de nettoyage (5 minutes)
}

-- Timestamp du dernier nettoyage
local last_cleanup = os.time()

-- Fonction utilitaire pour obtenir la taille approximative d'une valeur
local function get_size(value)
    local value_type = type(value)
    
    if value_type == "string" then
        return #value
    elseif value_type == "table" then
        local size = 0
        for k, v in pairs(value) do
            size = size + get_size(k) + get_size(v)
        end
        return size
    elseif value_type == "number" then
        return 8  -- Approximation pour un nombre
    elseif value_type == "boolean" then
        return 1
    else
        return 4  -- Valeur par défaut pour les autres types
    end
end

-- Fonction pour nettoyer les entrées expirées
local function cleanup()
    local now = os.time()
    local removed = 0
    
    for key, entry in pairs(cache) do
        if entry.expiry <= now then
            cache[key] = nil
            removed = removed + 1
            stats.evictions = stats.evictions + 1
        end
    end
    
    last_cleanup = now
    return removed
end

-- Récupérer une valeur du cache
function SmartCache:get(key)
    -- Vérifier si un nettoyage périodique est nécessaire
    if os.time() - last_cleanup > config.cleanup_interval then
        cleanup()
    end
    
    local entry = cache[key]
    if entry and entry.expiry > os.time() then
        -- Mettre à jour le timestamp de dernier accès
        entry.last_access = os.time()
        stats.hits = stats.hits + 1
        return entry.value
    end
    
    stats.misses = stats.misses + 1
    return nil
end

-- Stocker une valeur dans le cache
function SmartCache:set(key, value, ttl)
    -- Vérifier si on atteint la limite d'entrées
    local count = 0
    for _ in pairs(cache) do
        count = count + 1
    end
    
    -- Si on atteint la limite, supprimer les entrées les moins récemment utilisées
    if count >= config.max_entries then
        -- D'abord nettoyer les entrées expirées
        cleanup()
        
        -- Si on est toujours au-dessus de la limite, supprimer les entrées les moins récemment utilisées
        local entries = {}
        for k, v in pairs(cache) do
            table.insert(entries, {key = k, last_access = v.last_access})
        end
        
        -- Trier par dernier accès (du plus ancien au plus récent)
        table.sort(entries, function(a, b) return a.last_access < b.last_access end)
        
        -- Supprimer jusqu'à 10% des entrées les plus anciennes
        local to_remove = math.ceil(count * 0.1)
        for i = 1, to_remove do
            if entries[i] then
                cache[entries[i].key] = nil
                stats.evictions = stats.evictions + 1
            end
        end
    end
    
    -- Définir le TTL (time to live)
    ttl = ttl or config.default_ttl
    
    -- Stocker l'entrée
    cache[key] = {
        value = value,
        expiry = os.time() + ttl,
        last_access = os.time(),
        size = get_size(value)
    }
    
    return true
end

-- Vérifier si une clé existe dans le cache
function SmartCache:has(key)
    local entry = cache[key]
    return entry ~= nil and entry.expiry > os.time()
end

-- Supprimer une entrée du cache
function SmartCache:delete(key)
    if cache[key] then
        cache[key] = nil
        return true
    else
        return false
    end
end

-- Invalider toutes les entrées qui correspondent à un motif
function SmartCache:invalidate(key_pattern)
    local count = 0
    
    for key, _ in pairs(cache) do
        if key:match(key_pattern) then
            cache[key] = nil
            count = count + 1
        end
    end
    
    return count
end

-- Vider le cache
function SmartCache:clear()
    cache = {}
    return true
end

-- Configurer le cache
function SmartCache:configure(options)
    if options.default_ttl then
        config.default_ttl = options.default_ttl
    end
    
    if options.max_entries then
        config.max_entries = options.max_entries
    end
    
    if options.cleanup_interval then
        config.cleanup_interval = options.cleanup_interval
    end
end

-- Obtenir des statistiques sur l'utilisation du cache
function SmartCache:get_stats()
    local count = 0
    local expired = 0
    local total_size = 0
    local now = os.time()
    
    for _, entry in pairs(cache) do
        count = count + 1
        if entry.expiry <= now then
            expired = expired + 1
        end
        total_size = total_size + (entry.size or 0)
    end
    
    return {
        entries = count,
        expired = expired,
        hits = stats.hits,
        misses = stats.misses,
        evictions = stats.evictions,
        hit_ratio = stats.hits > 0 and stats.hits / (stats.hits + stats.misses) or 0,
        total_size = total_size,
        config = config
    }
end

return SmartCache
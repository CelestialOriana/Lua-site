-- lua/material.lua

local Material = {}

-- Simulation d'une classe Material
function Material:new(data)
    local instance = data or {}
    setmetatable(instance, { __index = self })
    return instance
end

function Material:validate()
    return self.name and self.type and self.total and true or false
end

-- Méthodes pour manipuler les matériels
function Material:get_available_percentage()
    if not self.total or self.total == 0 then
        return 0
    end
    return (self.available / self.total) * 100
end

function Material:is_low_stock()
    return self.available and self.total and (self.available / self.total) < 0.2
end

return Material
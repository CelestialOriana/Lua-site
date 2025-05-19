-- lua/home_controller.lua

local HomeController = {}

function HomeController:index()
    return "Bienvenue dans le Système de Gestion de Matériel"
end

function HomeController:about()
    return {
        title = "À propos",
        content = "Ce système permet de gérer l'inventaire de matériel informatique."
    }
end

return HomeController
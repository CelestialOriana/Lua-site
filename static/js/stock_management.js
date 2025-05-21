// stock_management.js
document.addEventListener('DOMContentLoaded', function() {
    // Vérifier si nous sommes sur la page de gestion des stocks
    if (!document.getElementById('stock-data')) {
        return;
    }

    // Récupérer les données depuis les éléments JSON
    var materialsJson = document.getElementById('stock-data').textContent;
    var apiUrlsJson = document.getElementById('api-urls').textContent;
    
    // Analyser les données
    var materials = JSON.parse(materialsJson);
    var apiUrls = JSON.parse(apiUrlsJson);
    
    // Le reste du code JavaScript pour la gestion des stocks...
});